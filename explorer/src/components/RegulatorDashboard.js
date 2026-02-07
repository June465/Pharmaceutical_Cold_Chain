import ShipmentDetails from "./ShipmentDetails";
import BlockInspector from "./BlockInspector";
import RoleAdmin from "./RoleAdmin";
import TemperatureTimeline from "./TemperatureTimeline";

// This component receives the full shipments object
export default function RegulatorDashboard({ shipments, loading }) {
  const shipmentList = Object.values(shipments || {});

  return (
    <div className="stack">
      <RoleAdmin />
      <BlockInspector />
      <TemperatureTimeline shipments={shipments} />

      {loading && (
        <div className="panel"><p>Finding existing shipments on the blockchain...</p></div>
      )}

      {!loading && (
        <>
          {shipmentList.length === 0 ? (
            <div className="panel"><p>No shipments found. Please create one from the Manufacturer tab.</p></div>
          ) : (
            // Map over the array of shipment objects and render a dumb component for each
            shipmentList.map(shipment => (
              <ShipmentDetails key={shipment.shipmentId} shipment={shipment} />
            ))
          )}
        </>
      )}
    </div>
  );
}