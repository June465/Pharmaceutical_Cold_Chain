// src/components/BlockViewer.tsx (Ethers v6 Compatible)

import React, { useState, useEffect } from 'react';
import { ethers, Block } from 'ethers'; // Import Block type for clarity

interface BlockViewerProps {
  provider: ethers.BrowserProvider; // Use BrowserProvider type
}

export const BlockViewer: React.FC<BlockViewerProps> = ({ provider }) => {
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [pendingTx, setPendingTx] = useState<string[]>([]);

  useEffect(() => {
    const fetchBlocks = async () => {
      try {
        const blockNumber = await provider.getBlockNumber();
        const blockPromises = [];
        for (let i = 0; i < 5 && blockNumber - i >= 0; i++) {
          blockPromises.push(provider.getBlock(blockNumber - i));
        }
        const resolvedBlocks = await Promise.all(blockPromises);
        // Filter out any null blocks that might occur in a race condition
        setBlocks(resolvedBlocks.filter((b): b is Block => b !== null));
      } catch (e) {
        console.error("Error fetching blocks:", e);
      }
    };

    fetchBlocks();
    const blockInterval = setInterval(fetchBlocks, 10000);

    provider.on('block', fetchBlocks);

    const pendingListener = (tx: ethers.TransactionResponse) => {
      setPendingTx(prev => [tx.hash, ...prev.slice(0, 4)]);
    };
    // In Ethers v6, the 'pending' event provides the full transaction object
    provider.on('pending', pendingListener);

    return () => {
      clearInterval(blockInterval);
      provider.off('block', fetchBlocks);
      provider.off('pending', pendingListener);
    };
  }, [provider]);

  return (
    <div className="w-full bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold mb-4 text-blue-300">Blockchain Explorer</h2>
      
      <div className="mb-6">
        <h3 className="text-xl font-medium text-yellow-300 mb-2">Pending Transactions (Mempool)</h3>
        {pendingTx.length > 0 ? (
          <ul className="list-disc pl-5 space-y-1">
            {pendingTx.map(hash => (
              <li key={hash} className="font-mono text-gray-400 text-sm truncate">
                {hash}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-400">Listening for new transactions...</p>
        )}
      </div>

      <div>
        <h3 className="text-xl font-medium text-purple-300 mb-2">Latest Blocks</h3>
        <div className="space-y-4">
          {blocks.map(block => (
            <div key={block.hash} className="bg-gray-700 p-3 rounded-md border border-gray-600">
              <p><strong>Block #{block.number}</strong></p>
              <p className="text-sm"><strong>Hash:</strong> <span className="font-mono text-gray-400 break-all">{block.hash}</span></p>
              <p className="text-sm"><strong>Transactions:</strong> {block.transactions.length}</p>
              <p className="text-sm"><strong>Mined On:</strong> {new Date(block.timestamp * 1000).toLocaleString()}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};