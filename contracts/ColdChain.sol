// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title ColdChain
 * @dev A smart contract to track the integrity of a pharmaceutical cold chain.
 * It manages shipment creation, custody transfers, and real-time temperature monitoring.
 */
contract ColdChain {
    // --- Data Structures ---

    struct TempLog {
        uint256 timestamp;
        int256 temp; // Use int256 for temperatures that can be negative
        string location;
    }

    struct Shipment {
        string shipmentID;
        string status; // e.g., "Created", "In-Transit", "Compromised", "Delivered"
        address custodian; // Address of the current custodian
        int256 maxTempLimit; // e.g., 8 degrees Celsius
        int256 minTempLimit; // e.g., 2 degrees Celsius
        TempLog[] tempHistory;
        string productDetails;
    }

    // --- State Variables ---

    mapping(string => Shipment) public shipments; // Maps a shipment ID to its Shipment struct
    address public owner; // The manufacturer (contract deployer)
    address public iotOracle; // The address designated as the IoT oracle

    // --- Events ---

    event ShipmentCreated(string indexed shipmentID, address indexed manufacturer, string productDetails);
    event TemperatureUpdated(string indexed shipmentID, int256 currentTemp, string location);
    event FaultDetected(string indexed shipmentID, int256 currentTemp, address indexed custodian);
    event CustodyTransferred(string indexed shipmentID, address indexed oldCustodian, address indexed newCustodian);

    // --- Modifiers ---

    modifier onlyManufacturer() {
        require(msg.sender == owner, "Only manufacturer can call this function");
        _;
    }
    
    modifier onlyOracle() {
        require(msg.sender == iotOracle, "Only IoT Oracle can call this function");
        _;
    }

    // --- Constructor ---

    constructor(address _iotOracleAddress) {
        owner = msg.sender;
        iotOracle = _iotOracleAddress;
    }

    // --- Core Functions ---

    /**
     * @dev Creates a new shipment record on the blockchain.
     * @notice This function is compatible with older compilers by populating the struct in storage.
     * @param _shipmentID A unique identifier for the shipment.
     * @param _productDetails Details about the product being shipped.
     */
    function createShipment(string memory _shipmentID, string memory _productDetails) public onlyManufacturer returns (bool) {
        require(bytes(shipments[_shipmentID].shipmentID).length == 0, "Shipment with this ID already exists");

        // Get a storage pointer to the new shipment struct first.
        Shipment storage newShipment = shipments[_shipmentID];
        
        // Populate its fields directly in storage.
        newShipment.shipmentID = _shipmentID;
        newShipment.status = "Created";
        newShipment.custodian = msg.sender;
        newShipment.maxTempLimit = 8;
        newShipment.minTempLimit = 2;
        newShipment.productDetails = _productDetails;
        // The 'tempHistory' array is already empty by default when created in storage.

        emit ShipmentCreated(_shipmentID, msg.sender, _productDetails);
        return true;
    }

    /**
     * @dev Updates the temperature log for a given shipment.
     * @notice This function is compatible with older compilers by creating the new TempLog directly in storage.
     * @param _shipmentID The ID of the shipment to update.
     * @param _currentTemp The current temperature reading.
     * @param _location The current location of the shipment.
     */
    function updateTemperature(string memory _shipmentID, int256 _currentTemp, string memory _location) public onlyOracle returns (bool) {
        Shipment storage targetShipment = shipments[_shipmentID];
        require(bytes(targetShipment.shipmentID).length > 0, "Shipment does not exist");
        
        // Create a new empty element in the array first
        targetShipment.tempHistory.push(); 
        // Get a pointer to the new element
        TempLog storage newLog = targetShipment.tempHistory[targetShipment.tempHistory.length - 1]; 
        // Populate the fields directly in storage
        newLog.timestamp = block.timestamp;
        newLog.temp = _currentTemp;
        newLog.location = _location;
        
        emit TemperatureUpdated(_shipmentID, _currentTemp, _location);

        // Check for temperature breach
        if (_currentTemp > targetShipment.maxTempLimit || _currentTemp < targetShipment.minTempLimit) {
            // Use abi.encode for safer hashing
            if (keccak256(abi.encode(targetShipment.status)) != keccak256(abi.encode("Compromised"))) {
                targetShipment.status = "Compromised";
                emit FaultDetected(_shipmentID, _currentTemp, targetShipment.custodian);
            }
        }
        return true;
    }

    /**
     * @dev Transfers custody of a shipment to a new party.
     * @param _shipmentID The ID of the shipment to transfer.
     * @param _newCustodian The address of the new custodian.
     */
    function transferCustody(string memory _shipmentID, address _newCustodian) public returns (bool) {
        Shipment storage targetShipment = shipments[_shipmentID];
        require(bytes(targetShipment.shipmentID).length > 0, "Shipment does not exist");
        require(msg.sender == targetShipment.custodian, "Only current custodian can transfer custody");
        // Use abi.encode for safer hashing
        require(keccak256(abi.encode(targetShipment.status)) != keccak256(abi.encode("Compromised")), "Shipment is compromised and cannot be transferred");
        
        address oldCustodian = targetShipment.custodian;
        targetShipment.custodian = _newCustodian;
        targetShipment.status = "In-Transit";
        
        emit CustodyTransferred(_shipmentID, oldCustodian, _newCustodian);
        return true;
    }

    // --- View/Getter Functions for Frontend ---

    function getShipmentStatus(string memory _shipmentID) public view returns (string memory) {
        return shipments[_shipmentID].status;
    }

    function getShipmentCustodian(string memory _shipmentID) public view returns (address) {
        return shipments[_shipmentID].custodian;
    }

    function getShipmentDetails(string memory _shipmentID) public view returns (string memory id, string memory status, address custodian, int256 minTempLimit, int256 maxTempLimit) {
        Shipment storage s = shipments[_shipmentID];
        require(bytes(s.shipmentID).length > 0, "Shipment does not exist");
        return (s.shipmentID, s.status, s.custodian, s.minTempLimit, s.maxTempLimit);
    }

    function getShipmentProductDetails(string memory _shipmentID) public view returns (string memory) {
        Shipment storage s = shipments[_shipmentID];
        require(bytes(s.shipmentID).length > 0, "Shipment does not exist");
        return s.productDetails;
    }

    function getTempHistoryCount(string memory _shipmentID) public view returns (uint256) {
        Shipment storage s = shipments[_shipmentID];
        require(bytes(s.shipmentID).length > 0, "Shipment does not exist");
        return s.tempHistory.length;
    }

    function getTempHistoryEntry(string memory _shipmentID, uint256 _index) public view returns (uint256 timestamp, int256 temp, string memory location) {
        Shipment storage s = shipments[_shipmentID];
        require(bytes(s.shipmentID).length > 0, "Shipment does not exist");
        require(_index < s.tempHistory.length, "Index out of bounds");
        TempLog storage log = s.tempHistory[_index];
        return (log.timestamp, log.temp, log.location);
    }
}