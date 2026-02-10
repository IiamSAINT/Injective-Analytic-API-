"""
Ninja Service - Activity Analysis and Tagging
"""
from typing import Dict, List, Optional, Any
from collections import defaultdict
import asyncio

from app.services.injective_client import get_injective_client, InjectiveClient

# In-memory "Database" for tags
ADDRESS_TAGS: Dict[str, List[str]] = {
    "inj1...binance": ["CEX", "Binance"],
    "inj1...kucoin": ["CEX", "KuCoin"],
}

class NinjaService:
    """Service for Injective community analysis."""
    
    def __init__(self):
        self.client = get_injective_client()
        self._tags = ADDRESS_TAGS
    
    def get_tags(self, address: str) -> List[str]:
        """Get tags for a specific address."""
        return self._tags.get(address, [])
    
    def add_tag(self, address: str, tag: str) -> None:
        """Add a tag to an address."""
        if address not in self._tags:
            self._tags[address] = []
        if tag not in self._tags[address]:
            self._tags[address].append(tag)
            
    async def get_active_traders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Identify active participants based on recent block transactions.
        (Renamed 'traders' but technically 'active accounts' - includes staking/governance etc)
        """
        # 1. Get latest block
        block = await self.client.get_latest_block()
        if not block:
            return []
            
        try:
            height = int(block.get("header", {}).get("height", 0))
        except ValueError:
            return []
            
        if height == 0:
            return []

        # 2. Fetch Txs for the latest block (and maybe previous one if needed for volume)
        # For speed, just latest block is fine for 'Right Now' activity
        txs = await self.client.get_block_txs(height)
        
        participant_counts = defaultdict(int)
        
        # 3. Aggregate Senders
        for tx in txs:
            # Structure: tx -> body -> messages -> [list] -> sender
            body = tx.get("body", {})
            messages = body.get("messages", [])
            for msg in messages:
                # Most cosmos messages have 'sender', some have 'grantee', 'from_address'
                sender = msg.get("sender") or msg.get("grantee") or msg.get("from_address")
                if sender:
                    participant_counts[sender] += 1

        # 4. Sort and Format
        sorted_participants = sorted(participant_counts.items(), key=lambda x: x[1], reverse=True)
        
        dashboard = []
        for addr, count in sorted_participants[:limit]:
            tags = self.get_tags(addr)
            
            # Simple heuristic score
            dashboard.append({
                "address": addr,
                "volume_24h_est": 0, # Cannot easily estimate dollar volume from raw block txs without price feed
                "transaction_count_recent": count,
                "tags": tags,
                "ninja_score": min(100, count * 10) # 10 points per tx in this block
            })
            
        return dashboard

_ninja_service = NinjaService()

def get_ninja_service() -> NinjaService:
    return _ninja_service
