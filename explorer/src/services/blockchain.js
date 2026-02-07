import { ethers } from "ethers";
import abi from "../abis/PharmaChain.json";
import { getSigner } from './wallet';

const HTTP_URL = process.env.REACT_APP_ALCHEMY_URL;
const WS_URL = process.env.REACT_APP_ALCHEMY_WS_URL || "";
const CONTRACT_ADDRESS = process.env.REACT_APP_CONTRACT_ADDRESS;

const providerOptions = {
  batchMaxCount: 1,
};

// --- ALL THE MISSING EXPORTS ARE HERE ---

export const httpProvider = new ethers.JsonRpcProvider(HTTP_URL, "sepolia", providerOptions);
export const wsProvider = WS_URL ? new ethers.WebSocketProvider(WS_URL, "sepolia") : null;
export const contract = new ethers.Contract(CONTRACT_ADDRESS, abi, httpProvider);

export const liveContract = wsProvider
  ? new ethers.Contract(CONTRACT_ADDRESS, abi, wsProvider)
  : contract;

export async function getSignerContract() {
  const signer = await getSigner();
  return new ethers.Contract(CONTRACT_ADDRESS, abi, signer);
}

export const ROLE = {
  MANUFACTURER: "MANUFACTURER_ROLE",
  REGULATOR: "REGULATOR_ROLE",
  CARRIER: "CARRIER_ROLE",
  PHARMACY: "PHARMACY_ROLE",
  ORACLE: "ORACLE_ROLE",
};

export async function myRoles(addr) {
  const labels = [];
  const id = ethers.id;
  if (!addr) return [];
  try {
    if (await contract.hasRole(id(ROLE.MANUFACTURER), addr)) labels.push("MANUFACTUFACTURER");
    if (await contract.hasRole(id(ROLE.REGULATOR), addr)) labels.push("REGULATOR");
    if (await contract.hasRole(id(ROLE.CARRIER), addr)) labels.push("CARRIER");
    if (await contract.hasRole(id(ROLE.PHARMACY), addr)) labels.push("PHARMACY");
    if (await contract.hasRole(id(ROLE.ORACLE), addr)) labels.push("ORACLE");
  } catch (e) {
    console.error("Error checking roles:", e);
  }
  return labels;
}

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

export async function getLogsChunked({ address, topics, fromBlock, toBlock }) {
  let chunk = 9;
  let from = fromBlock;
  const out = [];

  console.log(`Starting chunked log scan from block ${fromBlock} to ${toBlock}...`);

  while (from <= toBlock) {
    const to = Math.min(from + chunk, toBlock);
    try {
      // Log each attempt to give user feedback
      console.log(`   Querying chunk ${from} to ${to}...`);
      const logs = await httpProvider.getLogs({ address, topics, fromBlock: from, toBlock: to });
      out.push(...logs);
      from = to + 1;
      
      // THIS IS THE CRITICAL FIX: A longer delay to stay under the rate limit.
      await sleep(300); 

    } catch (e) {
      if (chunk > 1 && (e.code === -32600 || e.code === 429)) {
        chunk = Math.max(1, Math.floor(chunk / 2));
        console.warn(`getLogs failed, reducing chunk size to ${chunk} and retrying...`);
        await sleep(500); // Wait even longer after a failure
        continue;
      }
      console.error('getLogsChunked failed irrecoverably at chunk', { from, to }, e);
      throw e;
    }
  }
  console.log("Chunked log scan finished.");
  return out;
}

const keyFor = (id) => ethers.keccak256(ethers.toUtf8Bytes(id));

export async function fetchReadingsFromLogs(shipmentId) {
  try {
    const currentBlock = await httpProvider.getBlockNumber();
    const LOOKBACK = 5000;
    const startBlock = Math.max(currentBlock - LOOKBACK, 0);

    const key = keyFor(shipmentId);
    const tempTopic = contract.interface.getEvent('TemperatureRecorded').topicHash;

    const logs = await getLogsChunked({
      address: contract.target,
      topics: [tempTopic, key],
      fromBlock: startBlock,
      toBlock: currentBlock,
    });

    return logs.map(l => {
      const parsed = contract.interface.parseLog(l);
      return {
        temperature: Number(parsed.args[2]),
        timestamp: Number(parsed.args[3]) * 1000,
        txHash: l.transactionHash,
        blockNumber: l.blockNumber,
      };
    });
  } catch (e) {
    console.error(`Failed to fetch readings for ${shipmentId}`, e);
    return [];
  }
}

export async function fetchLifecycleEvents(shipmentId) {
  try {
    const key = ethers.keccak256(ethers.toUtf8Bytes(shipmentId));
    const currentBlock = await httpProvider.getBlockNumber();
    const LOOKBACK = 10000;
    const startBlock = Math.max(currentBlock - LOOKBACK, 0);

    const createdTopic = contract.interface.getEvent('ShipmentCreated').topicHash;
    const transferTopic = contract.interface.getEvent('CustodyTransferred').topicHash;
    const deliveredTopic = contract.interface.getEvent('Delivered').topicHash;

    const [createdLogs, transferLogs, deliveredLogs] = await Promise.all([
      getLogsChunked({ address: contract.target, topics: [createdTopic, key], fromBlock: startBlock, toBlock: currentBlock }),
      getLogsChunked({ address: contract.target, topics: [transferTopic, key], fromBlock: startBlock, toBlock: currentBlock }),
      getLogsChunked({ address: contract.target, topics: [deliveredTopic, key], fromBlock: startBlock, toBlock: currentBlock })
    ]);

    // This is the new, robust log processing logic
    const allEvents = [];

    // Process Created Events
    for (const log of createdLogs) {
      const block = await httpProvider.getBlock(log.blockNumber);
      allEvents.push({
        type: "CREATED",
        timestamp: block.timestamp * 1000,
        txHash: log.transactionHash,
        blockNumber: log.blockNumber,
      });
    }

    // Process Transfer Events
    for (const log of transferLogs) {
      const block = await httpProvider.getBlock(log.blockNumber);
      allEvents.push({
        type: "TRANSFERRED",
        timestamp: block.timestamp * 1000,
        txHash: log.transactionHash,
        blockNumber: log.blockNumber,
      });
    }
    
    // Process Delivered Events
    for (const log of deliveredLogs) {
      const block = await httpProvider.getBlock(log.blockNumber);
      allEvents.push({
        type: "DELIVERED",
        timestamp: block.timestamp * 1000,
        txHash: log.transactionHash,
        blockNumber: log.blockNumber,
      });
    }

    allEvents.sort((a, b) => a.timestamp - b.timestamp);

    return allEvents;
  } catch (e) {
    console.error(`Failed to fetch lifecycle events for ${shipmentId}`, e);
    return [];
  }
}