'''
CMPT 361 Project
Shadr Baaba
Rimneet Cheema
Jamie McDonald

key_generator.py

This program will generate key pairs for the server and clients and save
them to the corresponding directories
'''

'''
When running this is the folder formatting it follows
server/
├── server_public.pem
├── server_private.pem
├── user_pass.json
├── server.py
├── keys/
≈   ├── client1_public.pem
│   ├── client2_public.pem
│   ├── client3_public.pem
│   ├── client4_public.pem
│   └── client5_public.pem
├── client1/
│   ├── email files...
├── client2/
│   ├── email files...
├── client3/
│   ├── email files...
├── client4/
│   ├── email files...
└── client5/
    ├── email files...
    
for the client
client/
├── server_public.pem
├── client_client1/
|   ├── client1_public.pem
|   ├── client1_private.pem
├── client_client2/
|   ├── client1_public.pem
|   ├── client1_private.pem
├── client_client3/
|   ├── client1_public.pem
|   ├── client1_private.pem
├── client_client4/
|   ├── client1_public.pem
|   ├── client1_private.pem
├── client_client5/
|   ├── client1_public.pem
|   ├── client1_private.pem
'''

from Crypto.PublicKey import RSA
import os

#directory to store keys on the server
server_key_dir = "server"
if not os.path.exists(server_key_dir):
    os.makedirs(server_key_dir)

#generate server keys
server_key = RSA.generate(2048) #2048 bit

#save server public key
with open(os.path.join(server_key_dir, "server_public.pem"), "wb") as f:
    f.write(server_key.publickey().export_key())

#save server private key
with open(os.path.join(server_key_dir, "server_private.pem"), "wb") as f:
    f.write(server_key.export_key())

#known clients
clients = ["client1", "client2", "client3", "client4", "client5"]

#generate keys for each client and create their directories
for client in clients:
    #generate key for client
    client_key = RSA.generate(2048) #2048 bit
    
    #create directory in server directory for client publics keys
    client_key_dir = os.path.join(server_key_dir, "keys")
    if not os.path.exists(client_key_dir):
        os.makedirs(client_key_dir)
    
    #save clients puclic key
    with open(os.path.join(client_key_dir, f"{client}_public.pem"), "wb") as f:
        f.write(client_key.publickey().export_key())
    
    #create client folders for emails, this is also in server.py
    #just here for good meassures
    client_folder = os.path.join(server_key_dir, client)
    if not os.path.exists(client_folder):
        os.makedirs(client_folder)

    #create a client-side directory structure if not already exists
    client_side_dir = "client"
    if not os.path.exists(client_side_dir):
        os.makedirs(client_side_dir)
    
    #create client specific directory for storing client keys
    client_specific_dir = os.path.join(client_side_dir, f"client_{client}")
    if not os.path.exists(client_specific_dir):
        os.makedirs(client_specific_dir)
    
    #save client key pairs on client side in client specific directory
    with open(os.path.join(client_specific_dir, f"{client}_private.pem"), "wb") as f:
        f.write(client_key.export_key())
    with open(os.path.join(client_specific_dir, f"{client}_public.pem"), "wb") as f:
        f.write(client_key.publickey().export_key())

#copy of the server public key to the general client directory
client_general_dir = "client"
with open(os.path.join(client_general_dir, "server_public.pem"), "wb") as f:
    f.write(server_key.publickey().export_key())

#print to know key generation was successful
print("Keys and directories generated successfully.")
