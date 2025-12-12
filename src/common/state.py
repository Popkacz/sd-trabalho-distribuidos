class Banco:
    def __init__(self):
        # dicionário conta -> saldo
        self.contas: dict[str, float] = {}

    def criar_conta(self, conta: str):
        if conta not in self.contas:
            self.contas[conta] = 0.0

    def depositar(self, conta: str, valor: float):
        self.criar_conta(conta)
        self.contas[conta] += valor

    def sacar(self, conta: str, valor: float) -> bool:
        self.criar_conta(conta)
        if self.contas[conta] >= valor:
            self.contas[conta] -= valor
            return True
        return False

    def transferir(self, origem: str, destino: str, valor: float) -> bool:
        if self.sacar(origem, valor):
            self.depositar(destino, valor)
            return True
        return False

    def saldo(self, conta: str) -> float:
        self.criar_conta(conta)
        return self.contas[conta]

    def __repr__(self):
        return f"Banco({self.contas})"

