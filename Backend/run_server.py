import argparse
import signal
import sys
import time
from core.logging import logger
from services.socket_service import SocketServer
import uvicorn


def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


def start_socket_server(host, port):
    server = SocketServer(host=host, port=port)
    if server.start():
        logger.info(f"Socket server started on {host}:{port}")
        return server
    else:
        logger.error(f"Failed to start socket server on {host}:{port}")
        return None


def start_api_server(host, port, debug=False):
    logger.info(f"Starting FastAPI server on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=debug, log_level="info")


def main():
    parser = argparse.ArgumentParser(description="TSPO Chat Backend Runner")
    parser.add_argument("--mode", choices=["api", "socket", "both"], default="api",
                       help="Server mode to run")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port for API server")
    parser.add_argument("--socket-port", type=int, default=8888, help="Port for socket server")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info(f"Starting TSPO Chat Backend in {args.mode} mode")
    
    if args.mode == "api":
        start_api_server(args.host, args.port, args.debug)
    elif args.mode == "socket":
        server = start_socket_server(args.host, args.socket_port)
        if server:
            try:
                while server.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
            finally:
                server.stop()
    elif args.mode == "both":
        socket_server = start_socket_server(args.host, args.socket_port)
        if socket_server:
            start_api_server(args.host, args.port, args.debug)
        else:
            logger.error("Failed to start socket server, exiting")
            sys.exit(1)


if __name__ == "__main__":
    main()
