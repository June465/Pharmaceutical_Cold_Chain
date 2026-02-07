# Pharma Cold Chain Tracker DApp

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Blockchain](https://img.shields.io/badge/Blockchain-Ethereum-blueviolet.svg)](https://ethereum.org)
[![React](https://img.shields.io/badge/Frontend-React-blue.svg)](https://reactjs.org)
[![Solidity](https://img.shields.io/badge/Language-Solidity-lightgrey.svg)](https://soliditylang.org/)

A full-stack, multi-role decentralized application (DApp) for ensuring the integrity and transparency of the pharmaceutical cold chain, built on the Ethereum blockchain.

## About The Project

The pharmaceutical supply chain requires strict temperature controls to ensure product efficacy and patient safety. Traditional tracking systems are often siloed, opaque, and susceptible to data tampering. This project solves that problem by creating a transparent, immutable, and real-time audit trail for a shipment's entire lifecycle on the blockchain.

This DApp provides distinct, role-based dashboards for each key participant in the supply chain: **Regulators**, **Manufacturers**, **Logistics Carriers**, and **Pharmacies**. An automated IoT simulator acts as an oracle, submitting real-time temperature data to the smart contract, which enforces business logic, detects temperature breaches, and records all events immutably on-chain.

The result is a fully functional prototype that successfully demonstrates the power of blockchain technology for bringing trust and accountability to sensitive supply chains.

### Key Features

*   **🛡️ Role-Based Access Control (RBAC):** Secure smart contract logic using OpenZeppelin's `AccessControl` ensures that only authorized participants can perform critical actions (e.g., only a Manufacturer can create a shipment).
*   **🔗 End-to-End On-Chain Audit Trail:** Every critical event—creation, custody transfer, temperature reading, and final delivery—is recorded as an immutable event on the blockchain, providing a single source of truth.
*   **🖥️ Multi-Role UI Dashboards:** A clean, professional user interface with four distinct dashboards, providing each user with the specific tools and information relevant to their role.
*   **🌡️ Real-Time Data & Breach Detection:** An automated Python simulator sends continuous temperature readings. The smart contract automatically detects breaches (outside 2°C-8°C), updates the shipment's status, and flags it in the UI.
*   **🔍 Interactive Blockchain Explorer:** The UI includes powerful tools for inspecting block details, looking up transactions, and viewing a shipment's full lifecycle history, complete with timestamps and direct links to Etherscan.

## Architecture & Technology Stack

The application is composed of a React frontend, a Python simulator, and a Solidity smart contract, all interacting with the Ethereum Sepolia testnet via an Alchemy RPC provider.

[ IoT Simulator (Python) ] ----(Sends Tx)----> [ Alchemy RPC ] ----> [ PharmaChain Smart Contract ]
^
| (Reads Data & Sends Tx)
[ DApp Frontend (React) ] ----(User Interaction)---> [ MetaMask ] -------------

### Technology Stack

*   **Smart Contract:**
    *   **Language:** Solidity
    *   **Libraries:** OpenZeppelin Contracts
*   **Frontend DApp:**
    *   **Framework:** React
    *   **Blockchain Library:** Ethers.js
    *   **Routing:** React Router
    *   **Charting:** Recharts
*   **IoT Simulator:**
    *   **Language:** Python
    *   **Blockchain Library:** Web3.py
*   **Infrastructure:**
    *   **Blockchain:** Ethereum (Sepolia Testnet)
    *   **RPC Provider:** Alchemy
    *   **Wallet:** MetaMask

## Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

*   [Node.js](https://nodejs.org/) (v16 or later) and npm
*   [Python](https://www.python.org/downloads/) (v3.9 or later) and pip
*   [Git](https://git-scm.com/)
*   [MetaMask](https://metamask.io/) browser extension

### 1. One-Time Project Setup

1.  **Clone the Repository**
    ```bash
    git clone <your-repository-url>
    cd Pharmaceutical_Cold_Chain
    ```

2.  **Install Dependencies**
    ```bash
    # Set up the Python Simulator
    python -m venv venv                # Create a virtual environment
    source venv/bin/activate           # On Mac/Linux
    # .\venv\Scripts\activate          # On Windows
    pip install -r simulator/requirements.txt

    # Set up the React Frontend
    cd explorer
    npm install
    cd ..
    ```

3.  **Deploy the Smart Contract & Grant Roles**
    This is the most critical step. You will need several MetaMask accounts, each funded with Sepolia ETH from a faucet (e.g., [sepoliafaucet.com](https://sepoliafaucet.com/)).
    *   **Deploy:** Open `contracts/PharmaChain.sol` in the [Remix IDE](https://remix.ethereum.org/). Compile it, then go to the "Deploy" tab. Select "Injected Provider - MetaMask" and connect your main **Admin/Regulator** wallet. Paste your own address into the `admin` constructor field and deploy.
    *   **Copy the new contract address.**
    *   **Grant Roles:** In Remix, under "Deployed Contracts," use the `grantRoleTo` function to grant the following roles to your other funded accounts:
        *   `ORACLE_ROLE` -> The public address of the wallet whose private key you'll use for the simulator.
        *   `MANUFACTURER_ROLE` -> An account for the Manufacturer.
        *   `CARRIER_ROLE` -> An account for the Logistics Carrier.
        *   `PHARMACY_ROLE` -> An account for the Pharmacy.

4.  **Configure Environment Files (`.env`)**
    You need to create **two** `.env` files.

    *   **For the Simulator (in the project root):**
        *   Create a file named `.env`.
        *   Fill it with your details.
        ```
        # In <project_root>/.env
        ALCHEMY_URL="https://eth-sepolia.g.alchemy.com/v2/<your-alchemy-key>"
        CONTRACT_ADDRESS="<your-newly-deployed-contract-address>"
        SIMULATOR_PRIVATE_KEY="<0x-private-key-for-your-oracle-wallet>"
        SHIPMENT_ID="SHIP-TEST-101"
        ```

    *   **For the Frontend (in the `explorer` folder):**
        *   Create a file named `.env` inside the `explorer/` directory.
        *   Fill it with your details.
        ```
        # In <project_root>/explorer/.env
        REACT_APP_ALCHEMY_URL="https://eth-sepolia.g.alchemy.com/v2/<your-alchemy-key>"
        REACT_APP_ALCHEMY_WS_URL="wss://eth-sepolia.g.alchemy.com/v2/<your-alchemy-key>"
        REACT_APP_CONTRACT_ADDRESS="<your-newly-deployed-contract-address>"
        ```

### 2. Running the Application (Demo Workflow)

Run the frontend and the simulator in **two separate terminals**.

1.  **Start the Frontend (Terminal 1)**
    ```bash
    cd explorer
    npm start
    ```
    Your browser will open to `http://localhost:3000`.

2.  **Start the Simulator (Terminal 2)**
    ```bash
    # In the project root
    source venv/bin/activate  # Or .\venv\Scripts\activate
    python simulator/app.py
    ```

3.  **Demo the Full Workflow**
    *   **Connect:** In the DApp, click "Connect Wallet".
    *   **Create (As Manufacturer):** Switch MetaMask to your Manufacturer account. Go to the "Manufacturer" tab and create a shipment (e.g., `SHIP-TEST-101`).
    *   **Transfer (As Manufacturer):** On the same page, propose a transfer of that shipment to your Logistics/Carrier account.
    *   **Pickup (As Logistics):** Switch MetaMask to your Carrier account. Go to the "Logistics" tab and "Confirm Pickup" for the shipment. The status is now `IN_TRANSIT`.
    *   **Observe (As Regulator):** The Python simulator will now start sending temperature data. Switch MetaMask to your Regulator account and go to the "Regulator" tab. You will see the shipment card and timeline populate with real-time data.
    *   **Deliver (As Logistics & Pharmacy):** Continue the workflow by having the Logistics user transfer to the Pharmacy, and the Pharmacy user finally "Mark as Delivered".

## Project Structure

├── contracts/
│ └── PharmaChain.sol # The main Solidity smart contract
├── explorer/
│ ├── public/
│ ├── src/
│ │ ├── components/ # React components for each dashboard
│ │ ├── services/ # Blockchain interaction logic (Ethers.js)
│ │ └── App.js # Main application component with routing
│ └── .env # Frontend environment variables
├── simulator/
│ ├── app.py # The Python IoT device simulator
│ └── config.yaml # Configuration for the simulator
├── .env # Simulator environment variables
└── README.md # This file

code
Code
download
content_copy
expand_less
## Future Work

*   **Decentralized Storage:** Integrate IPFS for storing product "birth certificates" and other documents, linking the hash on-chain.
*   **Notifications:** Implement a system to notify users (e.g., via email or push notification) when an action is required, such as confirming a pickup.
*   **Advanced Analytics:** Build more complex charts and analytics on the Regulator dashboard to visualize data across all shipments.