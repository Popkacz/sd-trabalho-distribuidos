import rpyc

# IP público do servidor RPC (client/server01)
RPC_SERVER_IP = "100.48.156.203"


def main():
    print("[CLIENTE RPC] Conectando ao servidor RPC...")
    conn = rpyc.connect(RPC_SERVER_IP, 50051)
    bank = conn.root

    while True:
        print("\nOperações RPC:")
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
            resp = bank.depositar(conta, valor)
        elif op == "2":
            conta = input("Conta origem: ")
            valor = float(input("Valor: "))
            resp = bank.sacar(conta, valor)
        elif op == "3":
            origem = input("Conta origem: ")
            destino = input("Conta destino: ")
            valor = float(input("Valor: "))
            resp = bank.transferir(origem, destino, valor)
        else:
            print("Opção inválida.")
            continue

        print("[CLIENTE RPC] Resposta do servidor:", resp)

    conn.close()
    print("[CLIENTE RPC] Encerrado.")


if __name__ == "__main__":
    main()
