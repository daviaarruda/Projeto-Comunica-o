import socket
import threading
import hashlib

HOST = 'localhost'
PORT = 12345
TAMANHO_MAXIMO = 1024

def calcular_checksum(mensagem):
    return hashlib.md5(mensagem.encode()).hexdigest()

def processar_cliente(conn, endereco):
    print(f"[+] Conexão estabelecida com {endereco}")

    conn.send(str(TAMANHO_MAXIMO).encode())

    while True:
        try:
            dados = conn.recv(1024).decode()
            if not dados:
                break

            partes = dados.split('|', 3)
            if len(partes) != 4:
                print("[!] Pacote malformado recebido. Ignorando.")
                conn.send("NACK|MALFORMADO".encode())
                continue

            sequencia_str, checksum_recebido, flag, mensagem = partes
            try:
                sequencia = int(sequencia_str)
            except ValueError:
                print(f"[!] Sequência inválida: {sequencia_str}")
                conn.send("NACK|SEQ_INV".encode())
                continue

            if flag == "PERDER":
                print(f"[SIMULAÇÃO] Ignorando pacote {sequencia} conforme flag de perda.")
                continue

            checksum_calculado = calcular_checksum(mensagem)

            if checksum_recebido != checksum_calculado:
                print(f"[X] ERRO de integridade no pacote {sequencia}. Enviando NACK.")
                conn.send(f"NACK|{sequencia}".encode())
            else:
                print(f"[✓] Pacote {sequencia} recebido corretamente: {mensagem}")
                conn.send(f"ACK|{sequencia}".encode())

        except ConnectionResetError:
            print(f"[!] Conexão com {endereco} foi encerrada abruptamente.")
            break
        except Exception as e:
            print(f"[!] Erro inesperado com {endereco}: {e}")
            break

    conn.close()
    print(f"[-] Conexão encerrada com {endereco}")

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen()
    print(f"[*] Servidor aguardando conexões em {HOST}:{PORT}")

    while True:
        conn, endereco = servidor.accept()
        thread = threading.Thread(target=processar_cliente, args=(conn, endereco))
        thread.start()

if __name__ == "__main__":
    iniciar_servidor()