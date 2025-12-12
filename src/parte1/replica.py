import os
import sys
import zmq

# adiciona a pasta "src" ao caminho de imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from common.messages import Operacao
from common.state import Banco


def main():
    # IP PÚBLICO do CLIENTE (server01)
    ip_cliente = "100.48.156.203"  # mesmo IP que as réplicas usam

    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    # conecta na porta 5555 do cliente
    socket.connect(f"tcp://{ip_cliente}:5555")

    # recebe todas as mensagens (assinatura vazia)
    socket.setsockopt_string(zmq.SUBSCRIBE, "")

    banco = Banco()
    print(f"[REPLICA] Conectado ao cliente em tcp://{ip_cliente}:5555")

    while True:
        # espera operação vinda do cliente
        data = socket.recv_string()
        op = Operacao.from_json(data)

        print("\n[REPLICA] operação recebida:", op)

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
