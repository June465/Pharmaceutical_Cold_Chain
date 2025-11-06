import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import './App.css';
import { contract, liveContract, httpProvider, myRoles, getLogsChunked, fetchReadingsFromLogs } from './services/blockchain';
import { getSigner } from './services/wallet';
import RegulatorDashboard from "./components/RegulatorDashboard";
import ManufacturerDashboard from "./components/ManufacturerDashboard";
import LogisticsDashboard from "./components/LogisticsDashboard";
import PharmacyDashboard from "./components/PharmacyDashboard";

function WalletConnector() {
  const [address, setAddress] = useState(null);
  const [roles, setRoles] = useState([]);

  const connectWallet = async () => {
    try {
      const signer = await getSigner();
      const addr = await signer.getAddress();
      setAddress(addr);
      const userRoles = await myRoles(addr);
      setRoles(userRoles);
    } catch (e) {
      console.error("Failed to connect wallet:", e);
      alert("Failed to connect wallet. See console for details.");
    }
  };

  useEffect(() => {
    if (window.ethereum) {
      connectWallet();
      window.ethereum.on('accountsChanged', connectWallet);
      window.ethereum.on('chainChanged', () => window.location.reload());
    }
  }, []);

  if (!address) {
    return <button onClick={connectWallet} className="wallet-button">Connect Wallet</button>;
  }

  return (
    <div className='wallet-info panel'>
      <div><strong>Connected:</strong> {address.substring(0, 6)}...{address.substring(address.length - 4)}</div>
      <div><strong>Roles:</strong> {roles.length > 0 ? roles.join(', ') : 'None'}</div>
    </div>
  );
}

function App() {
  const [shipments, setShipments] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const provider = contract.runner?.provider;
    if (!provider) return;

    // This is the SINGLE AUTHORITATIVE function for fetching all data for a shipment.
    const fetchShipment = async (shipmentId) => {
      try {
        const id = shipmentId.toString();
        // 1. Get core data from the contract's view function
        const [shipmentData] = await contract.getShipment(id);
        // 2. Get temperature history from event logs
        const readings = await fetchReadingsFromLogs(id);

        // 3. Robustly update the state
        setShipments(prev => ({
          ...prev,
          [id]: {
            ...prev[id], // Preserve any previous state
            shipmentId: id,
            status: shipmentData.status,
            breachCount: Number(shipmentData.breachCount),
            readings,
          }
        }));
      } catch (err) {
        console.error(`Error fetching shipment ${shipmentId}:`, err);
      }
    };
    
    // Finds all existing shipments and fetches their full data SEQUENTIALLY
    const loadInitialData = async () => {
      console.log("Starting initial data load...");
      setLoading(true);
      try {
        const currentBlock = await httpProvider.getBlockNumber();
        const LOOKBACK = 2000;
        const startBlock = Math.max(currentBlock - LOOKBACK, 0);
        const initTopic = contract.interface.getEvent('ShipmentCreated').topicHash;

        const logs = await getLogsChunked({
          address: contract.target,
          topics: [initTopic],
          fromBlock: startBlock,
          toBlock: currentBlock
        });

        const shipmentIds = [...new Set(logs.map(l => String(contract.interface.parseLog(l).args[1])))].filter(id => id);
        console.log("Found unique shipment IDs:", shipmentIds);

        // --- THIS IS THE FINAL FIX ---
        // Instead of Promise.all, we use a sequential for...of loop.
        // This ensures we only fetch data for one shipment at a time.
        for (const id of shipmentIds) {
          console.log(`Fetching full data for ${id}...`);
          await fetchShipment(id);
        }
        
      } catch (err) {
        console.error("Error during initial data load:", err);
      }
      setLoading(false);
      console.log("Initial data load finished.");
    };

    // Listeners are correct, they call fetchShipment which is now safe
    const setupEventListeners = () => {
      liveContract.on("ShipmentCreated", (_key, id) => fetchShipment(id));
      liveContract.on("CustodyTransferred", (_key, id) => fetchShipment(id));
      liveContract.on("Delivered", (_key, id) => fetchShipment(id));
      liveContract.on("TemperatureRecorded", (_key, id) => fetchShipment(id));
    };

    loadInitialData();
    setupEventListeners();
    
    return () => {
      liveContract.removeAllListeners();
    };
  }, []);

  return (
    <BrowserRouter>
      <div className="App">
        <header className="App-header"><h1>Pharma Cold Chain Tracker</h1></header>
        <main className="container">
          <WalletConnector />
          <nav className="tabs">
            <NavLink to="/regulator">Regulator</NavLink>
            <NavLink to="/manufacturer">Manufacturer</NavLink>
            <NavLink to="/logistics">Logistics</NavLink>
            <NavLink to="/pharmacy">Pharmacy</NavLink>
          </nav>
          <Routes>
            <Route path="/" element={<RegulatorDashboard shipments={shipments} loading={loading} />} />
            <Route path="/regulator" element={<RegulatorDashboard shipments={shipments} loading={loading} />} />
            <Route path="/manufacturer" element={<ManufacturerDashboard />} />
            <Route path="/logistics" element={<LogisticsDashboard />} />
            <Route path="/pharmacy" element={<PharmacyDashboard />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;