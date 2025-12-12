# Trabalho de Sistemas Distribuídos  
## Banco Replicado em Ambiente AWS

Este repositório contém uma aplicação didática de **banco de dados replicado** construída para a disciplina de Sistemas Distribuídos.  
O mesmo cenário de aplicação (um “banco” simples) é implementado em **quatro arquiteturas diferentes**, cada uma destacando um conceito clássico da área:

1. **Multicast com ZeroMQ**  
2. **RPC + Fila de Mensagens**  
3. **Ordenação Total com Sequenciador Central**  
4. **Primário–Backup com coordenação mais leve**

---

## 1. Objetivo da Aplicação

A aplicação simula um **sistema bancário distribuído**, em que diversas réplicas mantêm uma cópia de uma base de contas.  
O foco **não** é em regras bancárias reais, mas em:

- Como **comunicar processos distribuídos**.  
- Como **replicar estado** entre processos (consistência).  
- Como diferentes **arquiteturas de comunicação e coordenação** impactam o sistema.

### 1.1 Funcionalidades

Em todas as partes, a aplicação suporta as mesmas operações:

- `DEPOSITO` – Aumenta o saldo de uma conta.  
- `SAQUE` – Diminui o saldo, se houver saldo suficiente.  
- `TRANSFERENCIA` – Move saldo de uma conta origem para uma destino.

Essas operações:

- São representadas pela classe `Operacao` (`src/common/messages.py`).  
- São **serializadas em JSON** para trafegar na rede.  
- São aplicadas sobre um objeto `Banco` (`src/common/state.py`) em cada réplica.

---

## 2. Arquitetura Física (AWS)

A aplicação é executada em 3 instâncias EC2:

- **Client / Orquestrador**
  - Executa os clientes das Partes 1, 2, 3 e 4.
  - Executa serviços centrais:
    - Servidor RPC (Parte 2).
    - Sequenciador (Parte 3).

- **Replica 01**
  - Parte 1: réplica simples (SUB).
  - Parte 2: worker da fila (PULL).
  - Parte 3: réplica com ordenação total.
  - Parte 4: **Primário** (REP/PUB).

- **Replica 02**
  - Parte 1: réplica simples (SUB).
  - Parte 2: worker da fila (PULL).
  - Parte 3: réplica com ordenação total.
  - Parte 4: **Backup** (SUB).

### 2.1 Portas Utilizadas (Security Group)

Para permitir a comunicação entre as instâncias, o Security Group foi configurado com as portas:

- **Parte 1**  
  - `5555/TCP` – Cliente (PUB) → Réplicas (SUB)
- **Parte 2**  
  - `50051/TCP` – RPC RPyC (cliente ↔ servidor)  
  - `6001/TCP` – Fila PULL nas réplicas (workers)
- **Parte 3**  
  - `6002/TCP` – Sequenciador (REQ/REP com o cliente)  
  - `6003/TCP` – Sequenciador (PUB/SUB para réplicas)
- **Parte 4**  
  - `6004/TCP` – Primário (REQ/REP com cliente)  
  - `6005/TCP` – Primário (PUB/SUB para backups)

No ambiente de laboratório, foi usada origem `0.0.0.0/0` por simplicidade.

---

## 3. Modelo Lógico da Aplicação

### 3.1. Estado – `Banco` (`src/common/state.py`)

Representa a base de contas em memória:

- Estrutura interna: `dict[str, float]` mapeando `conta → saldo`.
- Operações principais:
  - `criar_conta(conta)`
  - `depositar(conta, valor)`
  - `sacar(conta, valor) -> bool`
  - `transferir(origem, destino, valor) -> bool`
  - `saldo(conta) -> float`

Cada réplica mantém sua **instância própria** de `Banco`.  
O objetivo das arquiteturas é garantir que, no final, essas instâncias estejam **coerentes** entre si.

### 3.2. Mensagens – `Operacao` (`src/common/messages.py`)

Classe usada para trafegar operações:

```python
Operacao {
    id_msg: str,                        # UUID
    tipo: "DEPOSITO" | "SAQUE" | "TRANSFERENCIA",
    conta_origem: str | None,
    conta_destino: str | None,
    valor: float | None
}
