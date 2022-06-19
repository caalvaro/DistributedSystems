# Ver documentação em: https://rpyc.readthedocs.io/en/latest/

# Servidor de echo usando RPC
import rpyc  # modulo que oferece suporte a abstracao de RPC
import sys

# servidor que dispara um processo filho a cada conexao
from rpyc.utils.server import OneShotServer


# classe que implementa o servico de echo
class Echo(rpyc.Service):
    def __init__(self):
        self.nome = None
        self.valor = None
        self.conexoes = {}
        self.lider = None
        self.pai = None
        self.msg = None

    # executa quando uma conexao eh criada
    def on_connect(self, conn):
        pass

    # executa quando uma conexao eh fechada

    def on_disconnect(self, conn):
        if self.conexoes[conn] == self.pai:
            self.pai = None

        self.conexoes.pop(conn)
        print("Conexao finalizada:")

    # imprime e ecoa a mensagem recebida
    def exposed_echo(self, msg):
        print(msg)
        return msg

    def exposed_set_server(self, nome=-1, valor=-1):
        self.nome = nome
        self.valor = valor
        print("Servidor setado", self.nome, self.valor)

    def exposed_get_valor(self):
        return self.valor

    def exposed_get_nome(self):
        return self.nome

    def exposed_election(self, nome, valor):
        lider_provisorio = {"nome": self.nome, "valor": self.valor}

        if self.pai == None:
            self.pai = (nome, valor)
        else:
            return "ack"

        print("Explorando", nome)
        print("conexões de ", self.nome, self.conexoes.values())

        for (conn, info) in self.conexoes.items():
            if info == self.pai:
                continue

            resposta = conn.root.election(info[0], info[1])

            if resposta == "ack":
                continue

            if (resposta["valor"] is None or lider_provisorio["valor"] is None):
                print("\n\n\n\nErro none", resposta["valor"],
                      lider_provisorio["valor"], "\n\n\n\n")

            if resposta["valor"] > lider_provisorio["valor"]:
                print(self.nome, ": Achei um maior!!",
                      resposta["nome"], resposta["valor"])
                lider_provisorio["valor"] = resposta["valor"]
                lider_provisorio["nome"] = resposta["nome"]

        return lider_provisorio

    def exposed_inicia_eleicao(self):
        lider = self.exposed_election(self.nome, self.valor)

        self.inicia_broadcast(lider)

        return lider

    def exposed_broadcast(self, msg):
        for conn in self.conexoes:
            if self.msg == msg:
                continue

            conn.root.broadcast(msg)

    def exposed_get_conn(self, nome, valor):
        for key, value in self.conexoes.items():
            if value == (nome, valor):
                return key
        return None

    def inicia_broadcast(self, msg):
        self.msg = msg
        self.exposed_broadcast(msg)

    def exposed_conecta(self, endereco, porta):
        conn = rpyc.connect(endereco, porta)
        conexao = conn.root.get_conn(self.nome, self.valor)

        nome_conexao = conn.root.get_nome()
        valor_conexao = conn.root.get_valor()

        if not conexao:
            self.conexoes[conn] = (nome_conexao, valor_conexao)
        else:
            self.conexoes[conexao] = (nome_conexao, valor_conexao)

        print(self.nome, ": Conectei com", porta,
              (nome_conexao, valor_conexao))


# dispara o servidor
if __name__ == "__main__":
    OneShotServer(Echo, port=int(sys.argv[1])).start()
