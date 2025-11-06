import React, { useState } from 'react';
import { httpProvider } from '../services/blockchain';
import { isHexString } from 'ethers';

export default function BlockInspector() {
  const [blockInput, setBlockInput] = useState('latest');
  const [block, setBlock] = useState(null);
  const [loadingBlock, setLoadingBlock] = useState(false);

  const [txHash, setTxHash] = useState('');
  const [tx, setTx] = useState(null);
  const [loadingTx, setLoadingTx] = useState(false);

  async function fetchBlock() {
    try {
      setLoadingBlock(true);
      setBlock(null);
      const target = blockInput.trim().toLowerCase() === 'latest' ? 'latest' : Number(blockInput);
      // Fetch the block WITH its transaction hashes
      const blk = await httpProvider.getBlock(target);
      setBlock(blk || null);
    } catch (e) { console.error('fetchBlock error:', e); } 
    finally { setLoadingBlock(false); }
  }

  async function fetchTx() {
    try {
      setLoadingTx(true);
      setTx(null);
      const h = txHash.trim();
      if (!isHexString(h, 32)) { alert('Please paste a valid 0x… transaction hash'); setLoadingTx(false); return; }
      const [transaction, receipt] = await Promise.all([
        httpProvider.getTransaction(h),
        httpProvider.getTransactionReceipt(h)
      ]);
      setTx({ transaction, receipt });
    } catch (e) { console.error('fetchTx error:', e); } 
    finally { setLoadingTx(false); }
  }

  return (
    <section className="panel">
      <h3 style={{ marginTop: 0 }}>Chain Inspector</h3>
      
      {/* Block lookup */}
      <div className="field-group-horizontal">
        <input
          value={blockInput}
          onChange={(e) => setBlockInput(e.target.value)}
          placeholder="latest or a block number"
          style={{ flex: 1 }}
        />
        <button onClick={fetchBlock} disabled={loadingBlock}>
          {loadingBlock ? 'Loading…' : 'Fetch Block'}
        </button>
      </div>

      {block && (
        <div className="status-text" style={{ wordBreak: 'break-all', fontFamily: 'monospace', marginTop: 16 }}>
          <p><strong>Block Details</strong></p>
          <div><strong>Number:</strong> <a href={`https://sepolia.etherscan.io/block/${block.number}`} target="_blank" rel="noreferrer">{block.number}</a></div>
          <div><strong>Hash:</strong> {block.hash}</div>
          <div><strong>Parent Hash:</strong> {block.parentHash}</div>
          <div><strong>Timestamp:</strong> {new Date(block.timestamp * 1000).toLocaleString()}</div>
          <div><strong>Transactions:</strong> {block.transactions.length}</div>
          <hr style={{borderColor: '#415a77', margin: '8px 0'}}/>
          <p><strong>Merkle-Patricia Trie Roots:</strong></p>
          <div><strong>transactionsRoot:</strong> {block.transactionsRoot}</div>
          <div><strong>receiptsRoot:</strong> {block.receiptsRoot}</div>
          <div><strong>stateRoot:</strong> {block.stateRoot}</div>
        <hr style={{borderColor: '#415a77', margin: '8px 0'}}/>
          <p><strong>Transactions in this Block (first 10):</strong></p>
          {block.transactions.length > 0 ? (
            <ul style={{paddingLeft: '20px', margin: 0}}>
              {block.transactions.slice(0, 10).map(hash => (
                <li key={hash}>{hash}</li>
              ))}
            </ul>
          ) : (
            <p>No transactions in this block.</p>
          )}
        </div>
      )}
      
      {/* Transaction lookup */}
      <div className="field-group-horizontal" style={{ marginTop: 16 }}>
        <input
          value={txHash}
          onChange={(e) => setTxHash(e.target.value)}
          placeholder="0x… transaction hash"
          style={{ flex: 1 }}
        />
        <button onClick={fetchTx} disabled={loadingTx}>
          {loadingTx ? 'Loading…' : 'Lookup Tx'}
        </button>
      </div>

      {tx && (
        <div className="status-text" style={{ wordBreak: 'break-all', fontFamily: 'monospace', marginTop: 16 }}>
            <p><strong>Transaction Details</strong></p>
            {tx.transaction && <div><strong>Hash:</strong> <a href={`https://sepolia.etherscan.io/tx/${tx.transaction.hash}`} target="_blank" rel="noreferrer">{tx.transaction.hash}</a></div>}
            {tx.transaction && <div><strong>From:</strong> {tx.transaction.from}</div>}
            {tx.transaction && <div><strong>To:</strong> {tx.transaction.to}</div>}
            {tx.receipt && <div><strong>Status:</strong> {tx.receipt.status === 1 ? 'Success' : 'Failed'}</div>}
            {tx.receipt && <div><strong>Block:</strong> {tx.receipt.blockNumber}</div>}
            {tx.receipt && <div><strong>Gas Used:</strong> {tx.receipt.gasUsed.toString()}</div>}
        </div>
      )}
    </section>
  );
}