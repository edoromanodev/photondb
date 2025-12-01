"""

questa classe è un wrapper per salvare 
un valore con i suoi metadati come 
tipo di dato, timestamp di creazione,
ultimo accesso, contatore di accessi


"""

import time
from typing import Any, Optional

class value: 
    """
    
    Definition of the value class representing a single value
    with its associated metadata.
    
    Attributes:
        data: The actual value (string, list, dict, etc)
        type_: Logical data type ("string", "list", "hash", "set", "zset")
        created_at: Creation timestamp (ms)
        last_accessed: Timestamp of last access (ms)
        access_count: Number of accesses (for LFU)
        ttl_ms: Expiration timestamp in ms (None = no expiry)
    """



    def __init__ (self, data: Any, type_: str = "string"):  
        self.data = data
        self.type = type_
        self.created_at = int(time.time() * 1000)
        self.last_accessed = self.created_at
        self.access_count = 0
        self.ttl_ms: Optional[float] = None


    def is_expired (self) -> bool:
        """
        check if the value has expired based on TTL
        
        return:
            bool: True if is expired, else FALSE

        """
        if self.ttl_ms is None:
            return False
        
        return time.time() * 1000 > self.ttl_ms
    

    def touch (self):
        """
            Updates access metadata when a value
            is read or modified.
        
        """
        self.last_accessed = int(time.time() * 1000)
        self.access_count += 1







