# Ver documentação em: https://rpyc.readthedocs.io/en/latest/

# Cliente de echo usando RPC
import rpyc  # modulo que oferece suporte a abstracao de RPC

# endereco do servidor de echo
SERVIDOR = 'localhost'
PORTA = 10001


def iniciaConexao():
    '''Conecta-se ao servidor.
    Saida: retorna a conexao criada.'''
    conn = rpyc.connect(SERVIDOR, PORTA)

    print(type(conn.root))  # mostra que conn.root eh um stub de cliente
    # exibe o nome da classe (servico) oferecido
    print(conn.root.get_service_name())

    return conn


def fazRequisicoes(conn):
    '''Faz requisicoes ao servidor e exibe o resultado.
    Entrada: conexao estabelecida com o servidor'''
    # le as mensagens do usuario ate ele digitar 'fim'
    while True:
        msg = input("Digite uma mensagem ('fim' para terminar):")
        if msg == 'fim':
            break

        # envia a mensagem do usuario para o servidor
        ret = conn.root.exposed_echo(msg)

        # imprime a mensagem recebida
        print(ret)

    # encerra a conexao
    conn.close()


def main():
    ports = {
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

    conn = rpyc.connect("localhost", ports["b"])
    #conn.root.set_server(nome="b", valor=6)
    conn.root.conecta("localhost", ports["a"])
    conn.root.conecta("localhost", ports["g"])
    conn.root.conecta("localhost", ports["c"])

    conn = rpyc.connect("localhost", ports["c"])
    #conn.root.set_server(nome="c", valor=3)
    conn.root.conecta("localhost", ports["b"])
    conn.root.conecta("localhost", ports["d"])
    conn.root.conecta("localhost", ports["e"])

    conn = rpyc.connect("localhost", ports["d"])
    #conn.root.set_server(nome="d", valor=2)
    conn.root.conecta("localhost", ports["c"])
    conn.root.conecta("localhost", ports["e"])
    conn.root.conecta("localhost", ports["f"])

    conn = rpyc.connect("localhost", ports["e"])
    #conn.root.set_server(nome="e", valor=1)
    conn.root.conecta("localhost", ports["c"])
    conn.root.conecta("localhost", ports["d"])
    conn.root.conecta("localhost", ports["g"])
    conn.root.conecta("localhost", ports["f"])

    conn = rpyc.connect("localhost", ports["f"])
    #conn.root.set_server(nome="f", valor=4)
    conn.root.conecta("localhost", ports["d"])
    conn.root.conecta("localhost", ports["e"])
    conn.root.conecta("localhost", ports["i"])

    conn = rpyc.connect("localhost", ports["g"])
    #conn.root.set_server(nome="g", valor=2)
    conn.root.conecta("localhost", ports["b"])
    conn.root.conecta("localhost", ports["e"])
    conn.root.conecta("localhost", ports["h"])
    conn.root.conecta("localhost", ports["j"])

    conn = rpyc.connect("localhost", ports["h"])
    #conn.root.set_server(nome="h", valor=8)
    conn.root.conecta("localhost", ports["g"])
    conn.root.conecta("localhost", ports["i"])

    conn = rpyc.connect("localhost", ports["i"])
    #conn.root.set_server(nome="i", valor=5)
    conn.root.conecta("localhost", ports["f"])
    conn.root.conecta("localhost", ports["h"])

    conn = rpyc.connect("localhost", ports["j"])
    #conn.root.set_server(nome="j", valor=4)
    conn.root.conecta("localhost", ports["a"])
    conn.root.conecta("localhost", ports["g"])

    conn = rpyc.connect("localhost", ports["a"])
    #conn.root.set_server(nome="a", valor=4)
    conn.root.conecta("localhost", ports["b"])
    conn.root.conecta("localhost", ports["j"])
    lider = conn.root.inicia_eleicao()
    print("\n\n\nLider encontrado: ", lider)


# executa o cliente
if __name__ == "__main__":
    main()
