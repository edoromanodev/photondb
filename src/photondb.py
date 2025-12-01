"""
 in memory db 


"""
from persistence import PersistenceManager
import threading
import time
from typing import Dict, Optional
import heapq

from value import value


class PhotonDB:
    """
        Class representing an in-memory database
        to store key-value pairs with metadata.
    
        Attributes:
            store: Dictionary mapping keys (str) to value objects
        """
    
    
    def __init__(self):  # ← NO parametri host/port!
            self.data: Dict[str, value] = {}
            self.expiry_heap: list[tuple[float, str]] = []
            
            # Persistence
            self.persistence = PersistenceManager(data_dir="data")
            self.persistence.load_snapshot(self)

    # =============== Metodi di gestione per le strighe =============== #


    def set (self, key: str, val_: str, ex: Optional[int] = None) -> bool:
        """
        set KEY value [EX seconds]

        args:
            key (str): key to set
            value (str): value associated to thee key
            ex (Optional[int]): expiry time in seconds (None = no expiry) / opzionale
    
            
            return:
                bool: True if operation succeeded
        
        
        """

        val = value(val_, type_="string")

        if ex is not None:
            expire_ms = int(time.time() * 1000) + ex * 1000
            val.ttl_ms = expire_ms
            heapq.heappush(self.expiry_heap, (expire_ms, key))

        self.data[key] = val
        return True
    


    def get(self, key: str) -> Optional[str]:
        """
        get KEY

        args:
            key (str): key to retrieve
        
        return:
            Optional[str]: value associated with the key or None if absent or expired
        
        """

        value = self.data.get(key)

        #check del valore vuoto o scaduto

        if value is None:
            return None

        if value.is_expired():
            del self.data[key]
            return None

        value.touch()
        return value.data
    

    def delete(self, key: str) -> bool:
        """
        delete KEY

        args:
            key (str): key to deletye
        
        return:
            bool: True if the key was deleted, False if not exist
        
        """

        if key in self.data:
            del self.data[key]
            return True
        
        return False
    


    def exists(self, key: str) -> bool:


        """check if a key exists and is not expired"""


        if key not in self.data:
            return False
        if self.data[key].is_expired():
            del self.data[key]
            return False
        return True
    

    def incr(self, key: str) -> int:
        """ INCR key
        Increments the integer value stored at key by 1.
        If the key does not exist, it is set to 0 before the increment."""

        if key not in self.data or self.data[key].is_expired():
            self.set(key, "1")
            return 1
        

        try:
            current_value = int(self.data[key].data)
            new_value = current_value + 1
            self.set(key, str(new_value))
            return new_value
        except ValueError:
            raise ValueError(f"The value of key {key} is not a valid integer.")
        


    def append(self, key: str, value: str) -> int:
        """ APPEND key value
         Appends a string to the existing value of a key.
    If the key does not exist, it is created with the given value.
        
        return:
            int: the new length of value associated to key
        """

        if key not in self.data or self.data[key].is_expired():
            self.set(key, value)
            return len(value)
        
        current = self.get(key)
        if current is None:
            self.set(key, value)
            return len(value)
        
        new_value = current + value
        self.set(key, new_value)
        return len(new_value)
    

    def expire(self, key: str, seconds: int) -> bool:
        """ EXPIRE key seconds
            Sets a timeout on a key.
        
        args:
            key (str): the key to expire
            seconds (int): expiry time in seconds
        
        return:
            bool: True if expiry was set, False if key does not exist
        """


        if key not in self.data:
            return False
        

        expire_ms = int(time.time() * 1000) + seconds * 1000
        self.data[key].ttl_ms = expire_ms
        heapq.heappush(self.expiry_heap, (expire_ms, key))
        return True
    

    # =============== Metodi di gestione per le liste =============== #
    
    def lpush(self, key: str, *values: str) -> int:
        """ LPUSH key value [value ...]
        Inserts one or more values at the head of the list stored at key.
        If the key does not exist, creates a new list.
        
        return:
            int: The new length of the list.
        """


        if key not in self.data:
            self.data[key] = value([], type_="list")


        else:
            value_obj = self.data[key]
            if value_obj.type != "list":
                raise TypeError(f"The key {key} does not contain a list.")
            


        value_obj = self.data[key]
        for v in values:
            value_obj.data.insert(0, v)



        value_obj.touch()
        return len(value_obj.data)



    def rpush(self, key: str, *values: str) -> int:
        """
        RPUSH key value [value ...]
        Inserts one or more values at the tail of the list stored at key."""


        if key not in self.data:
            self.data[key] = value([], type_="list")
        else:
            value_obj = self.data[key]
            if value_obj.type != "list":
                raise TypeError(f"The key {key} does not contain a list.")
            


        value_obj = self.data[key]
        for v in values:
            value_obj.data.append(v)


        value_obj.touch()
        return len(value_obj.data)



    def lrange(self, key: str, start: int, end: int) -> list[str]:
        """
        LRANGE key start stop
        Returns elements from a list
        """
        
        if key not in self.data:
            return []
        
        value_obj = self.data[key]
        if value_obj.type != "list":
            raise TypeError(f"WRONGTYPE Operation against a key holding the wrong kind of value")
        
        value_obj.touch()
        
        # Handle negative indexes like Redis
        length = len(value_obj.data)
        
        # If start is negative, convert it
        if start < 0:
            start = max(0, length + start)
        
        # If end is negative, convert (but no +1)
        if end < 0:
            end = length + end
        
        # Do the slice
        return value_obj.data[start:end+1]




    def lpop(self, key: str) -> Optional[str]:
        """
        LPOP key
        Removes and returns the first element of the list stored at key.
        """


        if key not in self.data:
            return None
        
        value_obj = self.data[key]
        if value_obj.type != "list":
            raise TypeError(f"The key {key} does not contain a list.")
        
        if len(value_obj.data) == 0:
            del self.data[key]
            return None
        
        value_obj.touch()
        return value_obj.data.pop(0)



    def rpop(self, key: str) -> Optional[str]:
        """
        RPOP key
        Removes and returns the last element of the list stored at key.
        """


        if key not in self.data:
            return None
        
        value_obj = self.data[key]
        if value_obj.type != "list":
            raise TypeError(f"The key {key} does not contain a list.")
        
        if len(value_obj.data) == 0:
            del self.data[key]
            return None


        value_obj.touch()
        return value_obj.data.pop()




    def lsize(self, key: str) -> int:
        """
        LSIZE key
        Returns the length of the list stored at key.
        """


        if key not in self.data:
            return 0
        
        value_obj = self.data[key]
        if value_obj.type != "list":
            raise TypeError(f"The key {key} does not contain a list.")
        
        value_obj.touch()
        return len(value_obj.data)



    # =============== Hash methods =============== #


    def hset(self, key: str, field: str, val_: str) -> int:
        """
        HSET key field value
        Sets a field in a hash."""


        if key not in self.data:
            self.data[key] = value({}, type_="hash")


        else:
            value_obj = self.data[key]
            if value_obj.type != "hash":
                raise TypeError(f"The key {key} does not contain a hash.")
            


        value_obj = self.data[key]
        is_new_field = field not in value_obj.data
        value_obj.data[field] = val_
        value_obj.touch()


        return 1 if is_new_field else 0

    def hget(self, key: str, field: str) -> Optional[str]:
        """
        HGET key field
        Gets a field in a hash.
        """


        if key not in self.data:
            return None
        
        value_obj = self.data[key]
        if value_obj.type != "hash":
            raise TypeError(f"The key {key} does not contain a hash.")
        


        value_obj.touch()
        return value_obj.data.get(field)



    def hgetall(self, key: str) -> Dict[str, str]:
        """
        HGETALL key
        Get all fields in a hash
        """
        if key not in self.data:
            return {}
        
        value_obj = self.data[key]
        if value_obj.type != "hash":
            raise TypeError(f"WRONGTYPE Operation against a key holding the wrong kind of value")
        
        value_obj.touch()
        return dict(value_obj.data)

    def hdel(self, key: str, *fields: str) -> int:
        """
        HDEL key field [field ...]
        Deletes fields from a hash
        """
        if key not in self.data:
            return 0
        
        value_obj = self.data[key]
        if value_obj.type != "hash":
            raise TypeError(f"WRONGTYPE Operation against a key holding the wrong kind of value")
        
        deleted = 0
        for field in fields:
            if field in value_obj.data:
                del value_obj.data[field]
                deleted += 1
        
        value_obj.touch()
        return deleted



    # =============== UTILITY =============== #



    def cleanup_expired_keys(self):
        """
        Removes expired keys from the database.
        Must be called periodically to keep the database clean.
        """


        deleted = 0
        current_time_ms = time.time() * 1000


        while self.expiry_heap:
            expire_time, key = self.expiry_heap


            """Check if the key at the top of the heap has expired."""


            if expire_time > current_time_ms:
                break


            heapq.heappop(self.expiry_heap)


            if key in self.data and self.data[key].is_expired():
                del self.data[key]
                deleted += 1


        return deleted





    def dbsize(self) -> int:


        """Returns the number of active keys in the database."""
        return len(self.data)



    def flushdb(self) -> None:
        """Deletes all keys in the database."""


        try:
            self.data.clear()
            self.expiry_heap.clear()
            return True
        
        except Exception as e:
            print(f"Error during database flush: {e}")
            return False
        


    def keys(self) -> list[str]:
        """Returns a list of all keys in the database."""
        return list(self.data.keys())
