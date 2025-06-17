# 📁 udpFileServer  
**A simple file server using the UDP protocol with optional GUI interface.**

---

## 🚀 How to Run

### 🖥️ Server

Execute o servidor com o seguinte comando:

```bash
python Server/server.py
```

---

### 🧑‍💻 Client

#### ✅ With GUI (PyQt)
1. Ative o ambiente virtual:
    ```bash
    activate venv
    ```
2. Execute o cliente com interface gráfica:
    ```bash
    python PyQt/client.py
    ```

#### ⚙️ Without GUI (Terminal)
Execute diretamente pelo terminal:

```bash
python Client/client.py
```

---

## 📦 Estrutura do Projeto

```
udpFileServer/
 ── Server/
    └── client.py
    └── Arquivos/
 ── Client/
    └── client.py
    └── Downloads/
    └── Uploads/
 ── PyQt/
    └── client.py
 ── Ui/
    └── client.ui
    └── ui_client.py
 
```

---

## 🧪 Funcionalidades

- Envio e recebimento de arquivos via protocolo UDP
- Suporte a interface gráfica com PyQt
- Simulação de perda de pacotes (opcional)
- Controle de confiabilidade (Go-Back-N)
