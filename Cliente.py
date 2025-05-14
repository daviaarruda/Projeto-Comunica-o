import socket
import hashlib
import random
import time

HOST = 'localhost'
PORT = 12345
MAX_TENTATIVAS = 5
PROB_PERDA = 0.2

def calcular_checksum(mensagem):
    return hashlib.md5(mensagem.encode()).hexdigest()

def enviar_pacote(socket_cliente, sequencia, mensagem, corromper=False):
    checksum = calcular_checksum(mensagem)
    if corromper:
        checksum = "checksum_invalido"
    pacote = f"{sequencia}|{checksum}|{mensagem}"
    if random.random() < PROB_PERDA:
        print(f"[SIMULAÇÃO] Pacote {sequencia} foi perdido na rede.")
        return  # Simula perda
    socket_cliente.send(pacote.encode())

def iniciar_cliente():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_cliente:
        socket_cliente.connect((HOST, PORT))
        socket_cliente.settimeout(3)
        print("[*] Conectado ao servidor.")

        tamanho_max_msg = int(socket_cliente.recv(1024).decode())
        print(f"[*] Tamanho máximo da mensagem: {tamanho_max_msg} bytes")

        sequencia = 1  

        while True:
            print("\nMenu de opções:")
            print("1 - Enviar uma única mensagem")
            print("2 - Enviar mensagens em rajada")
            print("0 - Encerrar conexão")
            modo_envio = input("Escolha o modo de envio: ").strip()

            if modo_envio == '1':
                mensagem = input("Digite a mensagem a ser enviada: ").strip()
                if len(mensagem.encode()) > tamanho_max_msg:
                    print("[!] Erro: mensagem excede o tamanho máximo permitido.")
                    continue

                tentativas = 0
                while tentativas < MAX_TENTATIVAS:
                    enviar_pacote(socket_cliente, sequencia, mensagem)
                    try:
                        resposta = socket_cliente.recv(1024).decode()
                        if resposta.startswith("ACK"):
                            print(f"[Servidor] {resposta}")
                            break
                        else:
                            print(f"[Servidor] {resposta}")
                    except socket.timeout:
                        print(f"[!] Timeout - Reenviando pacote {sequencia}")
                    tentativas += 1

                sequencia += 1

            elif modo_envio == '2':
                total_pacotes = int(input("Quantos pacotes deseja enviar em rajada? ").strip())
                escolha_mensagem = input("Deseja digitar as mensagens manualmente? (s/n): ").strip().lower()
                mensagens = [input(f"Digite a mensagem para o pacote {i+1}: ").strip()
                             for i in range(total_pacotes)] if escolha_mensagem == 's' else [chr(97 + i) for i in range(total_pacotes)]

                corromper_pacote = input("Deseja corromper algum pacote? (s/n): ").strip().lower() == 's'
                pacote_corrompido = int(input(f"Qual número do pacote deseja corromper (1-{total_pacotes})? ").strip()) if corromper_pacote else -1

                for i, mensagem in enumerate(mensagens, start=1):
                    if len(mensagem.encode()) > tamanho_max_msg:
                        print(f"[!] Erro: o pacote {i} excede o tamanho permitido.")
                        continue

                    tentativas = 0
                    while tentativas < MAX_TENTATIVAS:
                        corromper = (i == pacote_corrompido)
                        enviar_pacote(socket_cliente, sequencia, mensagem, corromper)
                        try:
                            resposta = socket_cliente.recv(1024).decode()
                            if resposta.startswith("ACK"):
                                print(f"[Servidor] {resposta}")
                                break
                            else:
                                print(f"[Servidor] {resposta}")
                        except socket.timeout:
                            print(f"[!] Timeout - Reenviando pacote {sequencia}")
                        tentativas += 1

                    sequencia += 1

            elif modo_envio == '0':
                print("[*] Encerrando cliente.")
                break
            else:
                print("[!] Opção inválida. Tente novamente.")

if __name__ == "__main__":
    iniciar_cliente()
