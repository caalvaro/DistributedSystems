#servidor de echo: lado servidor
import socket

# define a localizacao do servidor
HOST = '' # vazio indica que podera receber requisicoes a partir de qq interface de rede da maquina
PORT = 10000 # porta de acesso

def iniciaServidor():
	'''Cria um socket de servidor e o coloca em modo de espera por conexoes
	Saida: o socket criado'''
	# cria o socket 
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet( IPv4 + TCP) 

	# vincula a localizacao do servidor
	sock.bind((HOST, PORT))

	# coloca-se em modo de espera por conexoes
	sock.listen(5) 

	return sock

def aceitaConexao(sock):
	'''Aceita o pedido de conexao de um cliente
	Entrada: o socket do servidor
	Saida: o novo socket da conexao e o endereco do cliente'''

	# estabelece conexao com o proximo cliente
	clisock, endr = sock.accept() 

	return clisock, endr

def atendeRequisicoes(clisock, endr):
	'''Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
	Entrada: socket da conexao e endereco do cliente
	Saida: '''

	while True: 
		#recebe dados do cliente
		data = clisock.recv(1024) 
		if not data: # dados vazios: cliente encerrou
			print(str(endr) + '-> encerrou')
			break 
		print(str(endr) + ': ' + str(data, encoding='utf-8'))
		clisock.send(data) # ecoa os dados para o cliente
	clisock.close() # encerra a conexao com o cliente

def main():
	'''Inicializa e implementa o loop principal (infinito) do servidor'''
	sock = iniciaServidor()
	while True:
		clisock, endr = aceitaConexao(sock)
		print ('Conectado com: ', endr)
		atendeRequisicoes(clisock, endr)

main()
