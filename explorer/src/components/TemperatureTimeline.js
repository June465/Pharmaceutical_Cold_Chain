import React, { useEffect, useMemo, useState } from "react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { httpProvider } from "../services/blockchain";

const toC = (scaled) => Number(scaled) / 100;

export default function TemperatureTimeline({ shipments }) {
  const [data, setData] = useState([]);
  const [details, setDetails] = useState(null); // Holds fetched block/tx info for the clicked point
  const [loadingDetails, setLoadingDetails] = useState(false);

  // Build graph data from the shipments prop
  useEffect(() => {
    const rows = [];
    for (const s of Object.values(shipments || {})) {
      (s.readings || []).forEach(r => {
        rows.push({
          time: r.timestamp,
          tempC: toC(r.temperature),
          txHash: r.txHash,
          blockNumber: r.blockNumber
        });
      });
    }
    rows.sort((a, b) => a.time - b.time);
    setData(rows);
  }, [shipments]);

  // This is your function to fetch deep data when a point is clicked
  const onPointClick = async (state) => {
    const payload = state?.activePayload?.[0]?.payload;
    if (!payload?.txHash || !payload.blockNumber) return;

    setLoadingDetails(true);
    setDetails(null);

    try {
      const { txHash, blockNumber } = payload;
      
      const [block, prevBlock, nextBlock] = await Promise.all([
        httpProvider.getBlock(blockNumber),
        httpProvider.getBlock(blockNumber - 1).catch(() => null),
        httpProvider.getBlock(blockNumber + 1).catch(() => null),
      ]);

      setDetails({
        ...payload,
        block,
        prev: prevBlock,
        next: nextBlock,
      });
    } catch (e) {
      console.error("Error fetching point details:", e);
    } finally {
      setLoadingDetails(false);
    }
  };
  
  const chartData = useMemo(() => 
    data.map(d => ({ ...d, label: new Date(d.time).toLocaleTimeString() })), 
    [data]
  );

  return (
    <div style={{ margin: "24px 0", padding: 16, borderRadius: 12, background: "#0d1b2a", border: "1px solid #1b263b", color: "#e0e1dd" }}>
      <h3 style={{ margin: 0, marginBottom: 16 }}>Temperature Timeline</h3>
      {chartData.length === 0 && <p>No temperature events yet.</p>}
      {chartData.length > 0 && (
        <div style={{ width: '100%', height: 320 }}>
          <ResponsiveContainer width="99%" height="100%">
            <LineChart data={chartData} onClick={onPointClick} style={{ cursor: 'pointer' }}>
              <CartesianGrid stroke="#1b263b" strokeDasharray="3 3" />
              <XAxis dataKey="label" minTickGap={40} />
              <YAxis unit="°C" domain={['dataMin - 1', 'dataMax + 1']} />
              <Tooltip
                contentStyle={{ background: '#0d1b2a', border: '1px solid #415a77' }}
                labelFormatter={(t) => new Date(t).toLocaleString()}
                formatter={(v, n) => n === "tempC" ? [`${v.toFixed(2)} °C`, 'Temperature'] : [v, n]}
              />
              <Line dataKey="tempC" type="monotone" stroke="#66d9e8" dot={{ r: 4 }} activeDot={{ r: 8 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* This is your details panel */}
      {(loadingDetails || details) && (
        <div style={{ marginTop: 16, background: "#1b263b", padding: 12, borderRadius: 8, textAlign: 'left', fontFamily: 'monospace', wordBreak: 'break-all' }}>
          <h3>Point Details</h3>
          {loadingDetails && <p>Loading details from the blockchain...</p>}
          {details?.block && (
            <>
              <p><b>Time:</b> {new Date(details.time).toLocaleString()}</p>
              <p><b>Temp:</b> {details.tempC.toFixed(2)}°C</p>
              <p><b>Tx:</b> <a href={`https://sepolia.etherscan.io/tx/${details.txHash}`} target="_blank" rel="noreferrer">{details.txHash}</a></p>
              <hr style={{borderColor: '#415a77', margin: '8px 0'}} />
              <p><b>Block:</b> #{details.block.number} (<a href={`https://sepolia.etherscan.io/block/${details.block.number}`} target="_blank" rel="noreferrer">{details.block.hash}</a>)</p>
              <p><b>Parent Block:</b> {details.block.parentHash}</p>
              <hr style={{borderColor: '#415a77', margin: '8px 0'}} />
              <p><b>transactionsRoot:</b> {details.block.transactionsRoot}</p>
              <p><b>receiptsRoot:</b> {details.block.receiptsRoot}</p>
              <p><b>stateRoot:</b> {details.block.stateRoot}</p>
              <hr style={{borderColor: '#415a77', margin: '8px 0'}} />
              <p><b>Prev Block:</b> {details.prev ? `#${details.prev.number}` : '—'}</p>
              <p><b>Next Block:</b> {details.next ? `#${details.next.number}` : '—'}</p>
            </>
          )}
        </div>
      )}
    </div>
  );
}