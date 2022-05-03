import socket
import select
import sys
import multiprocessing

def dados(nome_arquivo):
    texto = None

    try:
        with open(nome_arquivo) as arquivo:
            texto = '\n'.join(arquivo.readlines())
    except:
        texto = None

    return texto


def processamento(nome_arquivo):
    texto = dados(nome_arquivo)

    if (texto == None):
        return "Erro. Arquivo não encontrado."

    # substitui pontuação e breakline por espaço
    for char in '-.,\n':
        texto = texto.replace(char, ' ')

    palavras = texto.lower().split()

    contagem = {}
    mais_recorrentes = ''

    for palavra in palavras:
        if palavra in contagem:
            contagem[palavra] += 1
        else:
            contagem[palavra] = 1

    for i in range(5):
        maior = 0
        palavra_mais_recorrente = ''

        for palavra in contagem:
            if contagem[palavra] >= maior:
                palavra_mais_recorrente = palavra
                maior = contagem[palavra]

        mais_recorrentes += str(i+1) + '- ' + palavra_mais_recorrente + '.\n'
        contagem.pop(palavra_mais_recorrente)

    return mais_recorrentes


def atendeRequisicoes(novoSock):        
    while True:
        # depois de conectar-se, espera uma mensagem (chamada pode ser BLOQUEANTE))
        msg = novoSock.recv(1024)  # argumento indica a qtde maxima de dados

        if not msg:
             # fecha o socket da conexao
            novoSock.close()
            break
        else:
            resultado = processamento(str(msg,  encoding='utf-8'))

            # envia mensagem de resposta
            novoSock.send(bytes(resultado, encoding='utf-8'))
   

# define a lista de I/O de interesse (jah inclui a entrada padrao)
entradas = [sys.stdin]
# armazena as conexoes completadas
conexoes = {}
# armazena os processos criados para fazer join
clientes=[]

HOST = ''    # '' possibilita acessar qualquer endereco alcancavel da maquina local
PORTA = 5000  # porta onde chegarao as mensagens para essa aplicacao

# cria um socket para comunicacao
sock = socket.socket()  # valores default: socket.AF_INET, socket.SOCK_STREAM

# vincula a interface e porta para comunicacao
sock.bind((HOST, PORTA))

# define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
sock.listen(10)

# configura o socket para o modo nao-bloqueante
sock.setblocking(False)

# inclui o socket principal na lista de entradas de interesse
entradas.append(sock)

while True:
    # espera por qualquer entrada de interesse
    leitura, escrita, excecao = select.select(entradas, [], [])

    #tratar todas as entradas prontas
    for pronto in leitura:
        if pronto == sock:  # pedido novo de conexao
            # aceita a primeira conexao da fila (chamada pode ser BLOQUEANTE)
            # retorna um novo socket e o endereco do par conectado
            novoSock, endereco = sock.accept()

            # registra a nova conexao
            conexoes[novoSock] = endereco

            print('Conectado com: ', endereco)

            # cria um novo processo para executar a requisição do cliente
            cliente = multiprocessing.Process(target=atendeRequisicoes, args=(novoSock,))
            cliente.start()
            clientes.append(cliente) # armazena a referencia da thread para usar com join()

        elif pronto == sys.stdin: # entrada padrao
            cmd = input()

            if cmd == 'fim': # solicitacao de finalizacao do servidor
                for c in clientes: #aguarda todos os processos terminarem
                        c.join()
            
                sock.close()
                sys.exit()
            elif cmd == 'hist': # outro exemplo de comando para o servidor
                print(str(conexoes.values()))
