# src/commands.py
"""
CommandExecutor: Map commands to PhotonDB operations
"""

from photondb import PhotonDB


class CommandExecutor:
    
    def __init__(self, db: PhotonDB):
        self.db = db
    
    def execute(self, cmd: list[str]):
        """
            Execute a command
            
            Args:
                cmd (list[str]): Parsed command, e.g. ["GET", "mykey"]
            
            Returns:
                Command result
        """
        
        if not cmd:
            raise ValueError("\nempty command\n")
        
        command_name = cmd[0].upper()
        args = cmd[1:]
        
        # =============== STRING COMMANDS ===============
        
        if command_name == "SET":
            if len(args) < 2:
                raise ValueError("SET requires at least 2 arguments: SET key value [EX seconds]")
            
            key = args[0]
            value = args[1]
            ex = None
            
            """
            Optional EX param handling for TTL:
            1. Check if there are at least 4 args and third is "EX"
            2. If yes, set 'ex' to the integer value of the fourth arg
            """


            if len(args) >= 4 and args[2].upper() == "EX":
                ex = int(args[3])
            
            return self.db.set(key, value, ex=ex)
        
        elif command_name == "GET":
            if len(args) != 1:
                raise ValueError("GET requires exactly  1 argument: GET key")
            return self.db.get(args[0])
        
        elif command_name == "DEL":
            if len(args) < 1:
                raise ValueError("DEL requires exaclty 1 argument")
            count = 0
            for key in args:
                if self.db.delete(key):
                    count += 1
            return count
        
        elif command_name == "INCR":
            if len(args) != 1:
                raise ValueError("INCR requires exactly 1 argument: INCR key")
            return self.db.incr(args[0])
        
        # =============== LIST COMMANDS ===============
        
        elif command_name == "LPUSH":
            if len(args) < 2:
                raise ValueError("LPUSH requires at least 2 arguments: LPUSH key value [value...]")
            key = args[0]
            values = args[1:]
            return self.db.lpush(key, *values)
        
        elif command_name == "RPUSH":
            if len(args) < 2:
                raise ValueError("RPUSH requires at least 2 arguments: RPUSH key value [value...]")
            key = args[0]
            values = args[1:]
            return self.db.rpush(key, *values)
        
        elif command_name == "LPOP":
            if len(args) != 1:
                raise ValueError("LPOP requires exactly 1 argument: LPOP key")
            return self.db.lpop(args[0])
        
        elif command_name == "RPOP":
            if len(args) != 1:
                raise ValueError("RPOP requires exactly 1 argument: RPOP key")
            return self.db.rpop(args[0])
        
        elif command_name == "LRANGE":
            if len(args) != 3:
                raise ValueError("LRANGE richiede esattamente 3 argomenti: LRANGE key start stop")
            key = args[0]
            start = int(args[1])
            stop = int(args[2])
            return self.db.lrange(key, start, stop)
        
        elif command_name == "LSIZE":
            if len(args) != 1:
                raise ValueError("LSIZE requires exactly 1 argument: LSIZE key")
            return self.db.lsize(args[0])
        
        # =============== HASH COMMANDS ===============
        
        elif command_name == "HSET":
            if len(args) != 3:
                raise ValueError("HSET richiede esattamente 3 argomenti: HSET key field value")
            return self.db.hset(args[0], args[1], args[2])
        
        elif command_name == "HGET":
            if len(args) != 2:
                raise ValueError("HGET richiede esattamente 2 argomenti: HGET key field")
            return self.db.hget(args[0], args[1])
        
        elif command_name == "HGETALL":
            if len(args) != 1:
                raise ValueError("HGETALL requires exactly 1 argument: HGETALL key")
            return self.db.hgetall(args[0])
        
        elif command_name == "HDEL":
            if len(args) < 2:
                raise ValueError("HDEL requires at least 2 arguments: HDEL key field [field...]")
            key = args[0]
            fields = args[1:]
            return self.db.hdel(key, *fields)
        
        # =============== SERVER COMMANDS ===============
        
        elif command_name == "PING":
            if args:
                return args[0]
            return "PONG"
        
        elif command_name == "DBSIZE":
            return self.db.dbsize()
        
        elif command_name == "FLUSHDB":
            self.db.flushdb()
            return "OK"
        
        elif command_name == "KEYS":
            return self.db.keys()
        
        else:
            raise ValueError(f"\nunknown command: {command_name}\n")
