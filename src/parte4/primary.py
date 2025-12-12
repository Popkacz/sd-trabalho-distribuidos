import os
import sys
import zmq

# permite importar de src/common
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from common.messages import Operacao
from common.state import Banco


def main():
    context = zmq.Context()

    # socket REP: recebe pedidos dos clientes (porta 6004)
    rep_socket = context.socket(zmq.REP)
    rep_socket.bind("tcp://0.0.0.0:6004")
    print("[PRIMARY] REP ouvindo em tcp://0.0.0.0:6004")

    # socket PUB: envia atualizações para backups (porta 6005)
    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind("tcp://0.0.0.0:6005")
    print("[PRIMARY] PUB publicando atualizações em tcp://0.0.0.0:6005")

    banco = Banco()

    while True:
        data = rep_socket.recv_string()
        op = Operacao.from_json(data)
        print("\n[PRIMARY] operação recebida do cliente:", op)

        # aplica a operação localmente
        if op.tipo == "DEPOSITO":
            banco.depositar(op.conta_origem, op.valor)
        elif op.tipo == "SAQUE":
            ok = banco.sacar(op.conta_origem, op.valor)
            if not ok:
                print("  -> saque recusado (saldo insuficiente)")
        elif op.tipo == "TRANSFERENCIA":
            ok = banco.transferir(op.conta_origem, op.conta_destino, op.valor)
            if not ok:
                print("  -> transferência recusada (saldo insuficiente)")
        else:
            print("  -> tipo de operação desconhecido:", op.tipo)

        print("  -> estado atual (PRIMARY):", banco)

        # envia a operação para os backups
        pub_socket.send_string(op.to_json())
        print("[PRIMARY] atualização enviada aos backups")

        # responde ao cliente
        rep_socket.send_string("OK")


if __name__ == "__main__":
    main()
