import argparse
import requests
import time


def test_health(host, port):
    print("Testing health endpoint...")
    try:
        response = requests.get(f"http://{host}:{port}/health/")
        if response.status_code == 200:
            data = response.json()
            print(f"Health check passed: {data['status']}")
            print(f"  - Uptime: {data['uptime_seconds']:.2f}s")
            print(f"  - Rooms: {data['room_count']}")
            print(f"  - Messages: {data['message_count']}")
            return True
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Health check error: {e}")
        return False


def test_send_message(host, port):
    print("\nTesting send message...")
    try:
        message_data = {
            "room": "test-room",
            "content": "Hello from API test!",
            "sender": "test-user"
        }
        
        response = requests.post(
            f"http://{host}:{port}/messages/",
            json=message_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Message sent successfully!")
            print(f"  - Message ID: {data['id']}")
            print(f"  - Room: {data['room']}")
            print(f"  - Sender: {data['sender']}")
            return data['id']
        else:
            print(f"Send message failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Send message error: {e}")
        return None


def test_get_messages(host, port):
    print("\nTesting get messages...")
    try:
        response = requests.get(f"http://{host}:{port}/messages/?room=test-room&limit=10")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Get messages successful!")
            print(f"  - Total messages: {data['total']}")
            print(f"  - Has more: {data['has_more']}")
            return True
        else:
            print(f"Get messages failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Get messages error: {e}")
        return False


def test_socket_status(host, port):
    print("\nTesting socket server status...")
    try:
        response = requests.get(f"http://{host}:{port}/socket/status")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Socket server status retrieved!")
            print(f"  - Running: {data['running']}")
            print(f"  - Host: {data['host']}")
            print(f"  - Port: {data['port']}")
            return True
        else:
            print(f"Socket status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Socket status error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="TSPO Chat API Test")
    parser.add_argument("--host", default="localhost", help="API host")
    parser.add_argument("--port", type=int, default=8000, help="API port")
    
    args = parser.parse_args()
    
    print(f"Testing TSPO Chat API at {args.host}:{args.port}")
    print("=" * 50)
    
    time.sleep(2)
    
    tests_passed = 0
    total_tests = 4
    
    if test_health(args.host, args.port):
        tests_passed += 1
    
    message_id = test_send_message(args.host, args.port)
    if message_id:
        tests_passed += 1
    
    if test_get_messages(args.host, args.port):
        tests_passed += 1
    
    if test_socket_status(args.host, args.port):
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("All tests passed! Your TSPO Chat API is working correctly.")
    else:
        print("Some tests failed. Check the server logs for more details.")


if __name__ == "__main__":
    main()
