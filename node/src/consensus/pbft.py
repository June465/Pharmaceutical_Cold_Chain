# node/src/consensus/pbft.py
import threading
from collections import defaultdict
from src.core.block import Block
from src.p2p.gossip import broadcast_message
from src.utils.logger import get_logger

log = get_logger(__name__)
QUORUM_SIZE = 3

class PBFTNode:
    def __init__(self, node_id, blockchain):
        self.node_id = node_id
        self.blockchain = blockchain
        self.state = "IDLE"
        self.current_block = None
        self.prepare_log = defaultdict(set)
        self.commit_log = defaultdict(set)
        self.lock = threading.Lock()

    def start_consensus(self):
        with self.lock:
            if self.node_id != "node1": return False
            txs = self.blockchain.mempool.get_transactions()
            if not txs: return False
            
            last_block = self.blockchain.get_head()
            new_block = Block(index=last_block.header['index'] + 1, prev_hash=last_block.hash, proposer_id=self.node_id, transactions=txs)
            voting_hash = new_block.compute_merkle_root() 

            self.current_block = new_block
            self.state = "PRE-PREPARED"
            self.prepare_log[voting_hash].add(self.node_id)
            self.commit_log[voting_hash].add(self.node_id)

            message = {"type": "PRE-PREPARE", "block": new_block.to_dict(), "sender_id": self.node_id, "voting_hash": voting_hash}
            broadcast_message(message, endpoint="/gossip/consensus")
            log.info(f"Primary ({self.node_id}) sent PRE-PREPARE for block {new_block.header['index']}")
            return True

    def handle_consensus_message(self, message):
        msg_type = message.get("type")
        with self.lock:
            if msg_type == "PRE-PREPARE": self._handle_pre_prepare(message)
            elif msg_type == "PREPARE": self._handle_prepare(message)
            elif msg_type == "COMMIT": self._handle_commit(message)

    def _handle_pre_prepare(self, message):
        if self.state != "IDLE": return
        self.current_block = Block.from_dict(message['block'])
        head = self.blockchain.get_head()
        if self.current_block.header['index'] != head.header['index'] + 1 or self.current_block.header['prevHash'] != head.hash: return

        self.state = "PRE-PREPARED"
        voting_hash = message['voting_hash']
        self.prepare_log[voting_hash].add(self.node_id)
        self.commit_log[voting_hash].add(self.node_id)

        prepare_message = {"type": "PREPARE", "voting_hash": voting_hash, "sender_id": self.node_id}
        broadcast_message(prepare_message, endpoint="/gossip/consensus")
        log.info(f"Replica ({self.node_id}) sent PREPARE for hash {voting_hash[:10]}")

    def _handle_prepare(self, message):
        voting_hash, sender_id = message['voting_hash'], message['sender_id']
        self.prepare_log[voting_hash].add(sender_id)
        
        log.info(f"Node ({self.node_id}) received PREPARE from {sender_id}. Total votes for {voting_hash[:10]}: {len(self.prepare_log[voting_hash])}")
        
        if self.state == "PRE-PREPARED" and len(self.prepare_log[voting_hash]) >= QUORUM_SIZE:
            self.state = "PREPARED"
            commit_message = {"type": "COMMIT", "voting_hash": voting_hash, "sender_id": self.node_id}
            broadcast_message(commit_message, endpoint="/gossip/consensus")
            log.info(f"({self.node_id}) PREPARE Quorum reached. Sent COMMIT.")

    def _handle_commit(self, message):
        voting_hash, sender_id = message['voting_hash'], message['sender_id']
        self.commit_log[voting_hash].add(sender_id)

        log.info(f"Node ({self.node_id}) received COMMIT from {sender_id}. Total votes for {voting_hash[:10]}: {len(self.commit_log[voting_hash])}")

        if self.state == "PREPARED" and len(self.commit_log[voting_hash]) >= QUORUM_SIZE and self.current_block:
            log.info(f"({self.node_id}) COMMIT Quorum Reached! Finalizing block {self.current_block.header['index']}.")
            self.blockchain.add_block(self.current_block)
            self._reset_state()

    def _reset_state(self):
        self.state = "IDLE"
        self.current_block = None
        self.prepare_log.clear()
        self.commit_log.clear()
        log.info(f"({self.node_id}) Consensus state reset to IDLE.")