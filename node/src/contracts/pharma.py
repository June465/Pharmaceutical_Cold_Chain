# node/src/contracts/pharma.py
class BaseContract:
    def __init__(self, address: str, world_state, sender: str):
        self.address = address
        self.world_state = world_state
        self.sender = sender
        self.storage = self.world_state.get_account_storage(self.address) or {}

    def save_storage(self):
        self.world_state.set_account_storage(self.address, self.storage)

class PharmaContract(BaseContract):
    def constructor(self, min_temp: int, max_temp: int):
        self.storage['owner'] = self.sender
        self.storage['min_temp'] = min_temp
        self.storage['max_temp'] = max_temp
        self.storage['shipments'] = {}

    def record_temperature(self, shipment_id: str, temp: float, location: list):
        min_temp = self.storage['min_temp']
        max_temp = self.storage['max_temp']
        
        if shipment_id not in self.storage['shipments']:
            self.storage['shipments'][shipment_id] = {'status': 'IN_TRANSIT', 'readings': []}
        
        current_status = self.storage['shipments'][shipment_id]['status']
        status = 'BREACHED' if current_status == 'BREACHED' or not (min_temp <= temp <= max_temp) else 'IN_TRANSIT'
            
        if status == 'BREACHED' and current_status != 'BREACHED':
            print(f"!!! TEMPERATURE BREACH DETECTED for {shipment_id}: {temp} !!!")

        self.storage['shipments'][shipment_id]['status'] = status
        self.storage['shipments'][shipment_id]['readings'].append({'temp': temp, 'location': location, 'reporter': self.sender})
        print(f"Recorded temp for {shipment_id}: {temp}°C. Status: {status}")