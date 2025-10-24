# node/src/consensus/pbft.py
import threading
from ..core.block import Block
from ..core.blockchain import Blockchain
from ..p2p.gossip import broadcast_message

F = 1
QUORUM_SIZE = 2 * F + 1

class PBFTState:
    def __init__(self):
        self.lock = threading.Lock()
        self.block_proposal = None
        self.pre_prepare_msg = None
        self.prepares = {}
        self.commits = {}
        self.phase = "IDLE"

    def reset(self):
        with self.lock:
            self.block_proposal = None
            self.pre_prepare_msg = None
            self.prepares.clear()
            self.commits.clear()
            self.phase = "IDLE"
            print("--- Consensus state reset to IDLE ---", flush=True)

class PBFTNode:
    def __init__(self, node_id: str, blockchain: Blockchain):
        self.node_id = node_id
        self.blockchain = blockchain
        self.state = PBFTState()
        self.primary = "node1"

    def is_primary(self) -> bool:
        return self.node_id == self.primary

    def start_consensus(self, block: Block):
        if not self.is_primary(): return

        print(f"--- PRIMARY ({self.node_id}): STARTING CONSENSUS for block {block.header['index']} ---", flush=True)
        self.state.reset()
        self.state.block_proposal = block
        self.state.phase = "PRE-PREPARED"

        message = {
            "type": "PREPREPARE",
            "height": block.header['index'],
            "blockHash": block.hash,
            "blockHeader": block.header,
        }
        broadcast_message(message)
        print(f"PRIMARY ({self.node_id}): Sent PRE-PREPARE.", flush=True)

    def handle_message(self, msg: dict):
        msg_type = msg.get("type")
        print(f"NODE ({self.node_id}): Received message {msg_type} from {msg.get('signer') or msg.get('proposerId')}", flush=True)
        
        handlers = {
            "PREPREPARE": self.handle_pre_prepare,
            "PREPARE": self.handle_prepare,
            "COMMIT": self.handle_commit
        }
        handler = handlers.get(msg_type)
        if handler:
            try:
                handler(msg)
            except Exception as e:
                print(f"❌❌❌ FATAL ERROR in {msg_type} handler on {self.node_id}: {e}", flush=True)

    def handle_pre_prepare(self, msg: dict):
        if self.is_primary(): return
        with self.state.lock:
            if self.state.phase != "IDLE": return
            self.state.pre_prepare_msg = msg
            self.state.phase = "PRE-PREPARED"
        
        prepare_msg = { "type": "PREPARE", "height": msg['height'], "blockHash": msg['blockHash'], "signer": self.node_id }
        self.state.prepares[self.node_id] = prepare_msg # Add own vote
        broadcast_message(prepare_msg)
        print(f"REPLICA ({self.node_id}): Voted PREPARE.", flush=True)

    def handle_prepare(self, msg: dict):
        with self.state.lock:
            if self.state.phase != "PRE-PREPARED": return
            
            signer = msg['signer']
            if signer in self.state.prepares: return
            self.state.prepares[signer] = msg
            print(f"LOG ({self.node_id}): Logged PREPARE from {signer}. Total prepares: {len(self.state.prepares)}.", flush=True)

            if len(self.state.prepares) >= QUORUM_SIZE:
                self.state.phase = "PREPARED"
                commit_msg = { "type": "COMMIT", "height": msg['height'], "blockHash": msg['blockHash'], "signer": self.node_id }
                self.state.commits[self.node_id] = commit_msg # Add own vote
                broadcast_message(commit_msg)
                print(f"NODE ({self.node_id}): PREPARE QUORUM REACHED. Voted COMMIT.", flush=True)

    def handle_commit(self, msg: dict):
        with self.state.lock:
            if self.state.phase != "PREPARED": return
            
            signer = msg['signer']
            if signer in self.state.commits: return
            self.state.commits[signer] = msg
            print(f"LOG ({self.node_id}): Logged COMMIT from {signer}. Total commits: {len(self.state.commits)}.", flush=True)

            if len(self.state.commits) >= QUORUM_SIZE:
                self.state.phase = "COMMITTED"
                block_to_add = None
                if self.is_primary():
                    block_to_add = self.state.block_proposal
                else:
                    header = self.state.pre_prepare_msg['blockHeader']
                    block_to_add = Block(index=header['index'], prev_hash=header['prevHash'],
                                         proposer_id=header['proposerId'], timestamp=header['timestamp'], transactions=[])
                    block_to_add.header['merkleRoot'] = header['merkleRoot']
                    block_to_add.hash = block_to_add.compute_hash()

                if block_to_add and block_to_add.hash == msg['blockHash']:
                    print(f"✅✅✅ SUCCESS ({self.node_id}): COMMIT QUORUM REACHED! COMMITTING BLOCK {block_to_add.header['index']}.", flush=True)
                    self.blockchain.add_block(block_to_add)
                    self.state.reset()
                else:
                    print(f"❌❌❌ CRITICAL ({self.node_id}): Block hash mismatch on COMMIT. Consensus failed.", flush=True)
                    self.state.reset()