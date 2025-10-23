// src/App.tsx (Final Version with all components)

import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';
import contractInfo from './contract-info.json';
import { ShipmentViewer } from './components/ShipmentViewer';
import { BlockViewer } from './components/BlockViewer';
import { ShipmentManager } from './components/ShipmentManager'; // <-- IMPORT

const CONTRACT_ADDRESS = contractInfo.address;

function App() {
  const [provider, setProvider] = useState<ethers.BrowserProvider | null>(null);
  const [signer, setSigner] = useState<ethers.Signer | null>(null);
  const [account, setAccount] = useState<string | null>(null);
  const [contract, setContract] = useState<ethers.Contract | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [networkName, setNetworkName] = useState<string | null>(null);
  const [chainId, setChainId] = useState<bigint | null>(null);

  useEffect(() => {
    if (window.ethereum) {
      const web3Provider = new ethers.BrowserProvider(window.ethereum);
      setProvider(web3Provider);

      window.ethereum.on('accountsChanged', (accounts: string[]) => {
        if (accounts.length > 0) {
          setAccount(accounts[0]);
          setIsConnected(true);
        } else {
          setAccount(null);
          setIsConnected(false);
        }
      });

      window.ethereum.on('chainChanged', () => {
        window.location.reload();
      });

    } else {
      console.error("MetaMask not detected. Please install the extension.");
    }
  }, []);

  useEffect(() => {
    const setup = async () => {
      if (provider && account) {
        const s = await provider.getSigner();
        setSigner(s);
        const c = new ethers.Contract(CONTRACT_ADDRESS, contractInfo.abi, s);
        setContract(c);
        const network = await provider.getNetwork();
        setNetworkName(network.name);
        setChainId(network.chainId);
      }
    };
    setup();
  }, [provider, account]);

  const connectWallet = async () => {
    if (provider) {
      try {
        const s = await provider.getSigner();
        setSigner(s);
        setAccount(s.address);
        setIsConnected(true);
      } catch (error) {
        console.error("User denied account access or other error:", error);
      }
    } else {
      alert("Please install MetaMask!");
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center p-4 font-sans">
      <h1 className="text-4xl font-bold mb-8 text-blue-400">Pharmaceutical Cold Chain DApp</h1>
      
      <div className="w-full max-w-5xl bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-2xl font-semibold mb-4 text-blue-300">Wallet Connection</h2>
        {!isConnected ? (
          <button
            onClick={connectWallet}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors"
          >
            Connect MetaMask
          </button>
        ) : (
          <div>
            <p className="text-lg">Status: <span className="font-mono text-green-400">Connected</span></p>
            <p className="text-lg">Network: <span className="font-mono text-yellow-400">{networkName} (Chain ID: {chainId?.toString()})</span></p>
            <p className="text-lg">Account: <span className="font-mono text-green-400 break-all">{account}</span></p>
          </div>
        )}
      </div>

      {isConnected && contract && signer && provider && ( // also check for signer
        <div className="w-full max-w-5xl">
          <ShipmentManager contract={contract} signer={signer} /> {/* <-- ADDED */}
          <ShipmentViewer contract={contract} />
          <BlockViewer provider={provider} />
        </div>
      )}
    </div>
  );
}

export default App;