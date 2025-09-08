import argparse
import signal
import sys
from core.logging import logger
import uvicorn


def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


def start_api_server(host, port, debug=False):
    logger.info(f"Starting FastAPI server on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=debug, log_level="info")


def main():
    parser = argparse.ArgumentParser(description="TSPO Chat Backend Runner")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port for API server")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Starting TSPO Chat Backend in api mode")
    start_api_server(args.host, args.port, args.debug)


if __name__ == "__main__":
    main()
