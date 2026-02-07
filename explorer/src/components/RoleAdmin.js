import { useState } from "react";
import { getSignerContract, ROLE } from "../services/blockchain";
import { ethers } from "ethers";

export default function RoleAdmin() {
    const [selectedRole, setSelectedRole] = useState("MANUFACTURER_ROLE");
    const [address, setAddress] = useState("");
    const [status, setStatus] = useState("");

    const handleGrant = async () => {
        if (!ethers.isAddress(address)) { alert("Please enter a valid Ethereum address."); return; }
        setStatus(`Granting ${selectedRole}...`);
        try {
            const contract = await getSignerContract();
            const roleBytes = ethers.id(ROLE[selectedRole]);
            const tx = await contract.grantRoleTo(roleBytes, address);
            await tx.wait();
            setStatus(`Role ${selectedRole} granted to ${address.substring(0,6)}...`);
        } catch (e) { setStatus(`Error: ${e.reason || e.message}`); }
    };

    const handleRevoke = async () => {
        if (!ethers.isAddress(address)) { alert("Please enter a valid Ethereum address."); return; }
        setStatus(`Revoking ${selectedRole}...`);
        try {
            const contract = await getSignerContract();
            const roleBytes = ethers.id(ROLE[selectedRole]);
            const tx = await contract.revokeRoleFrom(roleBytes, address);
            await tx.wait();
            setStatus(`Role ${selectedRole} revoked from ${address.substring(0,6)}...`);
        } catch (e) { setStatus(`Error: ${e.reason || e.message}`); }
    };

    return (
        <section className="panel">
            <h3>Role Admin (Regulator)</h3>
            <div className="field-group-horizontal">
                <select value={selectedRole} onChange={e => setSelectedRole(e.target.value)}>
                    {Object.keys(ROLE).map(role => <option key={role} value={role}>{role}</option>)}
                </select>
                <input value={address} onChange={e => setAddress(e.target.value)} placeholder="0x... address" style={{flex: 1}} />
                <button onClick={handleGrant} className="button-primary">Grant</button>
                <button onClick={handleRevoke}>Revoke</button>
            </div>
            {status && <p className="status-text">{status}</p>}
        </section>
    );
}