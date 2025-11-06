import { ethers } from "ethers";

// Sepolia Chain ID in hexadecimal format
export const SEPOLIA_CHAIN_ID = '0xaa36a7'; // 11155111

/**
 * Checks if the user's MetaMask is on the Sepolia network.
 * If not, it prompts the user to switch.
 */
export async function ensureSepolia() {
  const ethereum = window.ethereum;
  if (!ethereum) {
    alert("MetaMask not found! Please install it to use this feature.");
    throw new Error("MetaMask not found");
  }

  const chainId = await ethereum.request({ method: "eth_chainId" });
  if (chainId !== SEPOLIA_CHAIN_ID) {
    try {
      await ethereum.request({
        method: "wallet_switchEthereumChain",
        params: [{ chainId: SEPOLIA_CHAIN_ID }],
      });
    } catch (switchError) {
      // This error code indicates that the chain has not been added to MetaMask.
      if (switchError.code === 4902) {
        alert("Please add the Sepolia network to your MetaMask and try again.");
      }
      throw switchError;
    }
  }
}

/**
 * Gets a signer instance from the user's MetaMask, ensuring they are on Sepolia.
 * A "signer" is an object that can sign and send transactions.
 */
export async function getSigner() {
  await ensureSepolia(); // First, make sure the network is correct.
  const provider = new ethers.BrowserProvider(window.ethereum);
  const signer = await provider.getSigner();
  return signer;
}