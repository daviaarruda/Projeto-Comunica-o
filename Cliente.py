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
        except:
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
            print("1 - Enviar mensagem única")
            print("2 - Enviar mensagens em grupo (janela deslizante)")
            print("0 - Encerrar")
            opcao = input("Escolha: ").strip()

            if opcao == '1':
                msg = input("Mensagem: ").strip()
                flag = "OK"
                if input("Simular perda? (s/n): ").strip().lower() == 's':
                    flag = "PERDER"
                elif input("Simular corrupção? (s/n): ").strip().lower() == 's':
                    flag = "CORROMPER"
                enviar_pacote(socket_cliente, sequencia, msg, flag)

                tentativas = 0
                while tentativas < MAX_TENTATIVAS:
                    time.sleep(TIMEOUT)
                    if acknowledged.get(sequencia) == True:
                        print("[✓] Mensagem entregue com sucesso.")
                        break
                    elif acknowledged.get(sequencia) == False:
                        print("[✘] NACK recebido. Reenviando...")
                        enviar_pacote(socket_cliente, sequencia, msg, "OK")
                    else:
                        print("[!] Timeout, reenviando...")
                        enviar_pacote(socket_cliente, sequencia, msg, "OK")
                    tentativas += 1

                sequencia += 1

            elif opcao == '2':
                total = int(input("Quantos pacotes deseja enviar? "))
                mensagens = [input(f"Mensagem do pacote {i+1}: ") for i in range(total)]

                perdas_input = input("Simular perda em quais pacotes? (ex: 2 4): ").strip()
                pacotes_perder = set(map(int, perdas_input.split())) if perdas_input else set()

                corrup_input = input("Simular corrupção em quais pacotes? (ex: 1 3): ").strip()
                pacotes_corromper = set(map(int, corrup_input.split())) if corrup_input else set()

                base = sequencia
                next_seq = sequencia
                fim = sequencia + total - 1

                acknowledged = {i: None for i in range(base, fim + 1)}
                tentativas = {i: 0 for i in range(base, fim + 1)}
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

                            flag = "OK"
                            if (next_seq - sequencia + 1) in pacotes_perder and tentativas[next_seq] == 0:
                                flag = "PERDER"
                            elif (next_seq - sequencia + 1) in pacotes_corromper and tentativas[next_seq] == 0:
                                flag = "CORROMPER"

                            enviar_pacote(socket_cliente, next_seq, msg, flag)
                            timers[next_seq] = time.time()
                            enviados[next_seq] = msg
                            tentativas[next_seq] += 1
                            next_seq += 1

                    time.sleep(0.5)
                    avancou = False
                    for seq in range(base, next_seq):
                        if acknowledged[seq] is True:
                            if seq in timers:
                                del timers[seq]
                            if base == seq:
                                base += 1
                                avancou = True
                        elif acknowledged[seq] is False and tentativas[seq] < MAX_TENTATIVAS:
                            print(f"[!] Reenviando pacote {seq} (NACK)")
                            enviar_pacote(socket_cliente, seq, enviados[seq])
                            tentativas[seq] += 1
                            timers[seq] = time.time()
                            acknowledged[seq] = None
                        elif acknowledged[seq] is None and time.time() - timers[seq] > TIMEOUT:
                            if tentativas[seq] < MAX_TENTATIVAS:
                                print(f"[!] Timeout - Reenviando pacote {seq}")
                                enviar_pacote(socket_cliente, seq, enviados[seq])
                                tentativas[seq] += 1
                                timers[seq] = time.time()
                            else:
                                print(f"[X] Pacote {seq} excedeu tentativas. Marcado como entregue.")
                                acknowledged[seq] = True
                                if base == seq:
                                    base += 1
                                    avancou = True

                    if avancou:
                        print(f"[Janela] Base: {base}, Próximo Seq: {next_seq}")

                sequencia = fim + 1

            elif opcao == '0':
                print("[*] Encerrando cliente.")
                break
            else:
                print("[!] Opção inválida.")

if __name__ == "__main__":
    iniciar_cliente()