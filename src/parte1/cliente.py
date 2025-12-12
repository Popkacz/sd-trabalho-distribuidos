import os
import sys
import time
import zmq

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from common.messages import Operacao


def main():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)

    socket.bind("tcp://0.0.0.0:5555")
    print("[CLIENTE] Publicando operações em tcp://0.0.0.0:5555")

    # dá tempo pros SUBs conectarem
    time.sleep(3)

    while True:
        print("\nOperações:")
        print(" 1 - Depósito")
        print(" 2 - Saque")
        print(" 3 - Transferência")
        print(" 0 - Sair")
        op = input("Escolha: ").strip()

        if op == "0":
            break

        if op == "1":
            conta = input("Conta destino: ")
            valor = float(input("Valor: "))
            msg = Operacao.nova("DEPOSITO", conta_origem=conta, valor=valor)
        elif op == "2":
            conta = input("Conta origem: ")
            valor = float(input("Valor: "))
            msg = Operacao.nova("SAQUE", conta_origem=conta, valor=valor)
        elif op == "3":
            origem = input("Conta origem: ")
            destino = input("Conta destino: ")
            valor = float(input("Valor: "))
            msg = Operacao.nova(
                "TRANSFERENCIA",
                conta_origem=origem,
                conta_destino=destino,
                valor=valor,
            )
        else:
            print("Opção inválida.")
            continue

        socket.send_string(msg.to_json())
        print("[CLIENTE] operação enviada:", msg)
        time.sleep(0.1)  # pequeno intervalo

    socket.close()
    context.term()


if __name__ == "__main__":
    main()
