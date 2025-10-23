// src/components/ShipmentViewer.tsx

import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';

interface ShipmentViewerProps {
  contract: ethers.Contract;
}

export const ShipmentViewer: React.FC<ShipmentViewerProps> = ({ contract }) => {
  const [shipmentId, setShipmentId] = useState('SHIP001'); // Default to SHIP001 for convenience
  const [shipmentDetails, setShipmentDetails] = useState<any>(null);
  const [tempHistory, setTempHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchShipmentData = async () => {
    if (!shipmentId) return;
    setLoading(true);
    setError(null);
    try {
      // Fetch main details
      const details = await contract.getShipmentDetails(shipmentId);
      const productDetails = await contract.getShipmentProductDetails(shipmentId);
      
      setShipmentDetails({
        id: details[0],
        status: details[1],
        custodian: details[2],
        minTemp: details[3].toNumber(),
        maxTemp: details[4].toNumber(),
        product: productDetails,
      });

      // Fetch temperature history
      const historyCount = (await contract.getTempHistoryCount(shipmentId)).toNumber();
      const historyPromises = [];
      for (let i = 0; i < historyCount; i++) {
        historyPromises.push(contract.getTempHistoryEntry(shipmentId, i));
      }
      const historyResults = await Promise.all(historyPromises);
      const formattedHistory = historyResults.map(log => ({
        timestamp: new Date(log.timestamp.toNumber() * 1000).toLocaleString(),
        temp: log.temp.toNumber(),
        location: log.location,
      }));
      setTempHistory(formattedHistory);

    } catch (e: any) {
      console.error("Error fetching shipment data:", e);
      setError("Shipment not found or an error occurred.");
      setShipmentDetails(null);
      setTempHistory([]);
    } finally {
      setLoading(false);
    }
  };

  // Set up event listeners for real-time updates
  useEffect(() => {
    const handleEvent = (sId: string) => {
      if (sId === shipmentId) {
        console.log(`Event detected for ${sId}, refreshing data...`);
        fetchShipmentData();
      }
    };
    
    contract.on("TemperatureUpdated", handleEvent);
    contract.on("FaultDetected", handleEvent);
    contract.on("CustodyTransferred", handleEvent);

    // Cleanup function to remove listeners when component unmounts
    return () => {
      contract.off("TemperatureUpdated", handleEvent);
      contract.off("FaultDetected", handleEvent);
      contract.off("CustodyTransferred", handleEvent);
    };
  }, [contract, shipmentId]); // Re-subscribe if the contract or shipmentId changes

  return (
    <div className="w-full bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
      <h2 className="text-2xl font-semibold mb-4 text-blue-300">View Shipment Status</h2>
      <div className="flex items-center mb-4">
        <input
          type="text"
          placeholder="Enter Shipment ID"
          value={shipmentId}
          onChange={(e) => setShipmentId(e.target.value)}
          className="flex-grow p-2 mr-4 rounded bg-gray-700 border border-gray-600 focus:outline-none focus:border-blue-500"
        />
        <button
          onClick={fetchShipmentData}
          disabled={loading}
          className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 transition-colors"
        >
          {loading ? 'Loading...' : 'View Shipment'}
        </button>
      </div>

      {error && <p className="text-red-500">{error}</p>}

      {shipmentDetails && (
        <div className="bg-gray-700 p-4 rounded-md">
          <h3 className="text-xl font-medium text-blue-200 mb-2">Details for: {shipmentDetails.id}</h3>
          <p><strong>Product:</strong> {shipmentDetails.product}</p>
          <p><strong>Status:</strong> 
            <span className={shipmentDetails.status === "Compromised" ? "text-red-500 font-bold" : "text-green-400 font-bold"}>
              {' '}{shipmentDetails.status}
            </span>
          </p>
          <p><strong>Custodian:</strong> <span className="font-mono text-yellow-300 text-sm">{shipmentDetails.custodian}</span></p>
          <p><strong>Temp Limits:</strong> {shipmentDetails.minTemp}°C to {shipmentDetails.maxTemp}°C</p>

          <h4 className="text-lg font-medium text-blue-200 mt-4 mb-2">Temperature History:</h4>
          <div className="max-h-60 overflow-y-auto pr-2">
            {tempHistory.length > 0 ? (
              <ul className="list-disc pl-5 space-y-1">
                {tempHistory.map((log, index) => (
                  <li key={index} className={log.temp < shipmentDetails.minTemp || log.temp > shipmentDetails.maxTemp ? "text-red-400" : ""}>
                    {log.timestamp}: <strong>{log.temp}°C</strong> at "{log.location}"
                    {log.temp < shipmentDetails.minTemp || log.temp > shipmentDetails.maxTemp && <span className="font-bold"> (BREACH!)</span>}
                  </li>
                ))}
              </ul>
            ) : (
              <p>No temperature history recorded yet.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};