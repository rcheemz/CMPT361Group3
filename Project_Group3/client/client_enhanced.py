'''
CMPT 361 Project
Spring 2024

Shadr Baaba
Rimneet Cheema
Jamie McDonald

client.py

This program creates a client that can connect to a server and allow
for secure emailing procols between clients
'''

import socket
import os
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def load_server_public_key():
    '''
    this function will open and read the server public key
    that is in the client folder
    '''
    with open("server_public.pem", "rb") as f:
        server_public_key = RSA.import_key(f.read())
    return server_public_key

def load_client_private_key(username):
    '''
    this function will open and read the specific clients private key
    from their client folder
    '''
    with open(os.path.join(f"client_{username}", f"{username}_private.pem"), "rb") as f:
        client_private_key = RSA.import_key(f.read())
    return client_private_key

def encrypt_credentials(username, password, public_key):
    '''
    this function will encrypt user credentials using RSA
    public key encryption
    
    parameters:
    username (str): the username to be encrypted
    password (str): the password to be encrypted
    public_key (RSA key): The RSA public key used to encrypt the credentials
    
    return: the encrytped credentails as bytes
    '''
    #initalize a cipher object using "PKCS1_0AEP" and public key
    cipher = PKCS1_OAEP.new(public_key)
    #encode string of username and password to bytes
    credentials = f"{username},{password}".encode()
    #encrypt using cipher object
    encrypted_credentials = cipher.encrypt(credentials)
    return encrypted_credentials

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


def client():
    '''
    this is the main function for the client
    '''
    #prompt user for server ip
    server_ip = input("Enter server name: ")


    #prompt user for authentication process
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    
    #load the server's public key
    server_public_key = load_server_public_key()
    
    #encrypt the credentials from client
    encrypted_credentials = encrypt_credentials(username, password, server_public_key)
    
    #Create client socket that useing IPv4 and TCP protocols 
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print('Error in client socket creation:',e)
        sys.exit(1) 
    
    #Connect to the server
    try:
        client_socket.connect((server_ip, 13000))    
    except:
        print('Error in connecting to server.')
        exit(1)    
    
    #send the encrypted credentials to the server
    client_socket.send(encrypted_credentials)
    
    #wait for response and print it
    response = client_socket.recv(1024).decode()
    print(response)
    
    #if invalid credentails close client socket
    if "Invalid" in response:
        print(response)
        client_socket.close()
        return

    
    #if authentication successful
    if response == "Authentication successful.\n":
        
        #receive the encrypted key from the server
        enc_sym_key = client_socket.recv(2048)
        
        #load the client's private key
        client_private_key = RSA.import_key(open(f"client_{username}/{username}_private.pem").read())

        #decrypt the sym key using rsa decrpytion 
        sym_key = rsa_decrypt_message(enc_sym_key, client_private_key)
        
        #debug testing
        #print(f"Client: Received encrypted symmetric key: {enc_sym_key.hex()}")
        

        #send "OK" message using aes encrpyion to the server
        ok_message = "OK"
        encrypted_ok_message = aes_ecb_encrypt(ok_message.encode(), sym_key)
        hash_obj = SHA256.new(encrypted_ok_message)
        signature = pkcs1_15.new(client_private_key).sign(hash_obj)
        print(f"signature made with hashing the signing with client private key = {signature}")
        
        
        client_socket.send(encrypted_ok_message)
        client_socket.send(signature)
        
        
        #menu loop
        while True:
            #recieve encrpyted menu and decrypt it using aes
            encrypted_menu = client_socket.recv(2048)
            
            
            
            menu = aes_ecb_decrypt(encrypted_menu, sym_key).decode().strip()
            
            #either server will send menu if correct user or Invalid
            if "Invalid" in menu:
                print(response)
                client_socket.close()
                return                
            print(menu)
            print("")
            
            #prompt user for choice, encrypt using aes and send to server
            choice = input("         choice: ")
            encrypted_choice = aes_ecb_encrypt(choice.encode(), sym_key)
            client_socket.send(encrypted_choice)
    
            if choice == "1":
                #call function for send email
                send_email(client_socket, sym_key)
                print("")
            elif choice == "2":
                #call function for view inbox
                view_inbox(client_socket, sym_key)
                print("")
            elif choice == "3":
                #call function for view email
                view_email(client_socket, sym_key)
                print("")
            elif choice == "4":
                #terminate connection on client side 
                print("Connection terminated.")
                client_socket.close()
                break
            else:
                print("Invalid choice. Try again.")
    

def send_email(client_socket, sym_key):
    '''
    This function will handle the send email operation for client
    
    parameters: client_socket, sym_key (aes key)
    '''
    #recipients 
    #recieve encrypted response, decrypt using AES and print
    encrypted_prompt = client_socket.recv(2048)
    prompt = aes_ecb_decrypt(encrypted_prompt, sym_key).decode()
    print(prompt, end='') 
    #prompt user for input, encrypt using AES and send to server
    to = input()
    encrypted_to = aes_ecb_encrypt(to.encode(), sym_key)
    client_socket.send(encrypted_to)
    
    
    #title
    #recieve encrypted response, decrypt using AES and print
    encrypted_prompt = client_socket.recv(2048)
    prompt = aes_ecb_decrypt(encrypted_prompt, sym_key).decode()
    print(prompt, end='') 
    #prompt user for input, encrypt using AES and send to server
    title = input()
    encrypted_title = aes_ecb_encrypt(title.encode(), sym_key)
    client_socket.send(encrypted_title)
    
    #message content
    #recieve encrypted response, decrypt using AES and print
    encrypted_prompt = client_socket.recv(2048)
    prompt = aes_ecb_decrypt(encrypted_prompt, sym_key).decode()
    print(prompt, end='')  
    #prompt user for input, encrypt using AES and send to server
    content = input()
    encrypted_content = aes_ecb_encrypt(content.encode(), sym_key)
    client_socket.send(encrypted_content)
    
    #email sent successful
    #recieve encrypted response, decrypt using AES and print
    encrypted_response = client_socket.recv(2048)
    response = aes_ecb_decrypt(encrypted_response, sym_key).decode().strip()
    print(response)

def view_inbox(client_socket, sym_key):
    '''
    This function will handle the view inbox operation for client
    
    parameters: client_socket, sym_key (aes key)
    '''
    #recieve encrypted response, decrypt using AES and print
    encrypted_response = client_socket.recv(4096)
    response = aes_ecb_decrypt(encrypted_response, sym_key).decode()
    print(response)


def view_email(client_socket, sym_key):
    '''
    This function will handle the view email operation for client
    
    parameters: client_socket, sym_key (aes key)
    '''
    
    #which email to view
    #recieve encrypted response, decrypt using AES and print
    encrypted_prompt = client_socket.recv(2048)
    prompt = aes_ecb_decrypt(encrypted_prompt, sym_key).decode()
    print(prompt, end='') 
    #prompt user for input, encrypt using AES and send to server
    email_index = input()
    
    #while the input is not a number keep prompting for index
    while not email_index.isdigit():
        print("Invalid input")
        email_index = input("Please enter a number: ")
       
    #prompt user for input, encrypt using AES and send to server
    encrypted_email_index = aes_ecb_encrypt(email_index.encode(), sym_key)
    client_socket.send(encrypted_email_index)
    
    #recieve encrypted response, decrypt using AES and print
    encrypted_response = client_socket.recv(4096)
    response = aes_ecb_decrypt(encrypted_response, sym_key).decode().strip()
    #if invalid
    if "Invalid" in response:
        print("Not an index, connection terminated")
        client_socket.close()
    
    print(response)
    
    
#-------------
if __name__ == "__main__":
    client()