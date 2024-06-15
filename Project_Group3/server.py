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
import sys
from datetime import datetime

from Cryptodome.Random import get_random_bytes

def generate_symmetric_key():
    return get_random_bytes(32)  # 32 bytes * 8 = 256 bits

def server():
    print("Server: Starting the server function")
    # Server port
    serverPort = 13000
    print(f"Server: Server port: {serverPort}")

    # Load user credentials
    with open('user_pass.json', 'r') as f:
        credentials = json.load(f)
    print("Server: Loaded user credentials")

    # Create server socket that uses IPv4 and TCP protocols
    try:
        print("Server: Creating server socket")
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Server: Server socket created successfully")
    except socket.error as e:
        print('Server: Error in server socket creation:', e)
        sys.exit(1)

    # Associate 13000 port number to the server socket
    try:
        print("Server: Binding server socket to port")
        serverSocket.bind(('', serverPort))
        print("Server: Server socket bound successfully")
    except socket.error as e:
        print('Server: Error in server socket binding:', e)
        sys.exit(1)

    print('Server: The server is ready to accept connections')

    # The server can only have one connection in its queue waiting for acceptance
    serverSocket.listen(5)

    while True:
        try:
            # Server accepts client connection
            connectionSocket, addr = serverSocket.accept()
            print(f"Server: Accepted connection from {addr}")
            print(addr, '   ', connectionSocket)
            pid = os.fork()  # implement forking method from lab 7 to create multiple connections 

            # If it is a client process
            if pid == 0:
                serverSocket.close()
                handle_client(connectionSocket, credentials)
                os._exit(0)
            else:
                connectionSocket.close()

        except socket.error as e:
            print('Server: An error occurred:', e)
            serverSocket.close()
            sys.exit(1)
        except:
            print('Server: Goodbye')
            serverSocket.close()
            sys.exit(0)



def handle_client(connectionSocket, users):
    '''
    Handle the client connection
    parameters(the connetion socket, autorized users from json database)
    '''
    
    try:
        #server sends client credentials prompts and recieves/saves them accordingly
        connectionSocket.send(b"Enter your username: ")
        print("Server: Sent username prompt")
        username = connectionSocket.recv(1024).decode().strip()
        print(f"Server: Received username: {username}")
        connectionSocket.send(b"Enter your password: ")
        print("Server: Sent password prompt")
        password = connectionSocket.recv(2048).decode().strip()
        print(f"Server: Received password: {password}")
        
        #check if the username is one of the users from the json database and the password matches
        if username in users and users[username] == password:
            # Generate a 256-bit symmetric key
            sym_key = get_random_bytes(32)
            
            # Send the symmetric key to the client
            connectionSocket.send(sym_key)

            connectionSocket.send(b"Authentication successful.\n")
            menu = '''Select the operation:
     1) Create and send an email
     2) Display the inbox list
     3) Display the email contents
     4) Terminate the connection'''
            
            #loop for menu
            while True:
                
                #send menu and recieve choice
                connectionSocket.send(menu.encode())
                choice = connectionSocket.recv(2048).decode().strip()
                
                if choice == "1":
                    #call send email funtion
                    send_email(connectionSocket, username)
                elif choice == "2":
                    #call view inbox funtion
                    view_inbox(connectionSocket, username)
                elif choice == "3":
                    #call view_email function
                    view_email(connectionSocket, username)
                elif choice == "4":
                    #terminate connection
                    connectionSocket.send(b"Connection terminated.")
                    break
                else:
                    connectionSocket.send(b"Invalid choice. Try again.")
        
        #else not autorized user
        else:
            
            connectionSocket.send(b"Invalid username or password")
            print(f"The received client information: {username} is invalid (Connection Terminated).")
    
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        connectionSocket.close()



def send_email(connectionSocket, sender):
    '''
    This function will save the email from the client to corresponding recipents 
    folder in their JSON database
    parameters(the connetion socket, the user sending the email)
    '''
    
    #prompt user for email information
    connectionSocket.send(b"Enter recipient(s) (separated by ;): ")
    recipients = connectionSocket.recv(2048).decode().strip().split(';')
    connectionSocket.send(b"Enter title: ")
    title = connectionSocket.recv(2048).decode().strip()
    connectionSocket.send(b"Enter message contents: ")
    content = connectionSocket.recv(2048).decode().strip()
    
    #create email 
    email = {
        "from": sender,
        "to": recipients,
        "title": title,
        "content": content,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    #for each recipicent save email to their JSON database
    for recipient in recipients:
        #get path to database, if it doesn't exisit then make it
        recipient_folder = os.path.join("server", recipient)
        if not os.path.exists(recipient_folder):
            os.makedirs(recipient_folder)
        #create the filename and save the email as a text file
        email_file = os.path.join(recipient_folder, f"{sender}_{title}.txt")
        with open(email_file, "w") as f:
            f.write(f"From: {email['from']}\n")
            f.write(f"To: {', '.join(email['to'])}\n")
            f.write(f"Time and Date Received: {email['timestamp']}\n")
            f.write(f"Title: {email['title']}\n")
            f.write(f"Content Length: {len(email['content'])}\n")
            f.write(f"Contents:\n{email['content']}\n")

    connectionSocket.send(b"Email sent successfully.")



def view_inbox(connectionSocket, username):
    '''
    This function will show the contents of saved email in clients JSON database
    parameters(the connetion socket, autorized username from json database)
    '''
    #find inbox folder for client if none then just say no emails found
    inbox_folder = os.path.join("server", username)
    if not os.path.exists(inbox_folder):
        connectionSocket.send(b"No emails found.")
        return
    
    #find emails in database if none say no emails found
    emails = os.listdir(inbox_folder)
    if not emails:
        connectionSocket.send(b"No emails found.")
        return
    
    #display emails 
    email_list = "Index From      DateTime                     Title\n"
    for idx, email in enumerate(emails):
        email_info = email.split('_')
        sender = email_info[0]
        title = email_info[1].split('.')[0]
        email_file = os.path.join(inbox_folder, email)
        timestamp = "N/A"
        with open(email_file, "r") as f:
            for line in f:
                if line.startswith("Time and Date Received: "):
                    timestamp = line[len("Time and Date Received: "):].strip()
                    break
        email_list += f"{idx+1:5} {sender:8} {timestamp:28} {title}\n"
    
    connectionSocket.send(email_list.encode())



def view_email(connectionSocket, username):
    '''
    This function will show you the content of the emails
    parameters(the connetion socket, autorized username from json database)
    '''
    #prompt user for index of email they want to view
    connectionSocket.send(b"Enter email index to view: ")
    email_index = connectionSocket.recv(2048).decode().strip()
    
    if not email_index.isdigit():
        connectionSocket.send(b"Invalid email index. Please enter a number.")
        return
    
    email_index = int(email_index) - 1
    
    #go to client folder 
    inbox_folder = os.path.join("server", username)
    emails = os.listdir(inbox_folder)
    
    if email_index < 0 or email_index >= len(emails):
        connectionSocket.send(b"Invalid email index.")
        return
    
    #find email and open file and read and send content to user
    email_file = os.path.join(inbox_folder, emails[email_index])
    
    with open(email_file, "r") as f:
        email_content = f.read()
    connectionSocket.send(response.encode())
    
#---------------------

if __name__ == "__main__":
    server()
