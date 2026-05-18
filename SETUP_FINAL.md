# ✅ GUIA FINAL — SUA CONFIGURAÇÃO COM OS IPS

## 🎯 Seus Computadores:

| Computador | IP | Papel | Porta |
|------------|----|----|-------|
| **Seu PC (Cliente)** | `172.19.9.44` | Roda `app.py` | 5000 |
| **Outro PC (Servidor)** | `172.19.9.43` | Roda `socket_server.py` | 5001 |

---

## 🚀 PASSO 1: Iniciar o SERVIDOR (Computador com IP 172.19.9.43)

Abra PowerShell **no outro computador** (172.19.9.43) e execute:

```bash
cd C:\Users\[usuario]\Downloads\Trabalho_AV2_Comp_paralela_concorrnte
env\Scripts\Activate.ps1
python socket_server.py --host 0.0.0.0 --port 5001
```

**Você verá:**
```
✅ Servidor Socket iniciado em 0.0.0.0:5001
   Aguardando conexões...
```

⚠️ **DEIXE ESTE TERMINAL ABERTO** — precisa ficar rodando

---

## 💻 PASSO 2: Iniciar o CLIENTE (Seu PC com IP 172.19.9.44)

Abra PowerShell **no seu PC** (172.19.9.44) e execute:

```bash
cd C:\Users\[usuario]\Downloads\Trabalho_AV2_Comp_paralela_concorrnte
env\Scripts\Activate.ps1
python app.py
```

**Você verá:**
```
✓ Servidor HTTP iniciado em http://localhost:5000
```

---

## 🌐 PASSO 3: Acessar a Interface

No **seu PC** (172.19.9.44), abra o navegador e acesse:

```
http://localhost:5000
```

Você verá a interface web com:
- Campo para **Linhas A (M)**
- Campo para **Colunas A (N)**  
- Campo para **Colunas B (P)**
- Campo para **Processos / Nodos**
- Botão **▶ Executar**

---

## 🎬 PASSO 4: Executar o Benchmark

Na interface web, preencha:
- **Linhas A (M)**: `100`
- **Colunas A (N)**: `100`
- **Colunas B (P)**: `100`
- **Tipo de Matriz**: `Aleatória (1-10)`
- **Processos / Nodos**: `2`

Clique em **▶ Executar**

---

## ✅ PASSO 5: Validar se está funcionando

Você verá 3 tempos de execução:
- ⏱️ **Serial**: Cálculo no seu PC
- ⏱️ **Paralelo**: Cálculo paralelo no seu PC  
- ⏱️ **Distribuído**: Cálculo enviado para 172.19.9.43 via socket

**Se o tempo "Distribuído" aparecer**, significa que **FUNCIONOU!** ✅

---

## 🧪 TESTE RÁPIDO DE CONECTIVIDADE

Se quiser validar antes, use o script de teste:

```bash
# No seu PC (172.19.9.44)
python teste_distribuido.py
```

Quando pedir o IP, digite: `172.19.9.43`

**Saída esperada:**
```
✅ Conexão bem-sucedida!
✅ Resposta recebida!
✅ Teste 2 PASSOU - Comunicação funcionando!
```

---

## 📍 ARQUIVOS ALTERADOS:

✅ **socket_client.py**
- IP padrão agora é `172.19.9.43` (seu servidor)
- Documentação atualizada

✅ **matrix_operations.py**
- Nova função: `multiplicar_distribuido_real(A, B, ip_servidor='172.19.9.43')`
- Integrada com socket real

---

## 🔍 VERIFICAÇÃO PASSO A PASSO:

### 1️⃣ Verificar se servidor está rodando:

No outro PC, verifique a saída:
```
✅ Servidor Socket iniciado em 0.0.0.0:5001
```

### 2️⃣ Verificar se cliente conecta:

Abra PowerShell e teste o ping:
```bash
ping 172.19.9.43
```

Deve responder com `Reply from 172.19.9.43`

### 3️⃣ Verificar conectividade via Python:

No seu PC, execute:
```bash
python teste_distribuido.py
# Digite: 172.19.9.43
```

### 4️⃣ Executar no app.py:

Abra `http://localhost:5000` e execute o benchmark

---

## 📊 O QUE VOCÊ VERÁ:

Se tudo funcionar:

```
Resultados de Benchmark
─────────────────────────
Serial:      0.523 s
Paralelo:    0.156 s  (3.35× mais rápido)
Distribuído: 0.312 s  (1.67× mais rápido) ← Enviado para 172.19.9.43!

Speedup Paralelo: 3.35×
Speedup Distribuído: 1.67×
Eficiência: 83.5%
```

---

## ❌ TROUBLESHOOTING:

| Problema | Solução |
|----------|---------|
| ❌ "Connection refused" | Servidor não está rodando em 172.19.9.43 |
| ❌ "Timeout" | Firewall bloqueando porta 5001 ou rede desconectada |
| ❌ "Módulo não encontrado" | Execute `pip install -r requirements.txt` em ambos PCs |
| ✅ Tudo funciona! | Veja métricas comparativas na interface |

---

## 🎓 RESUMO:

```
SEU PC (172.19.9.44)
    ↓
  app.py (http://localhost:5000)
    ↓
Preencheu valores e clicou "Executar"
    ↓
Socket TCP:5001
    ↓
OUTRO PC (172.19.9.43)
    ↓
socket_server.py
    ↓
Calcula multiplicação
    ↓
Retorna resultado via socket
    ↓
app.py exibe resultado + gráficos
```

---

## ✨ Está tudo pronto!

1. ✅ IPs configurados: 172.19.9.44 (cliente) e 172.19.9.43 (servidor)
2. ✅ socket_client.py atualizado com IP do servidor
3. ✅ Função de distribuição real criada
4. ✅ Script de teste disponível

**Próximos passos:**
1. Inicie servidor: `python socket_server.py` (172.19.9.43)
2. Inicie cliente: `python app.py` (172.19.9.44)
3. Acesse: `http://localhost:5000`
4. Clique em **▶ Executar** para começar!
