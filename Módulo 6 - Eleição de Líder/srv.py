# Ver documentação em: https://rpyc.readthedocs.io/en/latest/

# Servidor de echo usando RPC
import rpyc  # modulo que oferece suporte a abstracao de RPC
import sys

# servidor que dispara um processo filho a cada conexao
from rpyc.utils.server import ThreadedServer

HOST = "localhost"
porta = 0

# classe que implementa o servico de echo
class Echo(rpyc.Service):
    mapa = {
        10001: {
            "nome": "a",
            "valor": 4,
            "vizinhos": ["a", "j"]
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

    qtdAcks = 0
    qtdEcho = 0

    def __init__(self):
        print("Servidor iniciado. Porta: ", porta)
        self.nome = self.mapa[porta]["nome"]
        self.valor = self.mapa[porta]["valor"]
        self.maiorEncontrado = {"nome": self.nome, "valor": self.valor}
        self.vizinhos = []
        self.conexoes = {}
        self.lider = None
        self.pai = None
        self.eleicao = False
        self.valoresVizinhos = []

        for nome in self.mapa[porta]["vizinhos"]:
            self.vizinhos.append(self.portaPorNome[nome])

        for portaVizinho in self.vizinhos:
            if not self.conexoes[portaVizinho]:
                self.conexoes[portaVizinho] = rpyc.connect(HOST, portaVizinho)

        if porta == self.portaPorNome["a"]:
            self.exposed_inicia_eleicao()
            print(self.maiorEncontrado)


    # executa quando uma conexao eh criada
    def on_connect(self, conn):
        nomeConexao = conn.root.get_nome()
        print("Conexão recebida de:", nomeConexao)
        self.conexoes[self.portaPorNome[nomeConexao]] = conn

    # executa quando uma conexao eh fechada
    def on_disconnect(self, conn):
        print("Conexao finalizada")

    def exposed_get_valor(self):
        return self.valor

    def exposed_get_nome(self):
        return self.nome

    def exposed_ack(self, nome, valor, conn):
        print(self.nome, ": recebi ack de", self.pai)
        self.qtdAcks += 1

        if (self.qtdAcks + self.qtdEcho + 1 == len(self.conexoes)):
            print(self.nome, ": mandei echo no ack para", self.pai)
            rpyc.async_(self.conexoes[self.portaPorNome[self.pai]].root.echo)(self.maiorEncontrado)

    def exposed_echo(self, maiorRecebido):
        self.qtdEcho += 1

        if maiorRecebido["valor"] > self.maiorEncontrado["valor"]:
            self.maiorEncontrado["valor"] = self.maiorRecebido["valor"]
            self.maiorEncontrado["nome"] = self.maiorRecebido["nome"]

        if (self.qtdAcks + self.qtdEcho + 1 == len(self.conexoes)):
            print(self.nome, ": mandei echo no echo para", self.pai)
            rpyc.async_(self.conexoes[self.portaPorNome[self.pai]].root.echo)(self.maiorEncontrado)

    def exposed_probe(self, nome, conn):
        print(self.nome, ": recebi probe de ", nome)
        if not self.eleicao:
            print(self.nome, ": mandei ack para ", nome)
            rpyc.async_(conn.root.ack)(self.nome, self.valor, conn)
            return
        
        if not self.pai:
            self.pai = nome
        
        self.eleicao = True

        for vizinho in self.mapa[porta]["vizinhos"]:
            if vizinho != self.pai:
                print(self.nome, ": mandei probe para ", vizinho)
                rpyc.async_(self.conexoes[self.portaPorNome[vizinho]].root.probe)()

        if (len(self.conexoes) == 1):
            print(self.nome, ": mandei echo no probe para", self.pai)
            rpyc.async_(self.conexoes[self.portaPorNome[self.pai]].root.echo)(self.maiorEncontrado)

    def exposed_inicia_eleicao(self):
        self.eleicao = True

        for vizinho in self.mapa[porta]["vizinhos"]:
            print(self.nome, ": mandei probe para ", vizinho)
            rpyc.async_(self.conexoes[self.portaPorNome[vizinho]].root.probe)()


porta = int(sys.argv[1])
ThreadedServer(Echo, port=int(sys.argv[1])).start()
