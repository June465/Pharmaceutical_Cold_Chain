// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ColdChain {

    struct Shipment {
        string status;
        address custodian;
        uint256 maxTempLimit;
        uint256 minTempLimit;
        uint256[] tempHistory; 
    }

    mapping(string => Shipment) public shipments;

    address public manufacturer;
    
    constructor(address _manufacturer) {
        manufacturer = _manufacturer;
    }

    function createShipment(string memory shipmentID, uint256 maxTemp, uint256 minTemp) public {
        require(msg.sender == manufacturer, "Only the manufacturer can create a shipment.");
        require(bytes(shipments[shipmentID].status).length == 0, "Shipment ID already exists.");

        shipments[shipmentID] = Shipment({
            status: "Created",
            custodian: msg.sender,
            maxTempLimit: maxTemp,
            minTempLimit: minTemp,
            tempHistory: new uint256[](0)
        });
    }

    function updateTemperature(string memory shipmentID, uint256 currentTemp) public {
        require(bytes(shipments[shipmentID].status).length > 0, "Shipment does not exist.");
        
        shipments[shipmentID].tempHistory.push(currentTemp);

        if (currentTemp > shipments[shipmentID].maxTempLimit || currentTemp < shipments[shipmentID].minTempLimit) {
            if (keccak256(abi.encodePacked(shipments[shipmentID].status)) != keccak256(abi.encodePacked("Compromised"))) {
                shipments[shipmentID].status = "Compromised";
            }
        }
    }

    function transferCustody(string memory shipmentID, address newCustodian) public {
        require(bytes(shipments[shipmentID].status).length > 0, "Shipment does not exist.");
        require(msg.sender == shipments[shipmentID].custodian, "Only the current custodian can transfer ownership.");
        require(keccak256(abi.encodePacked(shipments[shipmentID].status)) != keccak256(abi.encodePacked("Compromised")), "Shipment is compromised and cannot be transferred.");
        
        shipments[shipmentID].custodian = newCustodian;
        shipments[shipmentID].status = "Delivered";
    }
    
    function getShipmentStatus(string memory shipmentID) public view returns (string memory) {
        require(bytes(shipments[shipmentID].status).length > 0, "Shipment does not exist.");
        return shipments[shipmentID].status;
    }
}