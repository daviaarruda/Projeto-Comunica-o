Este projeto é uma aplicação cliente-servidor simples baseada em sockets TCP, com suporte à escolha de envio **único** ou **em rajada**, além da simulação de **pacotes corrompidos**. Ele foi desenvolvido como parte do projeto de Comunicação.

---

## 🚀 Funcionalidades

- Conexão entre cliente e servidor via socket TCP
- Envio de mensagens com verificação de integridade via checksum (MD5)
- Escolha entre dois modos de envio:
  - ✅ **Único**: envia uma mensagem por vez
  - 🚀 **Rajada**: envia vários pacotes seguidos automaticamente
- Simulação de corrupção de pacotes
- Retorno do servidor indicando:
  - Se o pacote chegou corretamente
  - Se foi detectada corrupção no conteúdo

---

## 📦 Estrutura do Projeto

```bash
Projeto-Comunica-o/
├── cliente.py       # Cliente socket com modos de envio
├── servidor.py      # Servidor que valida mensagens e responde
└── README.md        # Este manual
```

⚙️ Como usar
1. Clone este repositório

```bash
  git clone https://github.com/daviaarruda/Projeto-Comunica-o
  cd Projeto-Comunica-o
```
2. Inicie o servidor
 ```bash

   python Servidor.py
```
Você verá a mensagem:

```bash
[OK] Servidor iniciado em localhost:12345
```
3. Execute o cliente em outro terminal

```bash
python Cliente.py
```
O programa perguntará:

```bash
[*] Escolha o modo de envio:
1 - Envio único
2 - Envio em rajada
>>>
```
No modo 1, digite a mensagem desejada.

No modo 2, informe quantos pacotes deseja enviar e se deseja corromper algum.

🛠 Exemplo
Envio em rajada com corrupção:
```bash
Quantos pacotes deseja enviar em rajada? 5
Deseja corromper algum pacote? (s/n): s
Qual número do pacote deseja corromper (1-5)? 3
```
O cliente enviará 5 pacotes e o terceiro será corrompido de forma proposital.

👨‍💻 Requisitos
Python 3.7 ou superior

Nenhuma biblioteca externa é necessária (apenas módulos nativos)





