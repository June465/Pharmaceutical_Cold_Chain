// src/components/ShipmentManager.tsx

import React, { useState } from 'react';
import { ethers } from 'ethers';

interface ShipmentManagerProps {
  contract: ethers.Contract;
  signer: ethers.Signer | null;
}

export const ShipmentManager: React.FC<ShipmentManagerProps> = ({ contract, signer }) => {
  // State for creating a new shipment
  const [newShipmentId, setNewShipmentId] = useState('');
  const [productDetails, setProductDetails] = useState('');
  
  // State for transferring custody
  const [transferShipmentId, setTransferShipmentId] = useState('');
  const [newCustodian, setNewCustodian] = useState('');

  // General state for loading and transaction status
  const [loading, setLoading] = useState(false);
  const [txHash, setTxHash] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCreateShipment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!signer || !newShipmentId || !productDetails) {
      alert("Please fill all fields to create a shipment.");
      return;
    }
    setLoading(true);
    setError(null);
    setTxHash(null);
    try {
      const tx = await contract.createShipment(newShipmentId, productDetails);
      setTxHash(tx.hash);
      console.log(`Transaction sent: ${tx.hash}`);
      await tx.wait(); // Wait for the transaction to be mined
      alert(`Shipment '${newShipmentId}' created successfully!`);
      setNewShipmentId('');
      setProductDetails('');
    } catch (err: any) {
      console.error("Error creating shipment:", err);
      setError(err.reason || "An error occurred during transaction.");
    } finally {
      setLoading(false);
    }
  };

  const handleTransferCustody = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!signer || !transferShipmentId || !newCustodian) {
      alert("Please fill all fields to transfer custody.");
      return;
    }
    if (!ethers.isAddress(newCustodian)) {
        alert("Invalid new custodian address.");
        return;
    }
    setLoading(true);
    setError(null);
    setTxHash(null);
    try {
      const tx = await contract.transferCustody(transferShipmentId, newCustodian);
      setTxHash(tx.hash);
      console.log(`Transaction sent: ${tx.hash}`);
      await tx.wait();
      alert(`Custody of '${transferShipmentId}' transferred successfully!`);
      setTransferShipmentId('');
      setNewCustodian('');
    } catch (err: any) {
      console.error("Error transferring custody:", err);
      setError(err.reason || "An error occurred during transaction.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
      <h2 className="text-2xl font-semibold mb-4 text-blue-300">Manage Shipments</h2>
      
      {/* Create Shipment Form */}
      <form onSubmit={handleCreateShipment} className="mb-8 p-4 border border-blue-500 rounded-md">
        <h3 className="text-xl font-medium text-blue-200 mb-3">Create New Shipment (Manufacturer Role)</h3>
        <div className="flex flex-col space-y-3">
          <input
            type="text"
            placeholder="New Shipment ID (e.g., SHIP001)"
            value={newShipmentId}
            onChange={(e) => setNewShipmentId(e.target.value)}
            className="p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:border-blue-500"
          />
          <input
            type="text"
            placeholder="Product Details (e.g., Vaccine Batch XYZ)"
            value={productDetails}
            onChange={(e) => setProductDetails(e.target.value)}
            className="p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 transition-colors"
          >
            {loading ? 'Processing...' : 'Create Shipment'}
          </button>
        </div>
      </form>

      {/* Transfer Custody Form */}
      <form onSubmit={handleTransferCustody} className="p-4 border border-green-500 rounded-md">
        <h3 className="text-xl font-medium text-green-200 mb-3">Transfer Custody (Custodian Role)</h3>
        <div className="flex flex-col space-y-3">
          <input
            type="text"
            placeholder="Shipment ID to Transfer"
            value={transferShipmentId}
            onChange={(e) => setTransferShipmentId(e.target.value)}
            className="p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:border-green-500"
          />
          <input
            type="text"
            placeholder="New Custodian Address (0x...)"
            value={newCustodian}
            onChange={(e) => setNewCustodian(e.target.value)}
            className="p-2 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:border-green-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 transition-colors"
          >
            {loading ? 'Processing...' : 'Transfer Custody'}
          </button>
        </div>
      </form>

      {/* Transaction Status Area */}
      {txHash && <p className="mt-4 text-sm text-gray-400">Transaction Sent: <span className="font-mono text-cyan-400">{txHash}</span></p>}
      {error && <p className="mt-4 text-red-500">Error: {error}</p>}
    </div>
  );
};