# Projeto-Comunica-o

Aplicação cliente-servidor TCP com janela deslizante, suporte a retransmissão, simulação de perda de pacotes e verificação de integridade via checksum MD5. Desenvolvido como parte do projeto de Comunicação.

---

## 🚀 Funcionalidades

- Comunicação via socket TCP entre cliente e servidor  
- Protocolo de janela deslizante (Sliding Window) com tamanho configurável (default: 4)  
- Verificação de integridade das mensagens com checksum MD5  
- Retransmissão automática em caso de NACK ou timeout (2 segundos)  
- Simulação configurável de perda de pacotes (pacotes "desperdiçados")  
- Limite máximo de tentativas para reenvio (default: 5)  
- Comunicação concorrente no servidor com múltiplos clientes via threads  

---

## 📦 Estrutura do Projeto
Projeto-Comunica-o/
├── cliente.py # Cliente TCP com janela deslizante, retransmissão e simulação de perda
├── servidor.py # Servidor TCP multithread que valida integridade e responde ACK/NACK
└── README.md # Documentação do projeto
---

## ⚙️ Como usar

### Passo 1: Clonar o repositório

```bash
git clone https://github.com/daviaarruda/Projeto-Comunica-o
cd Projeto-Comunica-o
```
### Passo 2: Iniciar o servidor

python servidor.py
No terminal será exibida a mensagem:


[*] Servidor aguardando conexões em localhost:12345
### Passo 3: Executar o cliente (em outro terminal)

bash
Copiar
Editar
python cliente.py
📝 Funcionamento do Cliente
Ao executar, o cliente conecta ao servidor e recebe o tamanho máximo de mensagem suportado.

O menu principal oferece as opções:


Editar
Menu:
1 - Enviar mensagens em janela deslizante
0 - Encerrar
Escolha: 
Enviar mensagens em janela deslizante
Informe quantos pacotes deseja enviar.

Digite a mensagem para cada pacote.

Opcionalmente, informe quais pacotes devem simular perda (não serem enviados).

O cliente gerencia a janela deslizante com tamanho 4, envia pacotes, aguarda ACK/NACK, e retransmite pacotes com erro ou timeout até o limite de tentativas.

Encerrar
Finaliza o cliente.

📄 Protocolo de Comunicação
Cada pacote enviado é formatado como:

Copiar
Editar
sequencia|checksum_md5|flag|mensagem
Flags possíveis:

"OK": pacote normal

"PERDER": pacote marcado para simular perda (não enviado pelo servidor)

Respostas do servidor:

ACK|sequencia: pacote recebido corretamente

NACK|sequencia: pacote corrompido ou erro detectado

👨‍💻 Requisitos
Python 3.7 ou superior

Módulos nativos do Python (socket, threading, hashlib, time)

Nenhuma biblioteca externa necessária

🛠️ Como Personalizar
WINDOW_SIZE: tamanho da janela deslizante (cliente.py)

TIMEOUT: tempo de espera para retransmissão em segundos (cliente.py)

MAX_TENTATIVAS: número máximo de retransmissões por pacote (cliente.py)

TAMANHO_MAXIMO: limite máximo do tamanho da mensagem suportado pelo servidor (servidor.py)

