import argparse
import signal
import sys
import time
from services.socket_service import SocketServer
from core.logging import logger


def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down...")
    server.stop()
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="TSPO Socket Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8888, help="Port to bind to")
    
    args = parser.parse_args()
    
    global server
    server = SocketServer(host=args.host, port=args.port)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info(f"Starting socket server on {args.host}:{args.port}")
    
    if server.start():
        logger.info("Server started successfully!")
        try:
            while server.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
    else:
        logger.error("Failed to start server")
        sys.exit(1)
    
    server.stop()
    logger.info("Server stopped")


if __name__ == "__main__":
    main()
