// scripts/deploy.ts

import "dotenv/config";
import { ethers } from "ethers"; // We will use the direct import
import * as fs from 'fs';
import hre from "hardhat"; 

async function main() {
  console.log("Deployment script started (Manual Provider)...");

  // 1. Manually create a provider connected to your Ganache instance.
  const rpcUrl = process.env.GANACHE_RPC_URL || "HTTP://127.0.0.1:7545";
  const provider = new ethers.JsonRpcProvider(rpcUrl);

  // 2. Get the Private Key for the deployer from .env
  const deployerPrivateKey = process.env.MANUFACTURER_PRIVATE_KEY;
  if (!deployerPrivateKey) {
    throw new Error("MANUFACTURER_PRIVATE_KEY not found in .env file");
  }
  // Create a Wallet instance connected to our new provider.
  const deployerWallet = new ethers.Wallet(`0x${deployerPrivateKey}`, provider);
  console.log("Deploying contracts with the account:", deployerWallet.address);

  // 3. Get the Oracle Address
  const iotOracleAddress = process.env.ORACLE_ADDRESS;
  if (!iotOracleAddress || !ethers.isAddress(iotOracleAddress)) {
    console.error("Error: ORACLE_ADDRESS not set or invalid in .env");
    process.exitCode = 1;
    return;
  }

  console.log(`\nAttempting to deploy ColdChain contract with IoT Oracle address: ${iotOracleAddress}`);

  // 4. Get the contract artifact using hre.artifacts
  const ColdChainArtifact = await hre.artifacts.readArtifact("ColdChain");
  
  // 5. Create a ContractFactory instance
  const ColdChainFactory = new ethers.ContractFactory(
    ColdChainArtifact.abi,
    ColdChainArtifact.bytecode,
    deployerWallet // The signer is our manually created wallet
  );

  // 6. Deploy the contract
  const coldChain = await ColdChainFactory.deploy(iotOracleAddress);

  // Wait for deployment
  await coldChain.waitForDeployment();

  console.log(`ColdChain contract deployed to: ${coldChain.target}`);
  console.log(`IoT Oracle set to: ${iotOracleAddress}`);
  
  // 7. Save contract info
  const contractInfo = {
    address: coldChain.target,
    abi: ColdChainArtifact.abi
  };
  fs.writeFileSync('contract-info.json', JSON.stringify(contractInfo, null, 2));
  console.log("Contract address and ABI saved to contract-info.json");
}

// Call the main function
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });