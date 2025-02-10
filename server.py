import socket   

HOST='127.0.0.1'
PORT=5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)


print(f"[*] Serveur en écoute sur {HOST}:{PORT}")


while True:
    client, addr = server.accept()
    print(f"[*] Connexion établie avec {addr[0]}:{addr[1]}")
    client.send("Bienvenue sur le serveur !".encode())
    client.close()
    print(f"[*] Connexion fermée avec {addr[0]}:{addr[1]}")