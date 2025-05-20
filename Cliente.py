import socket
import hashlib
import time
import threading

HOST = 'localhost'
PORT = 12345
WINDOW_SIZE = 4
TIMEOUT = 2
MAX_TENTATIVAS = 5

lock = threading.Lock()
acknowledged = {}
timers = {}

def calcular_checksum(mensagem):
    return hashlib.md5(mensagem.encode()).hexdigest()

def enviar_pacote(socket_cliente, sequencia, mensagem, flag="OK"):
    checksum = calcular_checksum(mensagem)
    pacote = f"{sequencia}|{checksum}|{flag}|{mensagem}"
    socket_cliente.send(pacote.encode())
    print(f"[ENVIO] Pacote {sequencia} enviado (flag: {flag}).")

def gerenciar_respostas(socket_cliente):
    global acknowledged
    while True:
        try:
            resposta = socket_cliente.recv(1024).decode()
            if resposta.startswith("ACK"):
                _, seq = resposta.split("|")
                seq = int(seq)
                with lock:
                    acknowledged[seq] = True
                    print(f"[✔] ACK recebido para pacote {seq}")
            elif resposta.startswith("NACK"):
                _, seq = resposta.split("|")
                seq = int(seq)
                with lock:
                    acknowledged[seq] = False
                    print(f"[✘] NACK recebido para pacote {seq}")
        except Exception:
            continue

def iniciar_cliente():
    global acknowledged
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_cliente:
        socket_cliente.connect((HOST, PORT))
        socket_cliente.settimeout(1.5)
        print("[*] Conectado ao servidor.")

        tamanho_max_msg = int(socket_cliente.recv(1024).decode())
        print(f"[*] Tamanho máximo da mensagem: {tamanho_max_msg} bytes")

        threading.Thread(target=gerenciar_respostas, args=(socket_cliente,), daemon=True).start()

        sequencia = 1

        while True:
            print("\nMenu:")
            print("1 - Enviar mensagens em janela deslizante")
            print("0 - Encerrar")
            opcao = input("Escolha: ").strip()

            if opcao == '1':
                total_pacotes = int(input("Quantos pacotes deseja enviar? ").strip())
                mensagens = [input(f"Mensagem do pacote {i+1}: ").strip() for i in range(total_pacotes)]

                perdas_input = input("Deseja simular perda em quais pacotes? (ex: 2 4),se não quiser apenas ENTER: ").strip()
                pacotes_a_perder = set(map(int, perdas_input.split())) if perdas_input else set()

                base = sequencia
                next_seq = sequencia
                fim = sequencia + total_pacotes - 1

                acknowledged = {}
                tentativas = {i: 0 for i in range(sequencia, fim + 1)}
                enviados = {}

                while base <= fim:
                    with lock:
                        while next_seq <= fim and next_seq < base + WINDOW_SIZE:
                            msg = mensagens[next_seq - sequencia]
                            if len(msg.encode()) > tamanho_max_msg:
                                print(f"[!] Mensagem {next_seq} excede limite.")
                                acknowledged[next_seq] = True
                                next_seq += 1
                                continue

                            flag_perda = "PERDER" if (next_seq - sequencia + 1) in pacotes_a_perder and tentativas[next_seq] == 0 else "OK"
                            enviar_pacote(socket_cliente, next_seq, msg, flag_perda)
                            timers[next_seq] = time.time()
                            enviados[next_seq] = msg
                            tentativas[next_seq] += 1
                            next_seq += 1

                        time.sleep(0.5)
                        for seq in range(base, next_seq):
                            if seq in acknowledged:
                                if acknowledged[seq]:
                                    del timers[seq]
                                    base += 1
                                elif tentativas[seq] < MAX_TENTATIVAS:
                                    print(f"[!] Reenviando pacote {seq} (NACK)")
                                    enviar_pacote(socket_cliente, seq, enviados[seq])
                                    tentativas[seq] += 1
                                    timers[seq] = time.time()
                                    acknowledged.pop(seq)
                            else:
                                if time.time() - timers[seq] > TIMEOUT:
                                    if tentativas[seq] < MAX_TENTATIVAS:
                                        print(f"[!] Timeout - Reenviando pacote {seq}")
                                        enviar_pacote(socket_cliente, seq, enviados[seq])
                                        tentativas[seq] += 1
                                        timers[seq] = time.time()
                                    else:
                                        print(f"[X] Pacote {seq} excedeu tentativas máximas.")
                                        acknowledged[seq] = True
                                        base += 1

                sequencia = fim + 1

            elif opcao == '0':
                print("[*] Encerrando cliente.")
                break

            else:
                print("[!] Opção inválida.")

if __name__ == "__main__":
    iniciar_cliente()