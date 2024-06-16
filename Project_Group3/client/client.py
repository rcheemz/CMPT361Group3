'''
CMPT 361 Project
Spring 2024

Shadr Baaba
Rimneet Cheema
Jamie McDonald

client.py
'''

import socket
import os
import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import pad, unpad

def load_server_public_key():
    with open("server_public.pem", "rb") as f:
        server_public_key = RSA.import_key(f.read())
    return server_public_key

def load_client_private_key(username):
    with open(os.path.join(f"client_{username}", f"{username}_private.pem"), "rb") as f:
        client_private_key = RSA.import_key(f.read())
    return client_private_key

def encrypt_credentials(username, password, public_key):
    cipher = PKCS1_OAEP.new(public_key)
    credentials = f"{username},{password}".encode()
    encrypted_credentials = cipher.encrypt(credentials)
    return encrypted_credentials

def rsa_decrypt_message(encrypted_message, private_key):
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_message = cipher.decrypt(encrypted_message)
    return decrypted_message

def aes_ecb_encrypt(message, key):
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(pad(message, AES.block_size))
    return ciphertext

def aes_ecb_decrypt(ciphertext, key):
    cipher = AES.new(key, AES.MODE_ECB)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext


def client():
    server_ip = input("Enter server name: ")


    #authentication process
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    
    #Load the server's public key
    server_public_key = load_server_public_key()
    
    #Encrypt the credentials
    encrypted_credentials = encrypt_credentials(username, password, server_public_key)
    
    #Create a socket and connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, 13000))    

    #send the encrypted credentials to the server
    client_socket.send(encrypted_credentials)

    response = client_socket.recv(1024).decode()
    print(response)
    
    if "Invalid" in response:
        print(response)
        client_socket.close()
        return

    #menu loop
    if response == "Authentication successful.\n":
        #receive the encrypted key from the server
        enc_sym_key = client_socket.recv(2048)
        print(f"Client: Encrypted message length received: {len(enc_sym_key)}")  #debugging line
        
        #load the client's private key
        client_private_key = RSA.import_key(open(f"client_{username}/{username}_private.pem").read())

        #decrypt the sym key
        sym_key = rsa_decrypt_message(enc_sym_key, client_private_key)
        print(f"Client: Received encrypted symmetric key: {enc_sym_key.hex()}")
        

        #send "OK" message to the server
        ok_message = "OK"
        encrypted_ok_message = aes_ecb_encrypt(ok_message.encode(), sym_key)
        client_socket.send(encrypted_ok_message)
        
        while True:
            encrypted_menu = client_socket.recv(2048)
            menu = aes_ecb_decrypt(encrypted_menu, sym_key).decode().strip()
            print(menu)
            print("")
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
    '''
    #prompt for recipients
    encrypted_prompt = client_socket.recv(2048)
    prompt = aes_ecb_decrypt(encrypted_prompt, sym_key).decode()
    print(prompt, end='') 
    to = input()
    encrypted_to = aes_ecb_encrypt(to.encode(), sym_key)
    client_socket.send(encrypted_to)
    
    
    #prompt for title
    encrypted_prompt = client_socket.recv(2048)
    prompt = aes_ecb_decrypt(encrypted_prompt, sym_key).decode()
    print(prompt, end='')  
    title = input()
    encrypted_title = aes_ecb_encrypt(title.encode(), sym_key)
    client_socket.send(encrypted_title)
    
    #prompt for message content
    encrypted_prompt = client_socket.recv(2048)
    prompt = aes_ecb_decrypt(encrypted_prompt, sym_key).decode()
    print(prompt, end='')  
    content = input()
    encrypted_content = aes_ecb_encrypt(content.encode(), sym_key)
    client_socket.send(encrypted_content)
    
    encrypted_response = client_socket.recv(2048)
    response = aes_ecb_decrypt(encrypted_response, sym_key).decode().strip()
    print(response)

def view_inbox(client_socket, sym_key):
    '''
    This function will handle the view inbox operation for client
    '''
    encrypted_response = client_socket.recv(4096)
    response = aes_ecb_decrypt(encrypted_response, sym_key).decode().strip()
    print(response)

def view_email(client_socket, sym_key):
    '''
    This function will handle the view email operation for client
    '''
    #prompt for which email to view
    encrypted_prompt = client_socket.recv(2048)
    prompt = aes_ecb_decrypt(encrypted_prompt, sym_key).decode()
    print(prompt, end='') 
    email_index = input()
    
    #while the input is not a number keep prompting for index
    while not email_index.isdigit():
        print("Invalid input. Please enter a number.")
        email_index = input()
    
    encrypted_email_index = aes_ecb_encrypt(email_index.encode(), sym_key)
    client_socket.send(encrypted_email_index)

    encrypted_response = client_socket.recv(4096)
    response = aes_ecb_decrypt(encrypted_response, sym_key).decode().strip()
    print(response)
    



#-------------
if __name__ == "__main__":
    client()