# node/src/contracts/pharma.py

class PharmaContract:
    """
    A smart contract for tracking pharmaceutical cold chain data.
    """
    def __init__(self):
        # The 'storage' dictionary is the contract's persistent state.
        self.storage = {
            "shipments": {}
        }

    def record_temperature(self, shipment_id: str, temperature: float, timestamp: int):
        """
        Records a new temperature reading for a specific shipment.
        This method modifies the contract's storage.
        """
        if shipment_id not in self.storage["shipments"]:
            # Initialize the record for a new shipment
            self.storage["shipments"][shipment_id] = {
                "readings": [],
                "breaches": 0,
                "status": "IN_TRANSIT"
            }
        
        # Add the new reading
        self.storage["shipments"][shipment_id]["readings"].append({
            "temp": temperature,
            "ts": timestamp
        })

        # Simple business logic: Check for temperature breaches
        if not (2.0 <= temperature <= 8.0):
            self.storage["shipments"][shipment_id]["breaches"] += 1
            self.storage["shipments"][shipment_id]["status"] = "BREACH_DETECTED"