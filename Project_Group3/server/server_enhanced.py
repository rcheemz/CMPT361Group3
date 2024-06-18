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
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def load_server_private_key():
    '''
    this function will open and read the server public key
    that is in the client folder
    '''
    with open("server_private.pem", "rb") as f:
        server_private_key = RSA.import_key(f.read())
    return server_private_key

def load_client_public_key(username):
    '''
    this function will open and read the specific clients private key
    from their client folder
    '''
    with open(os.path.join("keys", f"{username}_public.pem"), "rb") as f:
        client_public_key = RSA.import_key(f.read())
    return client_public_key

def rsa_encrypt_message(message, public_key):
    '''
    this function will encrypt using RSA
    public key encryption
    
    parameters:
    message (str)
    public_key (RSA key): The RSA public key used to encrypt the credentials
    
    return: the encrytped message as bytes
    '''
    cipher = PKCS1_OAEP.new(public_key)
    encrypted_message = cipher.encrypt(message)
    return encrypted_message

def rsa_decrypt_message(encrypted_message, private_key):
    '''
    this function will decrypt an RSA encrypted message using private key
    
    parameters:
    encrypted_message (bytes): the encrypted message to be decrypted
    private_key (RSA key): the RSA private key used to decrypt the message
    
    return: the decrypted message as string
    '''
    #initalize a cipher object using "PKCS1_0AEP" and private key
    cipher = PKCS1_OAEP.new(private_key)
    #decrypt using cipher object
    decrypted_message = cipher.decrypt(encrypted_message)
    return decrypted_message    


def decrypt_credentials(encrypted_credentials, private_key):
    '''
    this function will decrypt an RSA encrypted message using private key
    
    parameters:
    encrypted_credentials (bytes): the encrypted message to be decrypted
    private_key (RSA key): the RSA private key used to decrypt the message
    
    return: the decrypted username and password as string
    '''
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_credentials = cipher.decrypt(encrypted_credentials)
    username, password = decrypted_credentials.decode().split(',')
    return username, password


def generate_symmetric_key():
    '''
    this function will generate sym key for AES encryption
    return symmetric key
    '''    
    return get_random_bytes(32)  # 32 bytes * 8 = 256 bits

def aes_ecb_encrypt(message, key):
    '''
    this function will encrpyt a message using AES encryption in ECB mode
    
    parameters:
    message (string): the plaintext message to be encrypted
    key (bytes): the key used for AES encryption

    returns:the encrypted message (ciphertext) in bytes
    '''   
    #initalize an AES cipher object in ECB mode with key
    cipher = AES.new(key, AES.MODE_ECB)
    #pad message and ecrypt using cipher object
    ciphertext = cipher.encrypt(pad(message, AES.block_size))
    return ciphertext

def aes_ecb_decrypt(ciphertext, key):
    '''
    this function will decrpyt a message using AES encryption in ECB mode
    
    parameters:
    ciphertext (string): the encrypted message to be decrpyted
    key (bytes): the key used for AES encryption

    returns: plaintext (string)
    '''     
    #initalize an AES cipher object in ECB mode with key
    cipher = AES.new(key, AES.MODE_ECB)
    #decrypt using cipher object and then unpad message
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext

def server():
    '''
    this is the main function for the server
    '''    
    #server port
    serverPort = 13000


    #load user credentials
    with open('user_pass.json', 'r') as f:
        credentials = json.load(f)
   

    # Create server socket that uses IPv4 and TCP protocols
    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print('Server: Error in server socket creation:', e)
        sys.exit(1)

    # Associate 13000 port number to the server socket
    try:
        
        serverSocket.bind(('', serverPort))

    except socket.error as e:
        print('Server: Error in server socket binding:', e)
        sys.exit(1)

    print('The server is ready to accept connections')

    # The server can only have one connection in its queue waiting for acceptance
    serverSocket.listen(5)

    while True:
        try:
            # Server accepts client connection
            connectionSocket, addr = serverSocket.accept()
            pid = os.fork()  

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
        #server recieves encrypted credentials from client
        encrypted_credentials = connectionSocket.recv(2048)
        #load server private key
        server_private_key = load_server_private_key()
        #decrypt username and password
        username, password = decrypt_credentials(encrypted_credentials, server_private_key)

        
        #check if the username is one of the users from the json database and the password matches
        if username in users and users[username] == password:
            connectionSocket.send(b"Authentication successful.\n")
            
            #load client's public key
            client_public_key = load_client_public_key(username)
            
            # Generate a symmetric key
            sym_key = generate_symmetric_key()

                        
            #encrypt the symmetric key with the client's public key
            rsa_encrypted_sym_key = rsa_encrypt_message(sym_key, client_public_key)
            print(f"Connection Accepted and Symmetric Key Generated for client: {username}")
            
            #send the encrypted message to the client
            connectionSocket.send(rsa_encrypted_sym_key)          
            
            #receive the "OK" message from the client
            encrypted_ok_message = connectionSocket.recv(2048)
            print(f"encrypted_ok_message = {encrypted_ok_message}")
            signature = connectionSocket.recv(256)
            print(f"sign = {signature}")
            hash_obj = SHA256.new(encrypted_ok_message)
            pkcs1_15.new(client_public_key).verify(hash_obj, signature)
            ok_message = aes_ecb_decrypt(encrypted_ok_message, sym_key).decode()
            print(f"ok = {ok_message}")
            
            if ok_message == "OK":
                menu = '''Select the operation:
         1) Create and send an email
         2) Display the inbox list
         3) Display the email contents
         4) Terminate the connection'''
            
                      
                
                #loop for menu
                while True:
                    
                    #encrypt menu and send
                    encrypted_menu = aes_ecb_encrypt(menu.encode(), sym_key)
                    connectionSocket.send(encrypted_menu) 
                    
                    #recieve choice and decrypt
                    encrypted_choice = connectionSocket.recv(2048)
                    choice = aes_ecb_decrypt(encrypted_choice, sym_key).decode().strip()
                    
                    if choice == "1":
                        #call send email funtion
                        send_email(connectionSocket, username, sym_key)
                    elif choice == "2":
                        #call view inbox funtion
                        view_inbox(connectionSocket, username, sym_key)
                    elif choice == "3":
                        #call view_email function
                        view_email(connectionSocket, username, sym_key)
                    elif choice == "4":
                        connectionSocket.send(aes_ecb_encrypt(b"Connection terminated.", sym_key))
                        print(f"Terminating connection with {username}")
                        break
                    else:
                        connectionSocket.send(aes_ecb_encrypt(b"Invalid choice. Try again.", sym_key))
            else:
                #if ok message was not correct and hashing with sign didnt work then this is a man in the mdiddle attack
                connectionSocket.send("Invalid")
                connectionSocket.close()
        
        #else not autorized user
        else:
            
            connectionSocket.send(b"Invalid username or password")
            print(f"The received client information: {username} is invalid (Connection Terminated).")
    
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        connectionSocket.close()



def send_email(connectionSocket, sender, sym_key):
    '''
    This function will save the email from the client to corresponding recipents 
    folder in their JSON database
    parameters(the connetion socket, the user sending the email)
    '''
    
    #prompt user for email information using encyrption
    connectionSocket.send(aes_ecb_encrypt(b"Enter recipient(s) (separated by ;): ", sym_key))
    recipients = aes_ecb_decrypt(connectionSocket.recv(2048), sym_key).decode().strip().split(';')
    connectionSocket.send(aes_ecb_encrypt(b"Enter title: ", sym_key))
    title = aes_ecb_decrypt(connectionSocket.recv(2048), sym_key).decode().strip()
    connectionSocket.send(aes_ecb_encrypt(b"Enter message contents: ", sym_key))
    content = aes_ecb_decrypt(connectionSocket.recv(2048), sym_key).decode().strip()
    
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
        recipient_folder = os.path.join(recipient)
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

    connectionSocket.send(aes_ecb_encrypt(b"Email sent successfully.", sym_key))
    print(f"An email from {sender} is sent to {recipients} has a content length of {len(email['content'])}")  



def view_inbox(connectionSocket, username, sym_key):
    '''
    This function will show the contents of saved email in clients JSON database
    parameters(the connetion socket, autorized username from json database, key)
    '''
    
    #find inbox folder for client if none then just say no emails found
    inbox_folder = os.path.join(username)
    if not os.path.exists(inbox_folder):
        print("Inbox folder does not exist.")
        connectionSocket.send(aes_ecb_encrypt(b"Inbox is empty.", sym_key))
        return
    
    #find emails in database if none say no emails found
    emails = os.listdir(inbox_folder)
    if not emails:
        connectionSocket.send(aes_ecb_encrypt(b"No emails found.", sym_key))
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
    
    #send encrytped email list
    encrypted_email_list = aes_ecb_encrypt(email_list.encode(), sym_key)
    connectionSocket.send(encrypted_email_list) 
    
    

def view_email(connectionSocket, username, sym_key):
    '''
    This function will show you the content of the emails
    parameters(the connetion socket, autorized username from json database, key)
    '''
    #prompt user for index of email they want to view
    prompt = "Enter email index to view: "
    connectionSocket.send(aes_ecb_encrypt(pad(prompt.encode(), AES.block_size), sym_key))
    encrypted_email_index = connectionSocket.recv(2048)
    email_index = aes_ecb_decrypt(encrypted_email_index, sym_key).decode().strip()

    
    if not email_index.isdigit():
        error_message = "Invalid email index"
        connectionSocket.send(aes_ecb_encrypt(pad(error_message.encode(), AES.block_size), sym_key))
        return
    
    email_index = int(email_index) - 1
    
    #go to client folder 
    inbox_folder = os.path.join(username)
    emails = os.listdir(inbox_folder)
    
    if email_index < 0 or email_index >= len(emails):
        connectionSocket.send(aes_ecb_encrypt(b"Invalid email index.", sym_key))
        connectionSocket.close()
        return
    
    #find email and open file and read and send content to user
    email_file = os.path.join(inbox_folder, emails[email_index])
    
    #open and read and encrpyt email then send to client
    with open(email_file, "r") as f:
        email_content = f.read()
    connectionSocket.send(aes_ecb_encrypt(email_content.encode(), sym_key))
    
#---------------------

if __name__ == "__main__":
    server()

