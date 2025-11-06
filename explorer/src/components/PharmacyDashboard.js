import { useState } from "react";
import { contract, getSignerContract, fetchReadingsFromLogs } from "../services/blockchain"; // <-- Import the readings helper
import ShipmentDetails from "./ShipmentDetails";

export default function PharmacyDashboard() {
  const [shipmentId, setShipmentId] = useState("");
  const [status, setStatus] = useState("");
  const [shipmentData, setShipmentData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleLookup = async () => {
    if (!shipmentId) return;
    setIsLoading(true);
    setStatus("Looking up shipment...");
    setShipmentData(null);
    try {
      // 1. Fetch the core metadata from the contract
      const [sData] = await contract.getShipment(shipmentId);
      if (!sData.exists) {
        setStatus(`Shipment '${shipmentId}' not found.`);
        setIsLoading(false);
        return;
      }
      
      setStatus("Metadata found. Fetching temperature history...");

      // 2. Fetch the detailed temperature readings from the event logs
      const readings = await fetchReadingsFromLogs(shipmentId);

      // 3. Combine them into the final state object
      setShipmentData({
        shipmentId,
        status: sData.status,
        breachCount: Number(sData.breachCount),
        readings, // <-- Now we have the readings!
      });
      setStatus("Shipment data loaded successfully.");

    } catch (e) {
      console.error(e);
      setStatus("Error looking up shipment.");
    }
    setIsLoading(false);
  };

  const handleDelivery = async () => {
    if (!shipmentId) return;
    setStatus("Submitting confirmation...");
    try {
      const contract = await getSignerContract();
      const tx = await contract.markDelivered(shipmentId);
      await tx.wait();
      setStatus(`Shipment '${shipmentId}' successfully marked as delivered!`);
      handleLookup(); // Refresh the data to show the new "DELIVERED" status
    } catch (e) {
      console.error(e);
      setStatus(`Error: ${e.reason || e.message}`);
    }
  };

  return (
    <div className="stack">
      <section className="panel">
        <h3>Receive Shipment</h3>
        <div className="field">
          <label>Shipment ID</label>
          <input value={shipmentId} onChange={(e) => setShipmentId(e.target.value)} />
        </div>
        <button onClick={handleLookup} disabled={isLoading}>
          {isLoading ? "Loading..." : "Lookup Shipment"}
        </button>
        {status && !shipmentData && <p className="status-text">{status}</p>}
      </section>

      {shipmentData && (
        <>
          {shipmentData.breachCount > 0 && (
            <div className="panel warning">
              <strong>Warning:</strong> This shipment experienced {shipmentData.breachCount} temperature breach(es). Review the data carefully.
            </div>
          )}
          
          <ShipmentDetails shipment={shipmentData} />

          <section className="panel">
            <button onClick={handleDelivery} className="button-primary">Mark as Delivered</button>
            {status && <p className="status-text">{status}</p>}
          </section>
        </>
      )}
    </div>
  );
}