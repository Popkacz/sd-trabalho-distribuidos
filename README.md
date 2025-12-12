# Trabalho de Sistemas Distribuídos – Banco Replicado na AWS

Este repositório implementa um sistema de **banco de dados replicado** em um ambiente **distribuído na AWS**, evoluindo em quatro partes:

1. **Parte 1 – Multicast com ZeroMQ**  
2. **Parte 2 – RPC + Fila de Mensagens**  
3. **Parte 3 – Ordenação Total com Sequenciador Central**  
4. **Parte 4 – Coordenação Primário–Backup (menos coordenação)**  

Todas as partes usam a **mesma base de aplicação**: operações bancárias simples sobre contas (`depósito`, `saque`, `transferência`) mantidas em réplicas que compartilham o mesmo estado.

---

## 1. Ambiente Utilizado

O sistema foi implantado em **3 instâncias EC2** na AWS:

- **Client / Orquestrador**  
  - Roda os clientes das partes (1, 2, 3 e 4).  
  - Roda serviços centrais das Partes 2 e 3 (RPC e Sequenciador).  

- **Replica 01**  
  - Atua como **réplica** (Partes 1, 2 e 3).  
  - Atua como **Primário** (Parte 4).  

- **Replica 02**  
  - Atua como **réplica** (Partes 1, 2 e 3).  
  - Atua como **Backup** (Parte 4).  

### 1.1. Tecnologias

- Linguagem: **Python 3**
- Bibliotecas:
  - **ZeroMQ (`pyzmq`)** → multicast, filas, REQ/REP, PUB/SUB  
  - **RPyC** → RPC na Parte 2  
- Infra:
  - **AWS EC2**
  - **Security Group** com portas abertas para comunicação entre as instâncias

---

## 2. Modelo da Aplicação (Banco)

A aplicação é um **banco de contas bancárias replicadas**.

- Cada réplica mantém um objeto `Banco` (ver `src/common/state.py`):  
  - `depositar(conta, valor)`  
  - `sacar(conta, valor)`  
  - `transferir(origem, destino, valor)`  
- As operações são representadas pela classe `Operacao` (ver `src/common/messages.py`):  
  ```python
  Operacao {
      id_msg: str,
      tipo: "DEPOSITO" | "SAQUE" | "TRANSFERENCIA",
      conta_origem: str | None,
      conta_destino: str | None,
      valor: float | None
  }


