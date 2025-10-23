import type { HardhatUserConfig } from "hardhat/config";
import "dotenv/config";
import hardhatToolboxMochaEthersPlugin from "@nomicfoundation/hardhat-toolbox-mocha-ethers";

const MANUFACTURER_PRIVATE_KEY = process.env.MANUFACTURER_PRIVATE_KEY || "";
const GANACHE_RPC_URL = process.env.GANACHE_RPC_URL || "HTTP://127.0.0.1:7545";

console.log("Config Debug: MANUFACTURER_PRIVATE_KEY status:", MANUFACTURER_PRIVATE_KEY ? "LOADED" : "MISSING/EMPTY");
console.log("Config Debug: GANACHE_RPC_URL:", GANACHE_RPC_URL);

const config: HardhatUserConfig = {
  plugins: [hardhatToolboxMochaEthersPlugin],
  solidity: {
    profiles: {
      default: {
        version: "0.8.28",
        settings: { 
          optimizer: {
            enabled: true,
            runs: 200,
          },
          viaIR: true, 
        },
      },
      production: {
        version: "0.8.28",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
          },
          viaIR: true,
        },
      },
    },
  },
  networks: {
    hardhatMainnet: {
      type: "edr-simulated",
      chainType: "l1",
    },
    hardhatOp: {
      type: "edr-simulated",
      chainType: "op",
    },
    // sepolia: {
    //   type: "http",
    //   chainType: "l1",
    //   url: process.env.SEPOLIA_RPC_URL || "",
    //   accounts: process.env.SEPOLIA_PRIVATE_KEY ? [process.env.SEPOLIA_PRIVATE_KEY] : [],
    // },
    ganache: {
      url: GANACHE_RPC_URL,
      accounts: MANUFACTURER_PRIVATE_KEY ? [`0x${MANUFACTURER_PRIVATE_KEY}`] : [],
      type: "http", 
      chainId: 1337
    },
  },
};

export default config;
