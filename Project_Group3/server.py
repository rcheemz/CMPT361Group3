'''
CMPT 361 Project
Spring 2024

Shadr Baaba
Rimneet Cheema
Jamie McDonald

server.py
'''

import socket
import os
import json

def server():
    # Server port
    serverPort = 13000

    # Load user credentials
    with open('user_pass.json', 'r') as f:
        credentials = json.load(f)

    # Create server socket that uses IPv4 and TCP protocols
    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print('Error in server socket creation:', e)
        sys.exit(1)

    # Associate 12000 port number to the server socket
    try:
        serverSocket.bind(('', serverPort))
    except socket.error as e:
        print('Error in server socket binding:', e)
        sys.exit(1)

    print('The server is ready to accept connections')

    # The server can only have one connection in its queue waiting for acceptance
    serverSocket.listen(5)

    while True:
        try:
            # Server accepts client connection
            connectionSocket, addr = serverSocket.accept()
            print(addr, '   ', connectionSocket)
            pid = os.fork()  # implement forking method from lab 7 to create multiple connections 

            # If it is a client process
            if pid == 0:

                # serverSocket.close()

                # Load the key
                key = load_key('key') # need our key file sort out later

                # Server sends an encrypted welcoming message to the client
                print("Server is about to send a welcoming message...")
                welcome_message = "Welcome to the mail server."
                encrypted_welcome_message = encrypt_message(welcome_message, key)
                send_message(connectionSocket, encrypted_welcome_message)
                print("Server has sent the welcoming message.")

                # Server sends an encrypted message asking for the client's username and password
                print("Server is about to send a username/password prompt...")
                user_pass_prompt = "Please enter your username and password:"
                encrypted_user_pass_prompt = encrypt_message(user_pass_prompt, key)
                send_message(connectionSocket, encrypted_user_pass_prompt)
                print("Server has sent the username/password prompt.")

                # Server receives client's username and password, decrypts it and checks it
                encrypted_user_pass = receive_message(connectionSocket)
                client_user_pass = decrypt_message(encrypted_user_pass, key)

                # Check if the client's username and password are valid
                if client_user_pass in credentials:
                    # The client's username and password are valid
                    # Continue with the rest of the protocol...
                else:
                    # The client's username and password are invalid
                    # Send an error message and terminate the connection
               
                return

            # Parent doesn't need this connection
            connectionSocket.close()

        except socket.error as e:
            print('An error occurred:', e)
            serverSocket.close()
            sys.exit(1)
        except:
            print('Goodbye')
            serverSocket.close()
            sys.exit(0)

#--------------------------
server()