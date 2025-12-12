import os
import sys
import zmq

# garante que conseguimos importar de src/common
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from common.messages import Operacao
from common.state import Banco


def main():
    # cada réplica abre um PULL na porta 6001
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind("tcp://0.0.0.0:6001")

    banco = Banco()
    print("[WORKER] Fila PULL ligada em tcp://0.0.0.0:6001")

    while True:
        data = socket.recv_string()
        op = Operacao.from_json(data)

        print("\n[WORKER] operação recebida da fila:", op)

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

        print("  -> estado atual:", banco)


if __name__ == "__main__":
    main()
