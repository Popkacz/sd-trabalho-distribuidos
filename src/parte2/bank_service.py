import os
import sys
import zmq
import rpyc

# garantir imports de src/common
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from common.messages import Operacao


# IPs públicos das réplicas
REPLICAS = [
    "35.171.78.105",   # replica01
    "100.48.122.21",   # replica02
]


class BankService(rpyc.Service):
    def on_connect(self, conn):
        print("[RPC] Cliente conectado")

    def on_disconnect(self, conn):
        print("[RPC] Cliente desconectado")

    def _enviar_para_fila(self, op: Operacao):
        # enviamos a mesma operação para todas as réplicas
        data = op.to_json()
        for sock in self.push_sockets:
            sock.send_string(data)
        print("[RPC] operação enfileirada para réplicas:", op)

    # métodos expostos via RPC (client chama conn.root.depositar(...))
    def exposed_depositar(self, conta: str, valor: float):
        op = Operacao.nova("DEPOSITO", conta_origem=conta, valor=valor)
        self._enviar_para_fila(op)
        return f"DEPOSITO enfileirado: {op.id_msg}"

    def exposed_sacar(self, conta: str, valor: float):
        op = Operacao.nova("SAQUE", conta_origem=conta, valor=valor)
        self._enviar_para_fila(op)
        return f"SAQUE enfileirado: {op.id_msg}"

    def exposed_transferir(self, conta_origem: str, conta_destino: str, valor: float):
        op = Operacao.nova(
            "TRANSFERENCIA",
            conta_origem=conta_origem,
            conta_destino=conta_destino,
            valor=valor,
        )
        self._enviar_para_fila(op)
        return f"TRANSFERENCIA enfileirada: {op.id_msg}"


def main():
    # prepara ZeroMQ PUSH para as filas das réplicas
    context = zmq.Context()
    push_sockets = []
    for ip in REPLICAS:
        sock = context.socket(zmq.PUSH)
        sock.connect(f"tcp://{ip}:6001")
        push_sockets.append(sock)
        print(f"[RPC] Conectado à fila da réplica em tcp://{ip}:6001")

    # 'injeção' da lista nos objetos service
    BankService.push_sockets = push_sockets

    from rpyc.utils.server import ThreadedServer
    # servidor RPC ouvindo na porta 50051
    t = ThreadedServer(BankService, port=50051, protocol_config={"allow_public_attrs": True})
    print("[RPC] Servidor RPC ouvindo na porta 50051")
    t.start()


if __name__ == "__main__":
    main()
