# 🛰️ Comunicação Baseada em Localização

> Projeto desenvolvido para a disciplina de **Programação Paralela e Distribuída (PPD)** – NP2.

Este sistema permite a **comunicação entre usuários com base em localização geográfica**, utilizando **RPC (XML-RPC)** para mensagens síncronas e **ActiveMQ (STOMP)** para mensagens assíncronas. A entrega de mensagens depende da proximidade geográfica (raio de alcance) e do status (online/offline) do destinatário.

---

## 🧩 Tecnologias Utilizadas

- Python 3.x
- [ActiveMQ](https://activemq.apache.org/) (broker de mensagens)
- `stomp.py` (cliente STOMP)
- `xmlrpc.server` e `xmlrpc.client` (RPC)
- `tkinter` (GUI)
- Comunicação por sockets e filas

---

## ⚙️ Como Funciona

### 📌 Comunicação baseada em raio de alcance
- Usuários **"online" e dentro do raio** ➝ Comunicação **via RPC** (direta).
- Usuários **"offline" ou fora do raio** ➝ Comunicação **via fila ActiveMQ** (offline).

### 🗺️ Cada usuário possui:
- Nome
- Localização (latitude, longitude)
- Status: `online` ou `offline`
- Raio de comunicação (em quilômetros)
- Porta RPC para comunicação síncrona

---

## 📁 Estrutura do Projeto
├── user.py # Modelo de usuário
├── user_registry.py # Registro e gerenciamento dos usuários
├── registry_server.py # Servidor XML-RPC central
├── registry_client.py # Cliente para o servidor de registro
├── rpc_server.py # Servidor RPC local do usuário
├── rpc_client.py # Cliente RPC para envio de mensagens diretas
├── mom_manager.py # Gerenciador de mensagens via ActiveMQ (fila)
├── user_app_gui.py # Interface gráfica do usuário (Tkinter)
├── utils.py # Funções auxiliares (ex: haversine)
└── README.md

## 🧪 Exemplo de Fluxo
1. Usuário A se registra como online, define uma localização e raio.
2. Usuário B se registra próximo a A e também como online.
3. Usuário A envia uma mensagem para B → entregue via RPC.
4. Usuário B vai offline → A tenta enviar mensagem → entregue via fila STOMP.
5. Quando B voltar online, verá a mensagem offline.

## 📌 Requisitos
* Python 3.7+
* ActiveMQ rodando localmente
* Conexão STOMP via stomp.py
* Comunicação XML-RPC exposta na porta 9000



## 📚 Créditos
Desenvolvido por Davison Lucas Mendes Viana para a disciplina de Programação Paralela e Distribuída (PPD).