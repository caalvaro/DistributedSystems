# Ver documentação em: https://rpyc.readthedocs.io/en/latest/

# Servidor de echo usando RPC
import rpyc  # modulo que oferece suporte a abstracao de RPC
import sys

# servidor que dispara um processo filho a cada conexao
from rpyc.utils.server import ThreadedServer

HOST = "localhost"
# porta que o nó irá escutar, definida pelo argumento na hora de executar o programa
minhaPorta = int(sys.argv[1])

# mapa do grafo com os nós
mapa = {
    10001: {
        "nome": "a",
        "valor": 4,
        "vizinhos": ["b", "j"]
    },
    10002: {
        "nome": "b",
        "valor": 6,
        "vizinhos": ["a", "c", "g"]
    },
    10003: {
        "nome": "c",
        "valor": 3,
        "vizinhos": ["b", "d", "e"]
    },
    10004: {
        "nome": "d",
        "valor": 2,
        "vizinhos": ["c", "e", "f"]
    },
    10005: {
        "nome": "e",
        "valor": 1,
        "vizinhos": ["c", "d", "f", "g"]
    },
    10006: {
        "nome": "f",
        "valor": 4,
        "vizinhos": ["d", "e", "i"]
    },
    10007: {
        "nome": "g",
        "valor": 2,
        "vizinhos": ["b", "e", "h", "j"]
    },
    10008: {
        "nome": "h",
        "valor": 8,
        "vizinhos": ["g", "i"]
    },
    10009: {
        "nome": "i",
        "valor": 5,
        "vizinhos": ["f", "h"]
    },
    10010: {
        "nome": "j",
        "valor": 4,
        "vizinhos": ["a", "g"]
    }
}

# dicionário com as portas usadas por cada nó
portaPorNome = {
    "a": 10001,
    "b": 10002,
    "c": 10003,
    "d": 10004,
    "e": 10005,
    "f": 10006,
    "g": 10007,
    "h": 10008,
    "i": 10009,
    "j": 10010,
}

# dicionário com as conexões do nó
conexoes = {}

# atributos do nó
meuNome = mapa[minhaPorta]["nome"]
meuValor = mapa[minhaPorta]["valor"]
meusVizinhos = mapa[minhaPorta]["vizinhos"]
meuPai = None

# variáveis da eleição
lider = None
eleicao = False
maiorEncontrado = {"nome": meuNome, "valor": meuValor}
qtdAcks = 0
qtdEcho = 0


# classe que implementa o servico de echo
class Echo(rpyc.Service):

    def __init__(self):
        print("Servidor iniciado. Porta: ", minhaPorta)

    def on_connect(self, conn):
        '''
        A cada nova conexão recebida, o servidor adiciona numa lista de conexões
        O try utilizado é devido a forma que eu testo, onde crio um nó (arquivo cli.py) que executa configura todos os outros nós,
        dessa forma eu evito chamar o conn.root.get_nome() pois ele não tem essa propriedade
        '''
        global conexoes
        try:
            nomeConexao = conn.root.get_nome()
            print("Conexão recebida de:", nomeConexao)
            conexoes[portaPorNome[nomeConexao]] = conn
        except:
            pass

    # executa quando uma conexao eh fechada
    def on_disconnect(self, conn):
        print("Conexao finalizada")

    def exposed_get_valor(self):
        '''
        Retorna o atributo do nó para o algoritmo de eleição
        '''
        return meuValor

    def exposed_get_nome(self):
        '''
        Retorna o nome do nó
        '''
        return meuNome

    def exposed_ack(self, nome, valor):
        '''
        Função para a mensagem ack

        A quantidade de acks é incrementada e é verificado se é momento do nó fazer um echo
        '''
        global qtdEcho, qtdAcks, conexoes

        print(meuNome, ": recebi ack de", nome)
        qtdAcks += 1

        # A condição para fazer echo é que, para todos os probes que esse nó vai fazer, ele vai receber um ack ou um echo
        # Como ele faz um probe para todas as conexões menos para o pai, contamos apenas len(conexoes) - 1
        # Então quando qtdAcks + qtdEcho == len(conexoes) - 1, significa que esse nó recebeu todas as mensagens que ele esperava
        if (qtdAcks + qtdEcho == len(conexoes) - 1):
            if meuPai == None:  # quando é momento do nó que começou a eleição fazer echo, o algoritmo terminou
                print("Fim do algoritmo")
                return
            print(meuNome, ": mandei echo no ack para", meuPai)
            conexoes[portaPorNome[meuPai]].root.echo(maiorEncontrado)

    def exposed_echo(self, maiorRecebido):
        '''
        Função para a mensagem echo

        A quantidade de echos é incrementada e é verificado se é momento do nó fazer um echo
        Assim que o nó recebe um echo, ele verifica se o valor recebido é maior que o que ele tem armazenado
        '''
        global qtdEcho, qtdAcks, conexoes, maiorEncontrado
        qtdEcho += 1

        if maiorRecebido["valor"] > maiorEncontrado["valor"]:
            maiorEncontrado["valor"] = maiorRecebido["valor"]
            maiorEncontrado["nome"] = maiorRecebido["nome"]

        # A condição para fazer echo é que, para todos os probes que esse nó vai fazer, ele vai receber um ack ou um echo
        # Como ele faz um probe para todas as conexões menos para o pai, contamos apenas len(conexoes) - 1
        # Então quando qtdAcks + qtdEcho == len(conexoes) - 1, significa que esse nó recebeu todas as mensagens que ele esperava
        if (qtdAcks + qtdEcho == len(conexoes) - 1):
            if meuPai == None:  # quando é momento do nó que começou a eleição fazer echo, o algoritmo terminou
                print("Fim do algoritmo")
                return
            print(meuNome, ": mandei echo no echo para", meuPai)
            conexoes[portaPorNome[meuPai]].root.echo(maiorEncontrado)

    def exposed_probe(self, nome):
        '''
        Função para a mensagem probe
        '''
        global eleicao, meuPai, conexoes, lider

        print(meuNome, ": recebi probe de ", nome)
        conn = conexoes[portaPorNome[nome]]

        if eleicao:  # se já está numa eleição, manda um ack
            print(meuNome, ": mandei ack para ", nome)
            conn.root.ack(meuNome, meuValor)
            return

        if not meuPai:  # se não tem pai, admite o nó que mandou o probe como pai
            meuPai = nome

        # quando tiver uma eleição acontecendo, a rede fica temporariamente sem lider
        eleicao = True
        lider = None

        # manda probe para todos os vizinhos
        for vizinho in meusVizinhos:
            if vizinho != meuPai:
                print(meuNome, ": mandei probe para ", vizinho)
                conexoes[portaPorNome[vizinho]].root.probe(meuNome)

        # A condição para fazer echo é que, para todos os probes que esse nó vai fazer, ele vai receber um ack ou um echo
        # Como ele faz um probe para todas as conexões menos para o pai, contamos apenas len(conexoes) - 1
        # Então quando qtdAcks + qtdEcho == len(conexoes) - 1, significa que esse nó recebeu todas as mensagens que ele esperava
        if (qtdAcks + qtdEcho + 1 == len(conexoes)):
            if meuPai == None:  # quando é momento do nó que começou a eleição fazer echo, o algoritmo terminou
                print("Fim do algoritmo.")
                return
            print(meuNome, ": mandei echo no probe para", meuPai)
            conexoes[portaPorNome[meuPai]].root.echo(maiorEncontrado)

    def exposed_inicia_eleicao(self):
        '''
        Função para o nó iniciar uma eleição

        Para o teste, ela é chamada no arquivo cli.py, após a configuração dos servidores
        '''
        global eleicao, lider
        eleicao = True

        # envia probe para todos os vizinhos
        for vizinho in meusVizinhos:
            print(meuNome, ": mandei probe para ", vizinho)
            conexoes[portaPorNome[vizinho]].root.probe(meuNome)

        lider = maiorEncontrado
        eleicao = False

        # avisa os vizinhos de um novo lider
        for vizinho in meusVizinhos:
            print(meuNome, ": avisando novo lider: ", vizinho)
            conexoes[portaPorNome[vizinho]].root.lider(maiorEncontrado)

        return maiorEncontrado

    def exposed_lider(self, novoLider):
        '''
        Função para o nó avisar seus vizinhos sobre o novo líder recebido

        Para o teste, ela é chamada no arquivo cli.py, após a configuração dos servidores
        '''
        global lider, eleicao, meuPai

        if lider:  # se o nó já tiver um lider, retorna
            print(meuNome, ": já fui avisado do líder.")
            return

        lider = novoLider

        print(meuNome, ": novo lider rebido: ", novoLider)

        for vizinho in meusVizinhos:
            if vizinho != meuPai:
                print(meuNome, ": avisando novo lider: ", vizinho)
                conexoes[portaPorNome[vizinho]].root.lider(novoLider)

        meuPai = None
        eleicao = False
        return

    def exposed_conecta(self, endereco, porta):
        '''
        Função para configurar as conexões de cada nó

        Para o teste, ela é chamada no arquivo cli.py
        Foi a forma que encontrei de configurar como que os nós se relacionavam
        '''
        global conexoes

        # retorna se já tiver uma conexão ativa com esse nó
        if conexoes.get(porta, None):
            return

        conn = rpyc.connect(endereco, porta)

        nome_conexao = conn.root.get_nome()
        valor_conexao = conn.root.get_valor()

        conexoes[porta] = conn

        print(meuNome, ": Conectei com", porta,
              (nome_conexao, valor_conexao))


ThreadedServer(Echo, port=int(sys.argv[1])).start()
