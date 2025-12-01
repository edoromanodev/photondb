"""
Benchmark module for PhotonDB.

Origin:
    Generated with LLM assistance and reviewed for correctness.

Purpose:
    Run reproducible performance tests (SET, GET, SAVE) on 1M keys.


"""


import time
from photondb import PhotonDB
from commands import CommandExecutor


def benchmark_set_1m():
    """SET di 1M chiavi"""
    db = PhotonDB()
    executor = CommandExecutor(db)
    
    start = time.time()
    for i in range(1_000_000):
        executor.execute(["SET", f"key:{i}", f"value:{i}"])
    
    elapsed = time.time() - start
    print(f"SET 1M keys: {elapsed:.2f} sec ({1_000_000/elapsed:,.0f} ops/sec)")


def benchmark_get_1m():
    """GET di 1M chiavi"""
    db = PhotonDB()
    executor = CommandExecutor(db)
    
    # Popola
    for i in range(1_000_000):
        executor.execute(["SET", f"key:{i}", f"value:{i}"])
    
    start = time.time()
    for i in range(1_000_000):
        result = executor.execute(["GET", f"key:{i}"])
    
    elapsed = time.time() - start
    print(f"GET 1M keys: {elapsed:.2f} sec ({1_000_000/elapsed:,.0f} ops/sec)")


def benchmark_persistence():
    """SAVE di 1M chiavi"""
    db = PhotonDB()
    executor = CommandExecutor(db)
    
    # Popola
    print("Populating DB with 1M keys...")
    for i in range(1_000_000):
        executor.execute(["SET", f"key:{i}", f"value:{i}"])

    
  
    start = time.time()
    db.persistence.save_snapshot(db)
    elapsed = time.time() - start
    print(f"SAVE 1M keys: {elapsed:.2f} sec")


if __name__ == "__main__":
    print("PhotonDB Benchmark Suite\n")
    benchmark_set_1m()
    benchmark_get_1m()
    benchmark_persistence()
    print("\nBenchmark completed for 1M\n.")
