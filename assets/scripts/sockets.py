from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread


class Server:
    def __init__(self):
        self.clients = {}
        self.addresses = {}

        self.host = '127.0.0.1'
        self.port = 0
        self.bufsiz = 1024
        self.adr = (self.host, self.port)

        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind(self.adr)
        self.server.listen(3)
        print('Waiting for connection...')
        self.accept_thread = Thread(target=self.accept_incoming_connections)
        self.accept_thread.start()

    def accept_incoming_connections(self):
        while True:
            client, client_address = self.server.accept()
            print("{} has connected.".format(client_address))
            self.addresses[client] = client_address
            Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):  # Takes client socket as argument.
        name = client.recv(self.bufsiz).decode("utf8")
        self.clients[client] = name

        while True:
            msg = client.recv(self.bufsiz)
            if msg != bytes("{quit}", "utf8"):
                self.broadcast(msg)
            else:
                client.send(bytes("{quit}", "utf8"))
                client.close()
                del self.clients[client]
                break

    def broadcast(self, msg):  # prefix is for name identification.
        for sock in self.clients:
            print(sock)
            sock.send(msg)


class Client:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 33000
        self.bufsiz = 1024
        self.adr = (self.host, self.port)

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(self.adr)

        receive_thread = Thread(target=self.receive)
        receive_thread.start()

    def receive(self):
        while True:
            try:
                msg = self.client_socket.recv(self.bufsiz).decode("utf8")
            except OSError:  # Possibly client has left the chat.
                break

    def send(self, msg):  # event is passed by binders.
        self.client_socket.send(bytes(msg, "utf8"))
        if msg == "{quit}":
            self.client_socket.close()
