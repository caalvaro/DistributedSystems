#servidor de echo: lado servidor
#com finalizacao do lado do servidor
from glob import glob
from re import X
import socket
import select
import sys
import json
import os

# define a localizacao do servidor
HOST = '' # vazio indica que podera receber requisicoes a partir de qq interface de rede da maquina
PORT = -1 # a ser definida depois de acordo com o id passado

#define a lista de I/O de interesse (jah inclui a entrada padrao)
entradas = [sys.stdin]
#armazena as conexoes completadas
conexoes = {}

# informações de qual réplica é a cópia primaria da rede
copiaPrimaria = {
    "id": 1,
    "porta": 10001
}

# histórico de alterações do valor X
historico = []

# valor que vai ser alterado e copiado entre as réplicas
X = 0

def enviaMensagem(mensagem, sock):
    """Envia uma mensagem, onde os dois primeiros bytes representam o tamanho da mensagem"""
    mensagemJson = json.dumps(mensagem)
    tamanho = len(mensagemJson.encode("utf-8"))
    tamanho_em_bytes = tamanho.to_bytes(2, byteorder="big")
    sock.sendall(tamanho_em_bytes)
    sock.sendall(mensagemJson.encode("utf-8"))


def recebeMensagem(sock):
    """Recebe qualquer mensagem enviada ou pelo servidor central
    ou por outro cliente, resgata até atingir o tamnho notificado

    Saida: mensagem completa em formato JSON"""

    tamanho_mensagem = int.from_bytes(sock.recv(2), byteorder="big")
    chunks = []
    recebidos = 0
    while recebidos < tamanho_mensagem:
        chunk = sock.recv(min(tamanho_mensagem - recebidos, 2048))
        chunks.append(chunk)
        recebidos = recebidos + len(chunk)
    mensagem = b''.join(chunks)
    if(not mensagem):
        return None
    return json.loads(mensagem.decode("utf-8"))


def iniciaServidor(id):
    '''Cria um socket de servidor e o coloca em modo de espera por conexoes
    Saida: o socket criado'''
    global PORT

    PORT = 10000 + id
    # cria o socket 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet( IPv4 + TCP) 

    # vincula a localizacao do servidor
    sock.bind((HOST, PORT))

    # coloca-se em modo de espera por conexoes
    sock.listen(5) 

    # configura o socket para o modo nao-bloqueante
    sock.setblocking(False)

    # inclui o socket principal na lista de entradas de interesse
    entradas.append(sock)

    print("Escutando na porta: ", PORT)

    return sock


def aceitaConexao(sock):
    '''Aceita o pedido de conexao de um cliente
    Entrada: o socket do servidor
    Saida: o novo socket da conexao e o endereco do cliente'''
    global entradas

    # estabelece conexao com o proximo cliente
    clisock, endr = sock.accept()
    mensagem = recebeMensagem(clisock) # fica esperando uma mensagem com o id de quem conectou para adicionar no dicionário de conexoes
    
    id = mensagem["id"]

    # registra a nova conexao
    if not conexoes.get(id, None):
        conexoes[id] = clisock
        entradas.append(clisock) # lista de entradas para ouvir novas mensagens

    return clisock, id


def atendeRequisicoes(clisock):
    '''Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
    Entrada: socket da conexao e endereco do cliente
    Saida: '''
    global X, historico, copiaPrimaria

    print("Nova mensagem recebida.")

    mensagem = recebeMensagem(clisock)

    if mensagem["operacao"] == "novaCopiaPrimaria": # mensagem que avisa que o valor e a cópia foi alterada
        copiaPrimaria = mensagem["copiaPrimaria"]
        X = mensagem["novoValor"]
        print("Novo valor de X:", X)
        historico.append((copiaPrimaria["id"], X))
    elif mensagem["operacao"] == "pedeCopia": # mensagem que pede autorização de alteração. Move a cópia primária para lá
        print("Nova copia primaria:", copiaPrimaria)
        copiaPrimaria["id"] = mensagem["id"]
        copiaPrimaria["porta"] = mensagem["porta"]
    else:
        print("mensagem não reconhecida")


def conectaOutrasReplicas():
    '''Estabelece uma conexão com todas as réplicas'''
    global conexoes, meuID, PORT, entradas

    for id in range(1,5):
        porta = 10000+id

        if porta == PORT:
            continue

        if not conexoes.get(id, None):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            sock.connect((HOST, porta))
            conexoes[id] = sock
            entradas.append(sock)
            enviaMensagem({"operacao": "conecta", "id": meuID}, conexoes[id])
                

def avisaMudanca():
    '''Avisa que o valor de X foi alterado pela cópia primaria'''
    global X, meuID, conexoes

    # envia o último X que foi alterado
    for sock in conexoes.values():
        mensagem = {
            "operacao": "novaCopiaPrimaria",
            "copiaPrimaria": {
                "id": meuID,
                "porta": PORT
            },
            "novoValor": X
        }
        enviaMensagem(mensagem, sock)


def imprimeHistorico():
    '''Imprime a cópia local do histórico de alterações'''
    global historico
    print(historico)


def fazCopiaLocal():
    '''Envia uma mensagem para a cópia primária avisando que quer fazer alteração'''
    global copiaPrimaria, meuID, PORT, copiaPrimaria, X

    sockCopiaPrimaria = conexoes[copiaPrimaria["id"]]

    mensagem = {
        "operacao": "pedeCopia",
        "id": meuID,
        "porta": PORT
    }

    enviaMensagem(mensagem, sockCopiaPrimaria)
    print("enviei mensagem")

    copiaPrimaria["id"] = meuID
    copiaPrimaria["porta"] = PORT

    print("agora sou a primaria")


def leValorX():
    '''Lê cópia local de X'''
    global X
    print("Valor de X:", X)


def alteraValorX():
    '''Altera cópia local de X
    Se não for a cópia primária, faz o pedido
    envia a última alteração para todas as réplicas'''
    global X, copiaPrimaria, meuID, historico

    while True:
        if copiaPrimaria["id"] != meuID:
            # pede a copia primária se não for ainda
            # bloqueante
            fazCopiaLocal()

        novoX = input("Digite novo valor de X ('fim' para sair): ")
        if novoX == "fim":
            break

        novoX = int(novoX)

        X = novoX
        historico.append((meuID, novoX))
    
    # avisa os outros que houve mudança
    avisaMudanca()


def main():
    '''Inicializa e implementa o loop principal (infinito) do servidor'''
    global X, meuID, sock, copiaPrimaria

    meuID = int(input("Digite o ID da réplica: "))
    sock = iniciaServidor(meuID)
    
    while True:
        #espera por qualquer entrada de interesse
        leitura, escrita, excecao = select.select(entradas, [], [])
        os.system('cls' if os.name == 'nt' else 'clear')
        print('''Comandos disponíveis:
         'conecta': faz a conexão com outras réplicas
         'conexoes': imprime todas as conexões disponíveis
         'copiaPrimaria': imprime quem é a copia primaria atualmente
         'historico': imprime o historico de alterações
         'ler': lê o valor atual de X
         'alterar': altera o valor de X
         
         Digite um comando:''')
        #tratar todas as entradas prontas
        for pronto in leitura:
            if pronto == sock:  #pedido novo de conexao
                clisock, id = aceitaConexao(sock)
                print ('Conectado com: ', id)
            elif pronto == sys.stdin: #entrada padrao
                cmd = input()
                if cmd == 'fim': #solicitacao de finalizacao do servidor
                    sock.close()
                    sys.exit()
                elif cmd == 'conecta': #conecta com outras réplicas
                    conectaOutrasReplicas()
                elif cmd == 'ler': #le o valor mais atual de X
                    leValorX()
                elif cmd == 'historico': #imprime o historico de alterações
                    imprimeHistorico()
                elif cmd == 'alterar': #altera o valor de X
                    alteraValorX()
                elif cmd == 'conexoes': #imprime todas as conexoes
                    print(conexoes)
                elif cmd == 'copiaPrimaria': #imprime quem é a copia primaria
                    print(copiaPrimaria)
                else:
                    print("Comando não reconhecido.")
            else: # recebe mensagem
                atendeRequisicoes(pronto)
                    

main()