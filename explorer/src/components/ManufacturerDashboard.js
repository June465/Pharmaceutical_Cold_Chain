import { useState } from "react";
import { getSignerContract } from "../services/blockchain";

export default function ManufacturerDashboard() {
  // State for creating a shipment
  const [createId, setCreateId] = useState("");
  const [recipient, setRecipient] = useState("");
  const [createStatus, setCreateStatus] = useState("");

  // State for proposing a transfer
  const [transferId, setTransferId] = useState("");
  const [nextCustodian, setNextCustodian] = useState("");
  const [transferStatus, setTransferStatus] = useState("");

  async function handleCreate() {
    if (!createId || !recipient) {
      alert("Please provide a Shipment ID and a Recipient Pharmacy address.");
      return;
    }
    setCreateStatus("Submitting...");
    try {
      const contract = await getSignerContract();
      const tx = await contract.createShipment(createId, recipient);
      await tx.wait();
      setCreateStatus(`Shipment '${createId}' created successfully!`);
      setCreateId("");
      setRecipient("");
    } catch (e) {
      console.error(e);
      setCreateStatus(`Error: ${e.reason || e.message}`);
    }
  }

  // --- THIS IS THE NEW FUNCTION ---
  async function handlePropose() {
    if (!transferId || !nextCustodian) {
      alert("Please provide the Shipment ID and the next carrier's address.");
      return;
    }
    setTransferStatus("Submitting proposal...");
    try {
      const contract = await getSignerContract();
      // The Manufacturer calls proposeTransfer to kick off the logistics chain
      const tx = await contract.proposeTransfer(transferId, nextCustodian);
      await tx.wait();
      setTransferStatus(`Transfer for '${transferId}' proposed to ${nextCustodian.substring(0, 6)}...`);
      setTransferId("");
      setNextCustodian("");
    } catch (e) {
      console.error(e);
      setTransferStatus(`Error: ${e.reason || e.message}`);
    }
  }

  return (
    <div className="stack">
      <section className="panel">
        <h3>Create Shipment</h3>
        <div className="field">
          <label>Shipment ID</label>
          <input value={createId} onChange={(e) => setCreateId(e.target.value)} />
        </div>
        <div className="field">
          <label>Recipient Pharmacy Address</label>
          <input value={recipient} onChange={(e) => setRecipient(e.target.value)} />
        </div>
        <button onClick={handleCreate}>Create</button>
        {createStatus && <p className="status-text">{createStatus}</p>}
      </section>

      {/* --- THIS IS THE NEW UI SECTION --- */}
      <section className="panel">
        <h3>Propose Transfer to Logistics</h3>
        <p className="subtle">As the current custodian, you can propose a transfer to the first carrier.</p>
        <div className="field">
          <label>Shipment ID</label>
          <input value={transferId} onChange={(e) => setTransferId(e.target.value)} />
        </div>
        <div className="field">
          <label>Next Carrier Address</label>
          <input value={nextCustodian} onChange={(e) => setNextCustodian(e.target.value)} />
        </div>
        <button onClick={handlePropose}>Propose Transfer</button>
        {transferStatus && <p className="status-text">{transferStatus}</p>}
      </section>
    </div>
  );
}