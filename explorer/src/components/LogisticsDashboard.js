import { useState } from "react";
import { getSignerContract } from "../services/blockchain";

export default function LogisticsDashboard() {
  const [shipmentId, setShipmentId] = useState("");
  const [nextCustodian, setNextCustodian] = useState("");
  const [status, setStatus] = useState("");

  const handleAction = async (action) => {
    if (!shipmentId) {
      alert("Please provide a Shipment ID.");
      return;
    }
    let tx;
    const contract = await getSignerContract();
    try {
      if (action === "propose") {
        if (!nextCustodian) {
          alert("Please provide the next carrier's address.");
          return;
        }
        setStatus("Proposing transfer...");
        tx = await contract.proposeTransfer(shipmentId, nextCustodian);
      } else if (action === "pickup") {
        setStatus("Confirming pickup...");
        tx = await contract.confirmPickup(shipmentId);
      } else if (action === "drop") {
        setStatus("Confirming drop...");
        tx = await contract.confirmDrop(shipmentId);
      } else {
        return;
      }
      
      await tx.wait();
      setStatus(`Action '${action}' for shipment '${shipmentId}' was successful!`);
    } catch (e) {
      console.error(e);
      setStatus(`Error: ${e.reason || e.message}`);
    }
  };

  return (
    <div className="stack">
      <section className="panel">
        <h3>Logistics Actions</h3>
        
        {/* Propose Transfer Section */}
        <div className="field-group">
            <p className="subtle" title="As the current package custodian, you can propose a handoff to the next participant (another carrier or the final pharmacy).">
                <strong>Step 1: Propose Transfer</strong>
            </p>
            <div className="field">
                <label>Shipment ID</label>
                <input value={shipmentId} onChange={(e) => setShipmentId(e.target.value)} placeholder="e.g., SHIP-TEST-101" />
            </div>
            <div className="field">
                <label>Next Custodian Address</label>
                <input value={nextCustodian} onChange={(e) => setNextCustodian(e.target.value)} placeholder="0x... address of next carrier or pharmacy" />
            </div>
            <button onClick={() => handleAction("propose")}>Propose Transfer</button>
        </div>

        {/* Pickup & Drop Section */}
        <div className="field-group">
            <p className="subtle" title="If a transfer has been proposed to you, you must confirm you have received the package.">
                <strong>Step 2: Confirm Pickup</strong>
            </p>
            <div className="field">
                <label>Shipment ID</label>
                <input value={shipmentId} onChange={(e) => setShipmentId(e.target.value)} placeholder="e.g., SHIP-TEST-101" />
            </div>
            <button onClick={() => handleAction("pickup")}>Confirm Pickup</button>
        </div>

        <div className="field-group">
            <p className="subtle" title="After picking up the package and arriving at the next destination, confirm the drop-off.">
                <strong>Step 3: Confirm Drop</strong>
            </p>
            <div className="field">
                <label>Shipment ID</label>
                <input value={shipmentId} onChange={(e) => setShipmentId(e.target.value)} placeholder="e.g., SHIP-TEST-101" />
            </div>
            <button onClick={() => handleAction("drop")}>Confirm Drop</button>
        </div>

        {status && <p className="status-text">{status}</p>}
      </section>
    </div>
  );
}