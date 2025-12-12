import os
import sys
import json
import zmq

# permite importar de src/common
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from common.messages import Operacao
from common.state import Banco


def main():
    # IP PÚBLICO do sequenciador (server01)
    ip_sequenciador = "100.48.156.203"

    context = zmq.Context()
    sub_socket = context.socket(zmq.SUB)

    # conecta no PUB do sequenciador (porta 6003)
    sub_socket.connect(f"tcp://{ip_sequenciador}:6003")
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

    banco = Banco()
    print(f"[R-TOTAL] Conectado ao sequenciador em tcp://{ip_sequenciador}:6003")

    proximo_seq_esperado = 1
    pendentes: dict[int, Operacao] = {}

    while True:
        data = sub_socket.recv_string()
        envelope = json.loads(data)
        seq = envelope["seq"]
        op_json = envelope["op"]
        op = Operacao.from_json(op_json)

        print(f"\n[R-TOTAL] recebido seq={seq}: {op}")
        pendentes[seq] = op

        # entrega em ordem: enquanto houver a próxima seq, aplica
        while proximo_seq_esperado in pendentes:
            op_entregar = pendentes.pop(proximo_seq_esperado)
            print(f"[R-TOTAL] entregando seq={proximo_seq_esperado}: {op_entregar}")

            if op_entregar.tipo == "DEPOSITO":
                banco.depositar(op_entregar.conta_origem, op_entregar.valor)
            elif op_entregar.tipo == "SAQUE":
                ok = banco.sacar(op_entregar.conta_origem, op_entregar.valor)
                if not ok:
                    print("  -> saque recusado (saldo insuficiente)")
            elif op_entregar.tipo == "TRANSFERENCIA":
                ok = banco.transferir(
                    op_entregar.conta_origem,
                    op_entregar.conta_destino,
                    op_entregar.valor,
                )
                if not ok:
                    print("  -> transferência recusada (saldo insuficiente)")
            else:
                print("  -> tipo de operação desconhecido:", op_entregar.tipo)

            print("  -> estado atual:", banco)
            proximo_seq_esperado += 1


if __name__ == "__main__":
    main()
