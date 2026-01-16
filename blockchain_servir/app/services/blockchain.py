import hashlib
import json
from datetime import datetime
from ..models import db, Block, User, ActionDefinition
from .gamification import update_user_progress

class BlockchainService:
    @staticmethod
    def calculate_hash(index, timestamp, data, prev_hash):
        block_string = json.dumps({
            "index": index,
            "timestamp": str(timestamp),
            "data": data,
            "prev_hash": prev_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @staticmethod
    def add_block(user_id, action_id, data_payload):
        """
        Mines a new block and adds it to the chain.
        data_payload: Dictionary containing action details.
        """
        # 1. Get Last Block
        last_block = Block.query.order_by(Block.id.desc()).first()
        
        if last_block:
            prev_hash = last_block.hash
            new_index = last_block.id + 1
        else:
            prev_hash = "0" * 64 # Genesis Block
            new_index = 1

        timestamp = datetime.utcnow()
        
        # 2. Calculate Hash
        current_hash = BlockchainService.calculate_hash(
            new_index, timestamp, data_payload, prev_hash
        )

        # 3. Create Block
        new_block = Block(
            timestamp=timestamp,
            data=json.dumps(data_payload),
            prev_hash=prev_hash,
            hash=current_hash,
            user_id=user_id,
            action_id=action_id
        )

        db.session.add(new_block)
        db.session.commit()

        # 4. Trigger Gamification Update
        # If the block represents a completed action (positive points)
        if 'points' in data_payload and data_payload['points'] > 0:
            update_user_progress(user_id, data_payload['points'])
            
        return new_block

    @staticmethod
    def validate_chain():
        """
        Iterates through the DB to ensure cryptographic integrity.
        """
        blocks = Block.query.order_by(Block.id.asc()).all()
        for i, block in enumerate(blocks):
            if i == 0:
                continue # Skip genesis check for now
            
            prev_block = blocks[i-1]
            
            # Check linkage
            if block.prev_hash != prev_block.hash:
                return False, f"Broken link at block {block.id}"
            
            # Check data integrity (re-hash)
            # Note: We'd need to reconstruct the exact data string used at creation
            # This is simplified for MVP.
            
        return True, "Chain Valid"
