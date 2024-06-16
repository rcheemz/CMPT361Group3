import unittest
import socket
import json
import threading
import time

from server import server

class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Setting up the test")
        # Start the server in a new thread
        cls.server_thread = threading.Thread(target=server)
        cls.server_thread.daemon = True  # Set the thread as a daemon thread
        print("Starting the server thread")
        cls.server_thread.start()
        time.sleep(1)

        # Create a client socket that uses IPv4 and TCP protocols
        print("Creating the client socket")
        cls.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cls.clientSocket.settimeout(1.0)  # Set a timeout of 1 second

        # Connect to the server
        print("Connecting to the server")
        cls.clientSocket.connect(('localhost', 13000))
        print("Connected to the server")

        print("Finished setting up the test")

    @classmethod
    def tearDownClass(cls):
        print("Tearing down the test")
        # Close the client socket
        cls.clientSocket.close()
        # Stop the server thread after tests complete
        cls.server_thread.join(timeout=1)  # Wait for 1 second
        if cls.server_thread.is_alive():
            print("Server thread did not finish within the timeout period.")
        else:
            print("Server thread finished successfully.")
        print("Finished tearing down the test")

    def test_dummy(self):
        print("Dummy test running")
        self.assertEqual(1, 1)

    def recv_line(sock):
        chars = []
        while True:
            char = sock.recv(1).decode()
            if char == '\n':
                return ''.join(chars)
            chars.append(char)

    def test_login(self):
        print("Starting the test")
        # Load user credentials
        with open('user_pass.json', 'r') as f:
            credentials = json.load(f)
        username, password = list(credentials.items())[0]

        while True:
            try:
                print("Waiting for a message from the server")
                raw_message = self.clientSocket.recv(2048).decode()
                print(f"Client received raw: '{raw_message}'")
                message = raw_message.strip()
                print(f"Client received after stripping: '{message}'")
                if message.lower() == "enter your username:":
                    self.clientSocket.send((username + '\n').encode())
                    print(f"Client: Sent username: {username}", flush=True)
                elif message.lower() == "enter your password:":
                    self.clientSocket.send((password + '\n').encode())
                    print(f"Client: Sent password: {password}", flush=True)
                    # Receive the symmetric key from the server
                    sym_key = self.clientSocket.recv(32)
                    print(f"Client: Received symmetric key: {sym_key.hex()}") # REMOVE THIS LATER BAD BAD BAD
                    break
                elif message == "Authentication successful.\n":
                    print("Client: Authentication successful.")
                elif message == "":
                    print("Client: Received an empty message from the server.")
                    break
                else:
                    print(f"Client: Received an unexpected message from the server: '{message}'")
                    break
            except socket.timeout:
                print("Socket timed out")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

        # Send the shutdown command before closing the socket
        shutdown_command = "4"  # The option to terminate the connection
        self.clientSocket.send((shutdown_command + '\n').encode())
        # Close the client socket
        print("Closing the client socket")
        self.clientSocket.close()
        print("Finished the test")

if __name__ == "__main__":
    unittest.main()




