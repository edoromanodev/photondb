import socket
from parser import AsciiParser, Encoder
from commands import CommandExecutor
from photondb import PhotonDB
import threading

import time

class PhotonDBServer:
    def __init__(self, host: str = '0.0.0.0', port: int = 6379):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}
        
        self.db = PhotonDB()
        self.command_executor = CommandExecutor(self.db)
        
        # ← AGGIUNGI QUESTE RIGHE
        self.save_interval = 30  # Salva ogni 30 secondi
        self.save_thread = None
        self.running = False

    def start(self):
        """create server socket and start SELECT's loop"""
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        print(f"🚀 PhotonDB Server listening on {self.host}:{self.port}")
        print(f"   Auto-save enabled (every {self.save_interval}s)\n")
        
        # ← NUOVO: Avvia il thread di background saving
        self.running = True
        self.save_thread = threading.Thread(
            target=self._background_save_loop,
            daemon=True  # Thread daemon = muore quando main thread muore
        )
        self.save_thread.start()
        
        import select
        
        try:
            while True:
                readable, _, _ = select.select(
                    [self.server_socket] + list(self.clients.keys()),
                    [],
                    [],
                    1.0
                )
                
                for sock in readable:
                    if sock is self.server_socket:
                        self.handle_new_connection()
                    else:
                        self.handle_client_data(sock)
        
        except KeyboardInterrupt:
            print("\n🛑 Server stopping...")
            self.stop()

    def accept_client(self):


        """ ## """
        client_socket, (client_host, client_port) = self.server_socket.accept()

        print(f"✓ Client connected: {client_host}:{client_port}")
    
        return client_socket
    


    def receive_from_client(self, client_socket: socket.socket, buffer_size: int = 4096) -> str:
        """receive data from client's socket"""



        """receive max 4096byte from client"""
        data = client_socket.recv(4096)

        
        """ ## """
        if not data:
            return None
        

        """decode data in UTF8"""
        
        command_text = data.decode('utf-8', errors='ignore')

        return command_text 
    

    def send_to_client(self, client_socket: socket.socket, response: str):
        """send a response to client"""

        response_bytes = response.encode('utf-8')
        client_socket.sendall(response_bytes)

        print(f"→ Sent to client: {response}")   


    def handle_new_connection(self):
        """new conn in"""
        client_socket = self.accept_client()
        self.clients[client_socket] = ""

    def handle_client_data(self, client_socket: socket.socket):
        """receive data from client -> in buffer ##"""
        
        data = self.receive_from_client(client_socket)
        
        if not data:
            print(f"✗ Client disconnected")
            client_socket.close()
            del self.clients[client_socket]
            return
        
        # Accumula nel buffer
        self.clients[client_socket] += data
        
        # ← NUOVO: Processa comandi
        self._process_buffer(client_socket)

    def stop(self):
        """stop the server and close all the connection"""
        
        self.running = False
        
        if self.save_thread and self.save_thread.is_alive():
            self.save_thread.join(timeout=2)
        
        # ← CORRETTO: Passa self.db
        print("\n💾 Final save before shutdown...")
        self.db.persistence.save_snapshot(self.db)
        
        # Chiudi tutti i client
        for sock in list(self.clients.keys()):
            sock.close()
        
        # Chiudi il server socket
        if self.server_socket:
            self.server_socket.close()
        
        print("✓ Server stopped")




    def _process_buffer(self, client_socket: socket.socket):
        """process commands from buffer"""
        
        buffer = self.clients[client_socket]
        
        # Cerca linee complete
        while '\n' in buffer:
            # Separa in modo sicuro
            parts = buffer.split('\n', 1)
            
            if len(parts) != 2:
                break
            
            line = parts[0].strip()
            buffer = parts[1]
            
            if not line:
                continue
            
            self._execute_command(client_socket, line)
        
        self.clients[client_socket] = buffer




    def _execute_command(self, client_socket: socket.socket, command_line: str):
        """parse and exec commands"""
        
        try:
            # Parsa la linea ASCII
            cmd = AsciiParser.parse_ascii_command(command_line)
            
            # Esegui con CommandExecutor
            result = self.command_executor.execute(cmd)
            
            # Formatta la risposta
            response = Encoder.format_response(result)
            
            # Invia al client
            self.send_to_client(client_socket, response + "\n")
        
        except Exception as e:
            error_response = f"ERROR: {str(e)}"
            self.send_to_client(client_socket, error_response+"\n") 



        
    def _background_save_loop(self):
        """thread loop to save db in rdb"""
        
        while self.running:
            try:
                for _ in range(self.save_interval):
                    if not self.running:
                        break
                    import time
                    time.sleep(1)
                
                if self.running:
                   
                    self.db.persistence.save_snapshot(self.db)
            
            except Exception as e:
                print(f"✗ Error in background save: {e}")