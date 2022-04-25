import socket


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

    print(">>>proc:", palavras)

    contagem = {}
    mais_recorrentes = ''

    for palavra in palavras:
        if palavra in contagem:
            contagem[palavra] += 1
        else:
            contagem[palavra] = 1

    print(">>>proc:", contagem)

    for i in range(5):
        maior = 0
        palavra_mais_recorrente = ''

        for palavra in contagem:
            if contagem[palavra] >= maior:
                palavra_mais_recorrente = palavra
                maior = contagem[palavra]

        mais_recorrentes += str(i+1) + '- ' + palavra_mais_recorrente + '.\n'
        contagem.pop(palavra_mais_recorrente)

    print(">>>proc:", mais_recorrentes)

    return mais_recorrentes


HOST = ''    # '' possibilita acessar qualquer endereco alcancavel da maquina local
PORTA = 5000  # porta onde chegarao as mensagens para essa aplicacao

# cria um socket para comunicacao
sock = socket.socket()  # valores default: socket.AF_INET, socket.SOCK_STREAM

# vincula a interface e porta para comunicacao
sock.bind((HOST, PORTA))

# define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
sock.listen(10)

while True:
    # aceita a primeira conexao da fila (chamada pode ser BLOQUEANTE)
    # retorna um novo socket e o endereco do par conectado
    novoSock, endereco = sock.accept()
    print('Conectado com: ', endereco)

    # depois de conectar-se, espera uma mensagem (chamada pode ser BLOQUEANTE))
    msg = novoSock.recv(1024)  # argumento indica a qtde maxima de dados

    if not msg:
        break
    else:
        resultado = processamento(str(msg,  encoding='utf-8'))

        # envia mensagem de resposta
        novoSock.send(bytes(resultado, encoding='utf-8'))

    # fecha o socket da conexao
    novoSock.close()

# fecha o socket principal
sock.close()
