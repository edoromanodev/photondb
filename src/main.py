

import sys
import os


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import PhotonDBServer

if __name__ == "__main__":
    server = PhotonDBServer()
    server.start()
