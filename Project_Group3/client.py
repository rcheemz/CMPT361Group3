'''
CMPT 361 Project
Spring 2024

Shadr Baaba
Rimneet Cheema
Jamie McDonald

client.py
'''

import socket

def client():
    server_ip = input("Enter server name: ")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, 13000))

    #authentication process
    print(client_socket.recv(2048).decode(), end='')
    username = input()
    client_socket.send(username.encode())

    print(client_socket.recv(2048).decode(), end='') 
    password = input()
    client_socket.send(password.encode())

    #check authentication response
    response = client_socket.recv(2048).decode().strip()
    print(response)
    if "Invalid" in response:
        print(response)
        client_socket.close()
        return

    #menu loop
    while True:
        menu = client_socket.recv(2048).decode().strip()
        print(menu)
        choice = input("choice: ")
        client_socket.send(choice.encode())

        if choice == "1":
            #call function for send email
            send_email(client_socket)
        elif choice == "2":
            #call function for view inbox
            view_inbox(client_socket)
        elif choice == "3":
            #call function for view email
            view_email(client_socket)
        elif choice == "4":
            #terminate connection on client side 
            print("Connection terminated.")
            client_socket.close()
            break
        else:
            print("Invalid choice. Try again.")

def send_email(client_socket):
    '''
    This function will handle the send email operation for client
    '''
    #prompt for recipients
    print(client_socket.recv(2048).decode(), end='') 
    to = input()
    client_socket.send(to.encode())
    
    
    #prompt for title
    print(client_socket.recv(2048).decode(), end='')  
    title = input()
    client_socket.send(title.encode())
    
    #prompt for message content
    print(client_socket.recv(2048).decode(), end='')  
    content = input()
    client_socket.send(content.encode())
    
    response = client_socket.recv(2048).decode().strip()
    print(response)

def view_inbox(client_socket):
    '''
    This function will handle the view inbox operation for client
    '''
    response = client_socket.recv(4096).decode().strip()
    print(response)

def view_email(client_socket):
    '''
    This function will handle the view email operation for client
    '''
    #prompt for which email to view
    print(client_socket.recv(2048).decode(), end='') 
    email_index = input()
    
    #while the input is not a number keep prompting for index
    while not email_index.isdigit():
        print("Invalid input. Please enter a number.")
        email_index = input()
    
    client_socket.send(email_index.encode())

    response = client_socket.recv(4096).decode().strip()
    print(response)


#-------------
client()