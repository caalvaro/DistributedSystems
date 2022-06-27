# Ver documentação em: https://rpyc.readthedocs.io/en/latest/

# Cliente de echo usando RPC
import rpyc  # modulo que oferece suporte a abstracao de RPC

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

# usando o exemplo dos slides
# configura nó b
conn = rpyc.connect("localhost", ports["b"])
conn.root.conecta("localhost", ports["a"])
conn.root.conecta("localhost", ports["g"])
conn.root.conecta("localhost", ports["c"])
conn.close()

# configura nó c
conn = rpyc.connect("localhost", ports["c"])
conn.root.conecta("localhost", ports["b"])
conn.root.conecta("localhost", ports["d"])
conn.root.conecta("localhost", ports["e"])
conn.close()

# configura nó d
conn = rpyc.connect("localhost", ports["d"])
conn.root.conecta("localhost", ports["c"])
conn.root.conecta("localhost", ports["e"])
conn.root.conecta("localhost", ports["f"])
conn.close()

# configura nó e
conn = rpyc.connect("localhost", ports["e"])
conn.root.conecta("localhost", ports["c"])
conn.root.conecta("localhost", ports["d"])
conn.root.conecta("localhost", ports["g"])
conn.root.conecta("localhost", ports["f"])
conn.close()

# configura nó f
conn = rpyc.connect("localhost", ports["f"])
conn.root.conecta("localhost", ports["d"])
conn.root.conecta("localhost", ports["e"])
conn.root.conecta("localhost", ports["i"])
conn.close()

# configura nó g
conn = rpyc.connect("localhost", ports["g"])
conn.root.conecta("localhost", ports["b"])
conn.root.conecta("localhost", ports["e"])
conn.root.conecta("localhost", ports["h"])
conn.root.conecta("localhost", ports["j"])
conn.close()

# configura nó h
conn = rpyc.connect("localhost", ports["h"])
conn.root.conecta("localhost", ports["g"])
conn.root.conecta("localhost", ports["i"])
conn.close()

# configura nó i
conn = rpyc.connect("localhost", ports["i"])
conn.root.conecta("localhost", ports["f"])
conn.root.conecta("localhost", ports["h"])
conn.close()

# configura nó j
conn = rpyc.connect("localhost", ports["j"])
conn.root.conecta("localhost", ports["a"])
conn.root.conecta("localhost", ports["g"])
conn.close()

# configura nó a
conn = rpyc.connect("localhost", ports["a"])
conn.root.conecta("localhost", ports["b"])
conn.root.conecta("localhost", ports["j"])

lider = conn.root.inicia_eleicao()  # inicia a eleição pelo nó a

conn.close()

print("\n\n\nLider encontrado: ", lider)
