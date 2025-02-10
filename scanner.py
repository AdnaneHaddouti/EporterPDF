import socket

def scan_port(ip, port):
    """Vérifie si un port est ouvert sur une IP donnée"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)  
    result = s.connect_ex((ip, port))
    s.close()
    return result == 0

def main():
    target = input("Entrez l'adresse IP cible : ")
    ports = [21, 22, 25, 53, 80, 443, 3306, 8080]  
    print(f"\nScan en cours sur {target}...\n")
    for port in ports:
        if scan_port(target, port):
            print(f"[+] Port {port} est **OUVERT** ✅")
        else:
            print(f"[-] Port {port} est fermé ❌")

if __name__ == "__main__":
    main()