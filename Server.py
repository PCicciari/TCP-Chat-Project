import threading
import socket

# Now this Host is the IP address of the Server, over which it is running.
# I've user my localhost.
host = "127.0.0.1"
port = 55555  # Choose any random port which is not so common (like 80)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the server to IP Address
server.bind((host, port))
# Start Listening Mode
server.listen()
# List to contain the Clients getting connected and nicknames
clients = []
nicknames = []
users = []


# 1.Broadcasting Method
def broadcast(message):
    for client in clients:
        client.send(message)


# 2.Receiving Messages from client then broadcasting
def handle(client):
    while True:
        try:
            msg = message = client.recv(1024)

            if msg.decode('ascii').startswith('DM'):
                priv_mes = str()
                Name_to_send = msg.decode('ascii')[3:].split()
                name = Name_to_send[0]
                sender_name = Name_to_send.pop()
                Name_to_send.pop(0)
                len_of_msg = len(Name_to_send)
                for i in range(len_of_msg):
                    priv_mes += f'{Name_to_send[i]} '
                sender_name +=f': {priv_mes}'
                priv_msg(name, sender_name)
            elif msg.decode('ascii').startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_kick = msg.decode('ascii')[5:]
                    kick_user(name_to_kick)
                else:
                    client.send('Command Refused!'.encode('ascii'))
            elif msg.decode('ascii').startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_ban = msg.decode('ascii')[4:]
                    kick_user(name_to_ban)
                    with open('bans.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} was banned by the Admin!')
                else:
                    client.send('Command Refused!'.encode('ascii'))
            else:
                broadcast(message)  # As soon as message received, broadcast it.

        except socket.error:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f'{nickname} left the Chat!'.encode('ascii'))
                nicknames.remove(nickname)
                users.remove(nickname)
                break


# Main Receive method
def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        # Ask the clients for Nicknames
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        # If the Client is an Admin prompt for the password.
        with open('bans.txt', 'r') as f:
            bans = f.readlines()

        if nickname + '\n' in bans:
            client.send('BAN'.encode('ascii'))
            client.close()
            continue

        if nickname == 'admin':
            client.send('PASS'.encode('ascii'))
            password = client.recv(1024).decode('ascii')
            # I know it is lame, but my focus is mainly for Chat system and not a Login System
            if password != 'adminpass':
                client.send('REFUSE'.encode('ascii'))
                client.close()
                continue

        nicknames.append(nickname)
        clients.append(client)
        users.append(nickname)


        print(f'Nickname of the client is {nickname}')
        broadcast(f'{nickname} joined the Chat'.encode('ascii'))
        broadcast(f"Current User List:\n".encode('ascii'))
        for user in users:
            broadcast(f"{user}\n".encode('ascii'))
        client.send('Connected to the Server!'.encode('ascii'))

        # Handling Multiple Clients Simultaneously
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You Were Kicked from Chat !'.encode('ascii'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked from the server!'.encode('ascii'))

def priv_msg(name, priv_mss):
    print("Priv mesage called")
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_msg = clients[name_index]
        client_to_msg.send(priv_mss.encode('ascii'))

# Calling the main method
print('Server is Listening ...')
receive()