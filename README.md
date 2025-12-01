# PhotonDB (in-memory)

A database in pure Python. Zero dependencies, maximum simplicity.

## What is it?

PhotonDB is a IN-MEMORY DB written by me from scratch in Python. It is Perfect for learning how databases work, rapid prototyping, or using as a local cache without complications.

## Features

- ✅ String: SET, GET, INCR, APPEND, DEL
- ✅ List: LPUSH, RPUSH, LPOP, RPOP, LRANGE
- ✅ Hash: HSET, HGET, HGETALL, HDEL
- ✅ TTL and automatic expiration
- ✅ RDB persistence (disk snapshots)
- ✅ Multi-client TCP (with SELECT loop)
- ✅ Zero external dependencies

## Installation

```bash
git clone https://github.com/yourusername/photondb.git
cd photondb
python src/run.py
```

Server starts on `localhost:6379`.

## Quick Usage

```bash
telnet localhost 6379
```

```
SET name alice
OK
GET name
alice
LPUSH tasks "task1" "task2"
2
LRANGE tasks 0 -1
task2
task1
```

## Performance

| Operation | Time | Throughput |
|-----------|------|-----------|
| SET 1M | 1.71 sec | 583K ops/sec |
| GET 1M | 1.00 sec | 1M ops/sec |
| SAVE 1M | 15.22 sec | 65K keys/sec |


## Structure

```
photondb/
├── src/
│   ├── benchmark.py     # 1M test
│   ├── photondb.py      # Core database
│   ├── server.py        # TCP server
│   ├── commands.py      # Command executor
│   ├── persistence.py   # RDB snapshots
│   ├── parser.py        # ASCII parser
│   ├── value.py         # Value wrapper
│   └── main.py           # Entry point
├── data/                # Snapshots
├── README.md
├── LICENSE (MIT)
└── requirements.txt
```

## Supported Commands

**String**: `SET`, `GET`, `INCR`, `APPEND`, `DEL`, `EXPIRE`

**List**: `LPUSH`, `RPUSH`, `LPOP`, `RPOP`, `LRANGE`, `LSIZE`

**Hash**: `HSET`, `HGET`, `HGETALL`, `HDEL`

**Server**: `PING`, `DBSIZE`, `FLUSHDB`, `KEYS`

## How it Works

- **In-memory**: Python dict for O(1) access
- **SELECT multiplexing**: handles 1000+ concurrent clients
- **TTL with min-heap**: efficient expiration O(log n)
- **RDB snapshot**: auto-saves every 30s
- **Background thread**: persistence without blocking the server

## Contributing

1. Fork the repo
2. Create a branch (`git checkout -b feature/awesome`)
3. Commit (`git commit -m 'Add awesome'`)
4. Push (`git push origin feature/awesome`)
5. Open a PR

## License

MIT - Use, modify, distribute freely.

## Next Steps

- RESP Protocol (redis-cli compatibility)
- Eviction policies (LRU/LFU)
- New support for more data types and structures
- Clustering
- Upgrade the TCP server
- increase the efficiency of benchmarks
---

**Made with ❤️ by edo**
