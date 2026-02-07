import React, { useState, useEffect } from 'react';
import { fetchLifecycleEvents } from '../services/blockchain';

function HistoryRow({ event }) {
  const getTitle = () => {
    switch (event.type) {
      case "CREATED": return "Shipment Created by Manufacturer";
      case "TRANSFERRED": return "Custody Transferred";
      case "DELIVERED": return "Marked as Delivered by Pharmacy";
      default: return "Unknown Event";
    }
  };

  return (
    <div className="history-row">
      <div className="history-row-title">
        <span className={`pill ${event.type.toLowerCase()}`}>{event.type}</span>
        <span>{getTitle()}</span>
      </div>
      <div className="history-row-details">
        <span>{new Date(event.timestamp).toLocaleString()}</span>
        <span>Block #{event.blockNumber}</span>
        <a href={`https://sepolia.etherscan.io/tx/${event.txHash}`} target="_blank" rel="noreferrer">View Transaction</a>
      </div>
    </div>
  );
}

export default function ShipmentHistory({ shipmentId }) {
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadHistory = async () => {
      if (!shipmentId) return;
      setIsLoading(true);
      const events = await fetchLifecycleEvents(shipmentId);
      setHistory(events);
      setIsLoading(false);
    };
    loadHistory();
  }, [shipmentId]);

  return (
    <>
      <h4 style={{ marginTop: '24px' }}>Shipment Lifecycle & Audit Trail</h4>
      <div className="history-container">
        {isLoading && <p style={{padding: '12px'}}>Loading shipment history...</p>}
        {!isLoading && history.length === 0 && <p style={{padding: '12px'}}>No lifecycle events found.</p>}
        {!isLoading && history.map((event) => (
          <HistoryRow key={event.txHash} event={event} />
        ))}
      </div>
    </>
  );
}