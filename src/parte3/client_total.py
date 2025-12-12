import os
import sys
import zmq
import time

# permite importar de src/common
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from common.messages import Operacao

# IP do sequenciador (server01)
SEQ_IP = "100.48.156.203"
SEQ_PORT = 6002


def main():
    context = zmq.Context()
    req_socket = context.socket(zmq.REQ)

    req_socket.connect(f"tcp://{SEQ_IP}:{SEQ_PORT}")
    print(f"[CLIENTE-TOTAL] Conectado ao sequenciador em tcp://{SEQ_IP}:{SEQ_PORT}")

    time.sleep(1)

    while True:
        print("\nOperações (ordenadas via sequenciador):")
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
            operacao = Operacao.nova("DEPOSITO", conta_origem=conta, valor=valor)
        elif op == "2":
            conta = input("Conta origem: ")
            valor = float(input("Valor: "))
            operacao = Operacao.nova("SAQUE", conta_origem=conta, valor=valor)
        elif op == "3":
            origem = input("Conta origem: ")
            destino = input("Conta destino: ")
            valor = float(input("Valor: "))
            operacao = Operacao.nova(
                "TRANSFERENCIA",
                conta_origem=origem,
                conta_destino=destino,
                valor=valor,
            )
        else:
            print("Opção inválida.")
            continue

        req_socket.send_string(operacao.to_json())
        ack = req_socket.recv_string()
        print("[CLIENTE-TOTAL] Resposta do sequenciador:", ack)

    req_socket.close()
    context.term()


if __name__ == "__main__":
    main()
