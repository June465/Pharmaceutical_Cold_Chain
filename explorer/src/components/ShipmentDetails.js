import React, { useMemo, useState } from "react";
import { httpProvider } from "../services/blockchain";
import ShipmentHistory from './ShipmentHistory';

const toC = (scaled) => (scaled === undefined || scaled === null) ? 0 : Number(scaled) / 100;
const statusMap = ["CREATED", "IN_TRANSIT", "BREACH_DETECTED", "DELIVERED"];

export default function ShipmentDetails({ shipment }) {
  const sortedReadings = useMemo(
    () => (shipment?.readings ?? []).slice().sort((a, b) => b.timestamp - a.timestamp),
    [shipment]
  );

  const [selectedReading, setSelectedReading] = useState(null);
  const [details, setDetails] = useState(null);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);

  // This function is triggered when a user clicks a reading row
  const onRowClick = async (reading) => {
    if (!reading || !reading.blockNumber) return;

    // If clicking the same row again, toggle it closed
    if (selectedReading?.txHash === reading.txHash) {
      setSelectedReading(null);
      setDetails(null);
      return;
    }

    setSelectedReading(reading);
    setIsLoadingDetails(true);
    setDetails(null);
    try {
      // --- THIS IS THE UPGRADE ---
      // Fetch the block, neighbors, AND the transaction receipt in parallel
      const [block, prev, next, receipt] = await Promise.all([
        httpProvider.getBlock(reading.blockNumber),
        reading.blockNumber > 0 ? httpProvider.getBlock(reading.blockNumber - 1).catch(() => null) : null,
        httpProvider.getBlock(reading.blockNumber + 1).catch(() => null),
        httpProvider.getTransactionReceipt(reading.txHash),
      ]);

      setDetails({ 
        block, 
        prev, 
        next, 
        receipt // Add the receipt to our details state
      });
    } catch (e) {
      console.error("Failed to load details for row:", e);
    } finally {
      setIsLoadingDetails(false);
    }
  };

  const shipmentStatus = statusMap[shipment.status] || "UNKNOWN";

  return (
    <section className="panel">
      <h3 style={{ margin: 0, color: "#e94560" }}>Shipment ID: {shipment.shipmentId}</h3>
      <div style={{ marginTop: 8, display: "flex", justifyContent: "space-between" }}>
        <div><b>Status:</b> <span style={{ fontWeight: 'bold', color: shipmentStatus === "BREACH_DETECTED" ? "#ff6b6b" : shipmentStatus === "DELIVERED" ? "#6bff95" : "inherit" }}>{shipmentStatus}</span></div>
        <div><b>Breaches:</b> {shipment.breachCount ?? 0}</div>
      </div>

      <h4 style={{ marginTop: 16 }}>Temperature Readings:</h4>
      <div className="readings-list-container">
        {sortedReadings.length === 0 && <div className="reading-row">No readings yet.</div>}
        {sortedReadings.map((reading, index) => {
          const isSelected = selectedReading?.txHash === reading.txHash;
          const isBreach = toC(reading.temperature) < 2 || toC(reading.temperature) > 8;
          return (
            <React.Fragment key={reading.txHash ?? index}>
              <button className="reading-button" onClick={() => onRowClick(reading)} style={{ background: isSelected ? '#0f2744' : '#0e1a2a' }}>
                <span>{new Date(reading.timestamp).toLocaleString()}</span>
                <span style={{ opacity: 0.8, fontFamily: 'monospace' }}>Block #{reading.blockNumber}</span>
                <strong style={{ color: isBreach ? '#ff6b6b' : '#cde7ff' }}>{toC(reading.temperature).toFixed(2)}°C</strong>
              </button>
              {isSelected && (
                <div className="details-box">
                  {isLoadingDetails && <p>Loading on-chain details...</p>}
                  {details?.block && (
                    <>
                      <p><b>Time:</b> {new Date(selectedReading.timestamp).toLocaleString()}</p>
                      <p><b>Temp:</b> {toC(selectedReading.temperature).toFixed(2)}°C</p>
                      
                      {/* --- THIS IS THE UPGRADE --- */}
                      {/* Displaying details from the Transaction Receipt */}
                      <hr />
                      <p><b>Tx Hash:</b> <a href={`https://sepolia.etherscan.io/tx/${selectedReading.txHash}`} target="_blank" rel="noreferrer">{selectedReading.txHash}</a></p>
                      {details.receipt && <p><b>From (Oracle):</b> {details.receipt.from}</p>}
                      {details.receipt && <p><b>Gas Used:</b> {details.receipt.gasUsed.toString()}</p>}

                      <hr />
                      <p><b>Block #{details.block.number}:</b> {details.block.hash}</p>
                      <p><b>Parent:</b> {details.block.parentHash}</p>
                      <hr />
                      <p><b>Prev Block:</b> {details.prev ? `#${details.prev.number}` : "—"}</p>
                      <p><b>Next Block:</b> {details.next ? `#${details.next.number}` : "—"}</p>
                    </>
                  )}
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
      <ShipmentHistory shipmentId={shipment.shipmentId} />
    </section>
  );
}