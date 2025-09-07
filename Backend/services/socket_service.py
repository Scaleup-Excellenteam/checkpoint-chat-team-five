import socket
import threading
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set
from core.logging import logger
from core.config import settings
from schemas.socket import SocketMessage, SocketMessageType, SocketConnection, SocketServerStatus


class SocketServer:
    """Python socket server for real-time chat"""
    
    def __init__(self, host: str = None, port: int = None):
        self.host = host or settings.SOCKET_HOST
        self.port = port or settings.SOCKET_PORT
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        self.connections: Dict[str, SocketConnection] = {}
        self.room_connections: Dict[str, Set[str]] = {}  # room -> set of client_ids
        self.lock = threading.RLock()
        self.start_time = time.time()
        self.total_connections = 0
        
        logger.info(f"Socket server initialized: {self.host}:{self.port}")
    
    def start(self) -> bool:
        """Start the socket server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(settings.SOCKET_MAX_CONNECTIONS)
            
            self.running = True
            logger.info(f"Socket server started on {self.host}:{self.port}")
            
            # Start accepting connections in a separate thread
            accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            accept_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start socket server: {e}")
            self.running = False
            return False
    
    def stop(self):
        """Stop the socket server"""
        with self.lock:
            self.running = False
            
            # Close all connections
            for client_id in list(self.connections.keys()):
                self._disconnect_client(client_id)
            
            # Close server socket
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
            
            logger.info("Socket server stopped")
    
    def _accept_connections(self):
        """Accept incoming connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                client_id = str(uuid.uuid4())
                
                logger.info(f"New connection from {address}: {client_id}")
                
                # Handle client in a separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_id, address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    logger.error(f"Error accepting connection: {e}")
                break
    
    def _handle_client(self, client_socket: socket.socket, client_id: str, address):
        """Handle a client connection"""
        try:
            # Send welcome message
            welcome_msg = SocketMessage(
                type=SocketMessageType.CHAT,
                room="system",
                sender="server",
                content=f"Welcome! Your client ID is {client_id}"
            )
            self._send_message(client_socket, welcome_msg)
            
            while self.running:
                try:
                    # Receive message
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    # Parse message
                    message_data = json.loads(data.decode('utf-8'))
                    message = SocketMessage(**message_data)
                    
                    # Handle different message types
                    if message.type == SocketMessageType.JOIN:
                        self._handle_join(client_socket, client_id, message)
                    elif message.type == SocketMessageType.CHAT:
                        self._handle_chat(client_socket, client_id, message)
                    elif message.type == SocketMessageType.PING:
                        self._handle_ping(client_socket, client_id)
                    elif message.type == SocketMessageType.LEAVE:
                        self._handle_leave(client_socket, client_id, message)
                    
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from client {client_id}")
                    self._send_error(client_socket, "Invalid message format")
                except Exception as e:
                    logger.error(f"Error handling message from {client_id}: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            self._disconnect_client(client_id)
            client_socket.close()
    
    def _handle_join(self, client_socket: socket.socket, client_id: str, message: SocketMessage):
        """Handle join room message"""
        with self.lock:
            # Create connection record
            self.connections[client_id] = SocketConnection(
                client_id=client_id,
                room=message.room,
                sender=message.sender,
                connected_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            
            # Add to room
            if message.room not in self.room_connections:
                self.room_connections[message.room] = set()
            self.room_connections[message.room].add(client_id)
            
            self.total_connections += 1
            
            # Send join confirmation
            join_msg = SocketMessage(
                type=SocketMessageType.CHAT,
                room=message.room,
                sender="server",
                content=f"{message.sender} joined the room"
            )
            self._broadcast_to_room(message.room, join_msg, exclude_client=client_id)
            
            logger.info(f"Client {client_id} joined room {message.room} as {message.sender}")
    
    def _handle_chat(self, client_socket: socket.socket, client_id: str, message: SocketMessage):
        """Handle chat message"""
        with self.lock:
            if client_id not in self.connections:
                self._send_error(client_socket, "Not connected to any room")
                return
            
            connection = self.connections[client_id]
            connection.last_activity = datetime.utcnow()
            
            # Update sender from connection
            message.sender = connection.sender
            message.timestamp = datetime.utcnow()
            
            # Broadcast to room
            self._broadcast_to_room(connection.room, message)
            
            logger.info(f"Chat message from {connection.sender} in room {connection.room}")
    
    def _handle_ping(self, client_socket: socket.socket, client_id: str):
        """Handle ping message"""
        pong_msg = SocketMessage(
            type=SocketMessageType.PONG,
            room="system",
            sender="server",
            content="pong"
        )
        self._send_message(client_socket, pong_msg)
    
    def _handle_leave(self, client_socket: socket.socket, client_id: str, message: SocketMessage):
        """Handle leave room message"""
        with self.lock:
            if client_id in self.connections:
                connection = self.connections[client_id]
                
                # Send leave notification
                leave_msg = SocketMessage(
                    type=SocketMessageType.CHAT,
                    room=connection.room,
                    sender="server",
                    content=f"{connection.sender} left the room"
                )
                self._broadcast_to_room(connection.room, leave_msg, exclude_client=client_id)
                
                self._disconnect_client(client_id)
                
                logger.info(f"Client {client_id} left room {connection.room}")
    
    def _disconnect_client(self, client_id: str):
        """Disconnect a client"""
        with self.lock:
            if client_id in self.connections:
                connection = self.connections[client_id]
                
                # Remove from room
                if connection.room in self.room_connections:
                    self.room_connections[connection.room].discard(client_id)
                    if not self.room_connections[connection.room]:
                        del self.room_connections[connection.room]
                
                # Remove connection
                del self.connections[client_id]
                
                logger.info(f"Client {client_id} disconnected")
    
    def _send_message(self, client_socket: socket.socket, message: SocketMessage):
        """Send a message to a client socket"""
        try:
            data = json.dumps(message.dict(), default=str).encode('utf-8')
            client_socket.send(data)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    def _send_error(self, client_socket: socket.socket, error_message: str):
        """Send an error message to a client"""
        error_msg = SocketMessage(
            type=SocketMessageType.ERROR,
            room="system",
            sender="server",
            content=error_message
        )
        self._send_message(client_socket, error_msg)
    
    def _broadcast_to_room(self, room: str, message: SocketMessage, exclude_client: str = None):
        """Broadcast a message to all clients in a room"""
        with self.lock:
            if room in self.room_connections:
                for client_id in self.room_connections[room]:
                    if client_id != exclude_client and client_id in self.connections:
                        # In a real implementation, you'd need to store client sockets
                        # For now, we'll just log the broadcast
                        logger.info(f"Broadcasting to {client_id}: {message.content}")
    
    def get_status(self) -> SocketServerStatus:
        """Get server status"""
        with self.lock:
            return SocketServerStatus(
                running=self.running,
                port=self.port,
                host=self.host,
                active_connections=len(self.connections),
                total_connections=self.total_connections,
                uptime_seconds=time.time() - self.start_time
            )


# Global socket server instance
socket_server = SocketServer()
