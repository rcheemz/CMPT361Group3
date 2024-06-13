'''
CMPT 361 Project
Shadr Baaba
Rimneet Cheema
Jamie McDonald
This program will generate key pairs for the server and clients
'''

from Crypto.PublicKey import RSA
import os

#initialize directory to store keys
key_dir = "keys"
#if there is no directory named key_dir that exists
if not os.path.exists(key_dir):
    #then make the directory 
    os.makedirs(key_dir)

#generate server keys, 2048 bit key pairs
server_key = RSA.generate(2048)

#counstructs the path for servers public key file, opens file in write binary mode
#the writes the servers public key to the file in PEM format
with open(os.path.join(key_dir, "server_public.pem"), "wb") as f:
    f.write(server_key.publickey().export_key("PEM"))
 
#counstructs the path for servers private key file, opens file in write binary mode
#the writes the servers private key to the file in PEM format    
with open(os.path.join(key_dir, "server_private.pem"), "wb") as f:
    f.write(server_key.export_key("PEM"))


#make a list contain the names of the clients
clients = ["client1", "client2", "client3", "client4", "client5"]

#loop over each client 
for client in clients:
    #generate keys for each client, 048 bit key pairs
    client_key = RSA.generate(2048)
    
    #counstructs the path for client public key file, opens file in write binary mode
    #the writes the clients public key to the file in PEM format    
    with open(os.path.join(key_dir, f"{client}_public.pem"), "wb") as f:
        f.write(client_key.publickey().export_key("PEM"))
    
    #counstructs the path for client public key file, opens file in write binary mode
    #the writes the client public key to the file in PEM format    
    with open(os.path.join(key_dir, f"{client}_private.pem"), "wb") as f:
        f.write(client_key.export_key("PEM"))