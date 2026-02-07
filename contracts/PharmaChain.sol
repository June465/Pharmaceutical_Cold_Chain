// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";

contract PharmaChain is AccessControl {
    bytes32 public constant MANUFACTURER_ROLE = keccak256("MANUFACTURER_ROLE");
    bytes32 public constant REGULATOR_ROLE    = keccak256("REGULATOR_ROLE");
    bytes32 public constant CARRIER_ROLE      = keccak256("CARRIER_ROLE");
    bytes32 public constant PHARMACY_ROLE     = keccak256("PHARMACY_ROLE");
    bytes32 public constant ORACLE_ROLE       = keccak256("ORACLE_ROLE");

    enum Status { CREATED, IN_TRANSIT, BREACH_DETECTED, DELIVERED }

    struct Shipment {
        string  shipmentId;
        address manufacturer;
        address currentCustodian;
        address recipient;
        Status  status;
        uint256 createdAt;
        uint256 breachCount;
        bool    exists;
    }

    struct CustodyHop {
        address from_;
        address to_;
        uint256 pickupTime;
        uint256 dropTime;
    }

    mapping(bytes32 => Shipment) public shipments;
    mapping(bytes32 => CustodyHop[]) private custody;
    mapping(bytes32 => string) private birthCertIpfs;

    event ProductBirth(bytes32 indexed key, string shipmentId, address indexed manufacturer, string birthCertUri);
    event ShipmentCreated(bytes32 indexed key, string shipmentId, address indexed manufacturer, address indexed recipient);
    event CustodyProposed(bytes32 indexed key, address from_, address to_, uint256 atBlock);
    event PickupConfirmed(bytes32 indexed key, address indexed by, uint256 atBlock);
    event DropConfirmed(bytes32 indexed key, address indexed by, uint256 atBlock);
    event CustodyTransferred(bytes32 indexed key, address from_, address to_, uint256 atBlock);

    event TemperatureRecorded(bytes32 indexed key, string shipmentId, int256 temperature, uint256 timestamp, bytes32 txMerklePlaceHolder);
    event TemperatureBreach(bytes32 indexed key, string shipmentId, int256 temperature, uint256 timestamp);

    event Delivered(bytes32 indexed key, address indexed pharmacy, uint256 atBlock);

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(REGULATOR_ROLE, admin);
    }

    function grantRoleTo(bytes32 role, address account) external onlyRole(REGULATOR_ROLE) {
        _grantRole(role, account);
    }
    function revokeRoleFrom(bytes32 role, address account) external onlyRole(REGULATOR_ROLE) {
        _revokeRole(role, account);
    }

    function _key(string memory id) internal pure returns (bytes32) {
        return keccak256(bytes(id));
    }

    // Manufacturer
    function registerProductBirth(string calldata shipmentId, string calldata birthCertUri)
        external onlyRole(MANUFACTURER_ROLE)
    {
        bytes32 k = _key(shipmentId);
        require(!shipments[k].exists, "exists");
        birthCertIpfs[k] = birthCertUri;
        emit ProductBirth(k, shipmentId, msg.sender, birthCertUri);
    }

    function createShipment(string calldata shipmentId, address recipientPharmacy)
        external onlyRole(MANUFACTURER_ROLE)
    {
        bytes32 k = _key(shipmentId);
        require(!shipments[k].exists, "exists");
        shipments[k] = Shipment({
            shipmentId: shipmentId,
            manufacturer: msg.sender,
            currentCustodian: msg.sender,
            recipient: recipientPharmacy,
            status: Status.CREATED,
            createdAt: block.timestamp,
            breachCount: 0,
            exists: true
        });
        emit ShipmentCreated(k, shipmentId, msg.sender, recipientPharmacy);
    }

    // Logistics / Custody
    function proposeTransfer(string calldata shipmentId, address nextCarrier)
        external onlyRole(CARRIER_ROLE)
    {
        bytes32 k = _key(shipmentId);
        require(shipments[k].exists, "no shipment");
        require(shipments[k].currentCustodian == msg.sender, "not custodian");

        custody[k].push(CustodyHop({
            from_: msg.sender,
            to_: nextCarrier,
            pickupTime: 0,
            dropTime: 0
        }));
        emit CustodyProposed(k, msg.sender, nextCarrier, block.number);
    }

    function confirmPickup(string calldata shipmentId)
        external onlyRole(CARRIER_ROLE)
    {
        bytes32 k = _key(shipmentId);
        require(custody[k].length > 0, "no proposal");
        CustodyHop storage hop = custody[k][custody[k].length - 1];
        require(hop.to_ == msg.sender, "not proposed to you");
        require(hop.pickupTime == 0, "already picked");
        hop.pickupTime = block.timestamp;
        shipments[k].status = Status.IN_TRANSIT;
        emit PickupConfirmed(k, msg.sender, block.number);
    }

    function confirmDrop(string calldata shipmentId)
        external onlyRole(CARRIER_ROLE)
    {
        bytes32 k = _key(shipmentId);
        require(custody[k].length > 0, "no proposal");
        CustodyHop storage hop = custody[k][custody[k].length - 1];
        require(hop.to_ == msg.sender, "not this carrier");
        require(hop.pickupTime != 0 && hop.dropTime == 0, "invalid state");
        hop.dropTime = block.timestamp;

        shipments[k].currentCustodian = msg.sender;
        emit DropConfirmed(k, msg.sender, block.number);
        emit CustodyTransferred(k, hop.from_, hop.to_, block.number);
    }

    // Oracle temperature
    function recordTemperature(string calldata shipmentId, int256 tempScaled100)
        external onlyRole(ORACLE_ROLE)
    {
        bytes32 k = _key(shipmentId);
        require(shipments[k].exists, "no shipment");
        uint256 ts = block.timestamp;
        emit TemperatureRecorded(k, shipmentId, tempScaled100, ts, bytes32(0));

        if (tempScaled100 < 200 || tempScaled100 > 800) {
            shipments[k].breachCount++;
            shipments[k].status = Status.BREACH_DETECTED;
            emit TemperatureBreach(k, shipmentId, tempScaled100, ts);
        }
    }

    // Pharmacy
    function markDelivered(string calldata shipmentId)
        external onlyRole(PHARMACY_ROLE)
    {
        bytes32 k = _key(shipmentId);
        require(shipments[k].exists, "no shipment");
        require(msg.sender == shipments[k].recipient, "not recipient");
        shipments[k].status = Status.DELIVERED;
        emit Delivered(k, msg.sender, block.number);
    }

    // Views
    function getShipment(string calldata shipmentId)
        external view
        returns (Shipment memory s, CustodyHop[] memory hops, string memory birthUri)
    {
        bytes32 k = _key(shipmentId);
        s = shipments[k];
        hops = custody[k];
        birthUri = birthCertIpfs[k];
    }
}
