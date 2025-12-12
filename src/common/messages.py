import json
import uuid
from dataclasses import dataclass, asdict

@dataclass
class Operacao:
    id_msg: str
    tipo: str           # "DEPOSITO", "SAQUE", "TRANSFERENCIA"
    conta_origem: str | None = None
    conta_destino: str | None = None
    valor: float | None = None

    @staticmethod
    def nova(tipo, conta_origem=None, conta_destino=None, valor=None):
        return Operacao(
            id_msg=str(uuid.uuid4()),
            tipo=tipo,
            conta_origem=conta_origem,
            conta_destino=conta_destino,
            valor=valor,
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(data: str) -> "Operacao":
        return Operacao(**json.loads(data))

