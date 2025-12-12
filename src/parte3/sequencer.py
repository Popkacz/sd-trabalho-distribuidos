import os
import sys
import json
import zmq

# permite importar de src/common
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from common.messages import Operacao


def main():
    context = zmq.Context()

    # socket REP: recebe pedidos dos clientes na porta 6002
    rep_socket = context.socket(zmq.REP)
    rep_socket.bind("tcp://0.0.0.0:6002")
    print("[SEQ] REP ouvindo em tcp://0.0.0.0:6002")

    # socket PUB: multicast para réplicas na porta 6003
    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind("tcp://0.0.0.0:6003")
    print("[SEQ] PUB publicando em tcp://0.0.0.0:6003")

    seq = 0  # número de sequência global

    while True:
        # recebe operação do cliente (JSON de Operacao)
        data = rep_socket.recv_string()
        op = Operacao.from_json(data)
        seq += 1

        # envelope com número de sequência + operação
        envelope = {
            "seq": seq,
            "op": op.to_json(),
        }

        pub_socket.send_string(json.dumps(envelope))
        print(f"[SEQ] seq={seq} enviado para réplicas -> {op}")

        # responde ao cliente
        rep_socket.send_string(f"OK seq={seq}")

if __name__ == "__main__":
    main()
