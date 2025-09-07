import argparse
import threading
import time
from services.socket_client import create_client
from core.logging import logger


def input_thread(client):
    while client.connected:
        try:
            message = input()
            if message.strip():
                if message.lower() in ['/quit', '/exit', '/q']:
                    client.disconnect()
                    break
                elif message.lower() == '/ping':
                    client.ping()
                else:
                    client.send_message(message)
        except EOFError:
            break
        except Exception as e:
            logger.error(f"Error in input thread: {e}")
            break


def main():
    parser = argparse.ArgumentParser(description="TSPO Socket Client")
    parser.add_argument("--host", required=True, help="Server host IP address")
    parser.add_argument("--port", type=int, default=8888, help="Server port")
    parser.add_argument("--room", default="general", help="Room to join")
    parser.add_argument("--sender", required=True, help="Your name")
    
    args = parser.parse_args()
    
    logger.info(f"Connecting to {args.host}:{args.port} as {args.sender} in room {args.room}")
    
    client = create_client(
        server_host=args.host,
        server_port=args.port,
        room=args.room,
        sender=args.sender
    )
    
    if not client.connect():
        logger.error("Failed to connect to server")
        return
    
    print(f"\nConnected to chat server!")
    print(f"You're in room: {args.room}")
    print(f"Your name: {args.sender}")
    print(f"Type your messages and press Enter to send")
    print(f"Type '/ping' to test connection")
    print(f"Type '/quit' to exit")
    print(f"{'='*50}\n")
    
    input_t = threading.Thread(target=input_thread, args=(client,), daemon=True)
    input_t.start()
    
    try:
        while client.connected:
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    
    client.disconnect()
    print("\nDisconnected from chat server")


if __name__ == "__main__":
    main()
