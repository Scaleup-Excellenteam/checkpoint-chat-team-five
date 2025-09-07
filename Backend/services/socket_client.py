import socket
import json
import threading
import time
from datetime import datetime
from typing import Optional, Callable
from core.logging import logger
from schemas.socket import SocketMessage, SocketMessageType, SocketClientConfig


class SocketClient:
    """Python socket client for real-time chat"""
    
    def __init__(self, config: SocketClientConfig):
        self.config = config
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.running = False
        self.message_handler: Optional[Callable[[SocketMessage], None]] = None
        self.receive_thread: Optional[threading.Thread] = None
        
        logger.info(f"Socket client initialized: {config.server_host}:{config.server_port}")
    
    def connect(self) -> bool:
        """Connect to the socket server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.config.timeout)
            
            self.socket.connect((self.config.server_host, self.config.server_port))
            self.connected = True
            self.running = True
            
            logger.info(f"Connected to server {self.config.server_host}:{self.config.server_port}")
            
            # Start receiving messages in a separate thread
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()
            
            # Join the room
            self.join_room()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                # Send leave message
                self.leave_room()
            except:
                pass
            
            self.socket.close()
            self.socket = None
        
        logger.info("Disconnected from server")
    
    def join_room(self):
        """Join the configured room"""
        if not self.connected:
            logger.error("Not connected to server")
            return
        
        join_msg = SocketMessage(
            type=SocketMessageType.JOIN,
            room=self.config.room,
            sender=self.config.sender,
            content=f"Joining room {self.config.room}"
        )
        
        self._send_message(join_msg)
        logger.info(f"Joined room {self.config.room} as {self.config.sender}")
    
    def leave_room(self):
        """Leave the current room"""
        if not self.connected:
            return
        
        leave_msg = SocketMessage(
            type=SocketMessageType.LEAVE,
            room=self.config.room,
            sender=self.config.sender,
            content=f"Leaving room {self.config.room}"
        )
        
        self._send_message(leave_msg)
        logger.info(f"Left room {self.config.room}")
    
    def send_message(self, content: str):
        """Send a chat message"""
        if not self.connected:
            logger.error("Not connected to server")
            return
        
        chat_msg = SocketMessage(
            type=SocketMessageType.CHAT,
            room=self.config.room,
            sender=self.config.sender,
            content=content,
            timestamp=datetime.utcnow()
        )
        
        self._send_message(chat_msg)
        logger.info(f"Sent message: {content}")
    
    def ping(self):
        """Send a ping to the server"""
        if not self.connected:
            return
        
        ping_msg = SocketMessage(
            type=SocketMessageType.PING,
            room="system",
            sender=self.config.sender,
            content="ping"
        )
        
        self._send_message(ping_msg)
    
    def set_message_handler(self, handler: Callable[[SocketMessage], None]):
        """Set a function to handle incoming messages"""
        self.message_handler = handler
    
    def _send_message(self, message: SocketMessage):
        """Send a message to the server"""
        try:
            data = json.dumps(message.dict(), default=str).encode('utf-8')
            self.socket.send(data)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.connected = False
    
    def _receive_messages(self):
        """Receive messages from the server"""
        while self.running and self.connected:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                
                message_data = json.loads(data.decode('utf-8'))
                message = SocketMessage(**message_data)
                
                # Handle the message
                if self.message_handler:
                    self.message_handler(message)
                else:
                    self._default_message_handler(message)
                    
            except json.JSONDecodeError:
                logger.warning("Received invalid JSON from server")
            except Exception as e:
                if self.running:
                    logger.error(f"Error receiving message: {e}")
                break
        
        self.connected = False
        logger.info("Stopped receiving messages")
    
    def _default_message_handler(self, message: SocketMessage):
        """Default message handler"""
        timestamp = message.timestamp.strftime("%H:%M:%S") if message.timestamp else "??:??:??"
        
        if message.type == SocketMessageType.CHAT:
            if message.sender == "server":
                print(f"[{timestamp}] 🖥️  {message.content}")
            else:
                print(f"[{timestamp}] {message.sender}: {message.content}")
        elif message.type == SocketMessageType.ERROR:
            print(f"[{timestamp}] ❌ Error: {message.content}")
        elif message.type == SocketMessageType.PONG:
            print(f"[{timestamp}] 🏓 Pong received")
        else:
            print(f"[{timestamp}] 📨 {message.type}: {message.content}")


def create_client(server_host: str, server_port: int, room: str, sender: str) -> SocketClient:
    """Create a socket client with the given configuration"""
    config = SocketClientConfig(
        server_host=server_host,
        server_port=server_port,
        room=room,
        sender=sender
    )
    return SocketClient(config)
