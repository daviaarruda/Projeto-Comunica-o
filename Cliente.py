import socket
import hashlib

HOST = 'localhost'
PORT = 12345

def calcular_checksum(mensagem):
    return hashlib.md5(mensagem.encode()).hexdigest()

def enviar_pacote(socket_cliente, sequencia, mensagem, corromper=False):
    checksum = calcular_checksum(mensagem)
    if corromper:
        checksum = "checksum_invalido"
    pacote = f"{sequencia}|{checksum}|{mensagem}"
    socket_cliente.send(pacote.encode())

def iniciar_cliente():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_cliente:
        socket_cliente.connect((HOST, PORT))
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
                enviar_pacote(socket_cliente, sequencia, mensagem)
                resposta = socket_cliente.recv(1024).decode()
                print(f"[Servidor] {resposta}")
                sequencia += 1

            elif modo_envio == '2':
                total_pacotes = int(input("Quantos pacotes deseja enviar em rajada? ").strip())

                escolha_mensagem = input("Deseja digitar as mensagens manualmente? (s/n): ").strip().lower()
                mensagens = []
                if escolha_mensagem == 's':
                    for i in range(total_pacotes):
                        msg = input(f"Digite a mensagem para o pacote {i+1}: ").strip()
                        mensagens.append(msg)
                else:
                    mensagens = [chr(97 + i) for i in range(total_pacotes)]

                corromper_pacote = input("Deseja corromper algum pacote? (s/n): ").strip().lower() == 's'
                pacote_corrompido = int(input(f"Qual número do pacote deseja corromper (1-{total_pacotes})? ").strip()) if corromper_pacote else -1

                for i, mensagem in enumerate(mensagens, start=1):
                    corromper = (i == pacote_corrompido)
                    if len(mensagem.encode()) > tamanho_max_msg:
                        print(f"[!] Erro: o pacote {i} excede o tamanho permitido ({tamanho_max_msg} bytes).")
                        continue
                    enviar_pacote(socket_cliente, sequencia, mensagem, corromper)
                    resposta = socket_cliente.recv(1024).decode()
                    print(f"[Servidor] {resposta}")
                    sequencia += 1

            elif modo_envio == '0':
                print("[*] Encerrando cliente.")
                break

            else:
                print("[!] Opção inválida. Tente novamente.")

if __name__ == "__main__":
    iniciar_cliente()
