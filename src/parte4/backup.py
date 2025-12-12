import os
import sys
import zmq

# permite importar de src/common
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from common.messages import Operacao
from common.state import Banco


def main():
    # IP do primário (replica01)
    ip_primary = "35.171.78.105"

    context = zmq.Context()
    sub_socket = context.socket(zmq.SUB)

    # conecta ao PUB do primário (porta 6005)
    sub_socket.connect(f"tcp://{ip_primary}:6005")
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

    banco = Banco()
    print(f"[BACKUP] Conectado ao primário em tcp://{ip_primary}:6005")

    while True:
        data = sub_socket.recv_string()
        op = Operacao.from_json(data)

        print("\n[BACKUP] atualização recebida:", op)

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

        print("  -> estado atual (BACKUP):", banco)


if __name__ == "__main__":
    main()
