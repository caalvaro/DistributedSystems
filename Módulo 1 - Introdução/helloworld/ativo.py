# Exemplo basico socket (lado ativo)

import socket
import time

HOST = 'localhost'  # maquina onde esta o par passivo
PORTA = 5000        # porta que o par passivo esta escutando

# cria socket
sock = socket.socket()  # default: socket.AF_INET, socket.SOCK_STREAM

# conecta-se com o par passivo
sock.connect((HOST, PORTA))

# envia uma mensagem para o par conectado
sock.send(b"Ola, sou o lado ativo!")
time.sleep(3)
sock.send(b"Ola, sou o lado ativo!2")
time.sleep(3)
sock.send(b"Ola, sou o lado ativo!3")
time.sleep(3)
sock.send(b"Ola, sou o lado ativo!4")
time.sleep(5)

# espera a resposta do par conectado (chamada pode ser BLOQUEANTE)
msg = sock.recv(1024)  # argumento indica a qtde maxima de bytes da mensagem

# imprime a mensagem recebida
print(str(msg,  encoding='utf-8'))
time.sleep(5)

# encerra a conexao
sock.close()
