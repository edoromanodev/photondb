"""
Persistence Layer: save and load the dump from disk
"""

import json
import os
from datetime import datetime
from typing import Dict, Any


class PersistenceManager:
    
    def __init__(self, data_dir: str = "data"):
        """
        Args:
            data_dir (str): folder of RDB dump
        """
        
        self.data_dir = data_dir
        self.rdb_path = os.path.join(data_dir, "dump.rdb")
        
        """
            1. check if the folder exists
            2. if not, create it
            3. print the confirm message

        
        """
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"📁 Created data directory: {data_dir}")
    
    def save_snapshot(self, photon_db) -> bool:
        """
        save a snapshot of db on the disk
        
        Args:
            photon_db: instance of PhotonDB
        
        Returns:
            bool: True if it works
        """
        
        try:

            """ open file in write"""
          
            snapshot_data = self._serialize_db(photon_db)
            
     
            with open(self.rdb_path, 'w') as f:
                json.dump(snapshot_data, f, indent=2)
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"✓ Database snapshot saved at {timestamp}")
            print(f"  File: {self.rdb_path}")
            print(f"  Keys: {len(photon_db.data)}")
            
            return True
        
        except Exception as e:
            print(f"✗ Error saving snapshot: {e}")
            return False
    
    def load_snapshot(self, photon_db) -> bool:
        """
       load a snapshot from the disk
        
        Args:
            photon_db: isntnce of PhotonDB
        
        Returns:
            bool: True if it works
        """
        
        if not os.path.exists(self.rdb_path):
            print(f"ℹ No snapshot found at {self.rdb_path}")
            return False
        
        try:
            with open(self.rdb_path, 'r') as f:
                snapshot_data = json.load(f)
            
            # Ricrea il database
            self._deserialize_db(photon_db, snapshot_data)
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"✓ Database snapshot loaded at {timestamp}")
            print(f"  File: {self.rdb_path}")
            print(f"  Keys: {len(photon_db.data)}")
            
            return True
        
        except Exception as e:
            print(f"✗ Error loading snapshot: {e}")
            return False
    
    def _serialize_db(self, photon_db) -> Dict[str, Any]:
        """
        convert PhotonDB in a serializable dict
        
        PhotonDB in RAM:
        {
            "key1": value(data="Alice", type="string", ttl_ms=None),
            "key2": value(data=["a", "b"], type="list", ttl_ms=1234567),
        }
        
        we convert it in JSON:
        {
            "key1": {
                "data": "Alice",
                "type": "string",
                "ttl_ms": None,
                "created_at": 1234567890
            },
            ...
        }
        """
        
        serialized = {}
        
        for key, value in photon_db.data.items():
            serialized[key] = {
                "data": value.data,
                "type": value.type,
                "ttl_ms": value.ttl_ms,
                "created_at": value.created_at,
                "last_accessed": value.last_accessed,
                "access_count": value.access_count,
            }
        
        return {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "keys": serialized
        }
    
    def _deserialize_db(self, photon_db, snapshot_data: Dict[str, Any]):
        from value import value  # ← Classe
        
        photon_db.data.clear()
        photon_db.expiry_heap.clear()
        
        keys_data = snapshot_data.get("keys", {})
        
        for key, val_data in keys_data.items():  # ← val_data, NON value_data
            redis_value = value(
                data=val_data["data"],
                type_=val_data["type"]
            )
            
            redis_value.ttl_ms = val_data.get("ttl_ms")
            redis_value.created_at = val_data.get("created_at", 0)
            redis_value.last_accessed = val_data.get("last_accessed", 0)
            redis_value.access_count = val_data.get("access_count", 0)
            
            photon_db.data[key] = redis_value
            
            if redis_value.ttl_ms is not None:
                import heapq

                heapq.heappush(photon_db.expiry_heap, (redis_value.ttl_ms, key))
