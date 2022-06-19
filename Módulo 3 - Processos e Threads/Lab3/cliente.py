# Exemplo basico socket (lado ativo)

import socket

HOST = 'localhost'  # maquina onde esta o par passivo
PORTA = 5000        # porta que o par passivo esta escutando

# cria socket
sock = socket.socket()  # default: socket.AF_INET, socket.SOCK_STREAM

# conecta-se com o par passivo
sock.connect((HOST, PORTA))

nome_arquivo = input(
    'Digite o nome do arquivo: ')

# envia uma mensagem para o par conectado
sock.send(bytes(nome_arquivo, 'UTF-8'))

# espera a resposta do par conectado (chamada pode ser BLOQUEANTE)
# argumento indica a qtde maxima de bytes da mensagem
msg = sock.recv(1024)

# imprime a mensagem recebida
print(str(msg,  encoding='utf-8'))

# encerra a conexao
sock.close()
