# 📡 Guia Passo a Passo — Execução Distribuída em Dois Computadores

## 🎯 Objetivo
Executar a multiplicação de matrizes **distribuída** usando dois computadores na mesma rede local, onde:
- **Computador 1** (Servidor): Roda `socket_server.py` — aguarda requisições
- **Computador 2** (Cliente): Roda `app.py` — envia blocos de matrizes para processamento distribuído

---

## ⚙️ Pré-requisitos

### Ambos os Computadores:
- ✅ Python 3.10+ instalado
- ✅ Dependências instaladas: `pip install -r requirements.txt`
- ✅ Ambos conectados à **mesma rede local** (WiFi ou Ethernet)
- ✅ Sem firewall bloqueando a porta TCP 5001

### Verificar Conectividade:
```bash
ping <IP_DO_OUTRO_COMPUTADOR>
```

---

## 🔍 PASSO 1: Descobrir os IPs dos Computadores

### No Windows (ambos os computadores):
```bash
ipconfig
```

**Procure por:**
- `IPv4 Address` na seção da rede ativa
- Exemplo: `192.168.1.100` ou `10.0.0.50`

Anote:
- 🖥️ **Servidor (Computador 1)**: IP do servidor (ex: `192.168.1.50`)
- 💻 **Cliente (Computador 2)**: IP do cliente (ex: `192.168.1.100`)

---

## 🚀 PASSO 2: Iniciar o Servidor Distribuído (Computador 1)

### Terminal no Computador 1:

```bash
cd C:\Users\[seu_usuario]\Downloads\Trabalho_AV2_Comp_paralela_concorrnte

# Ativar ambiente virtual
env\Scripts\Activate.ps1

# Iniciar servidor na porta 5001, escutando em todos os IPs
python socket_server.py --host 0.0.0.0 --port 5001
```

**Saída esperada:**
```
✅ Servidor Socket iniciado em 0.0.0.0:5001
   Aguardando conexões...
```

⚠️ **DEIXE ESTE TERMINAL ABERTO** — o servidor precisa ficar rodando continuamente.

---

## 💻 PASSO 3: Iniciar a Aplicação Principal (Computador 2)

### Terminal no Computador 2:

```bash
cd C:\Users\[seu_usuario]\Downloads\Trabalho_AV2_Comp_paralela_concorrnte

# Ativar ambiente virtual
env\Scripts\Activate.ps1

# Iniciar app.py (abrirá interface web em http://localhost:5000)
python app.py
```

**Saída esperada:**
```
✓ Servidor HTTP iniciado em http://localhost:5000
```

---

## 🌐 PASSO 4: Acessar a Interface Web (Computador 2)

### No navegador do Computador 2:

```
http://localhost:5000
```

Você verá a interface com:
- Campo para **Linhas A (M)**
- Campo para **Colunas A (N)**
- Campo para **Colunas B (P)**
- Campo para **Processos / Nodos**
- Botão **▶ Executar**

---

## 🎬 PASSO 5: Executar Benchmark Distribuído

### Na interface web:

1. **Preencha os valores:**
   - **Linhas A (M)**: `100` (ou o tamanho desejado)
   - **Colunas A (N)**: `100`
   - **Colunas B (P)**: `100`
   - **Tipo de Matriz**: `Aleatória (1-10)`
   - **Processos / Nodos**: `2` (ou número de nodos remotos)

2. **Clique em ▶ Executar**

### O que acontece nos bastidores:

```
┌─────────────────────────────────────────────────────────────┐
│ CLIENTE (app.py - Computador 2)                             │
├─────────────────────────────────────────────────────────────┤
│ 1. Cria matrizes A e B localmente                            │
│ 2. Divide matriz A em BLOCOS por número de nodos            │
│ 3. Para cada bloco: conecta via socket ao servidor          │
│ 4. Envia: {"operacao": "multiplicar_bloco", "bloco_a": ..}  │
│ 5. Aguarda resposta: {"resultado": [linha 0 de C]}          │
│ 6. Monta C completa a partir das respostas                  │
└─────────────────────────────────────────────────────────────┘
                          ↕ SOCKET TCP:5001
┌─────────────────────────────────────────────────────────────┐
│ SERVIDOR (socket_server.py - Computador 1)                  │
├─────────────────────────────────────────────────────────────┤
│ 1. Recebe conexão do cliente                                │
│ 2. Recebe JSON com bloco_a e matriz_b                       │
│ 3. Calcula: linha_resultado = bloco_a @ matriz_b            │
│ 4. Retorna JSON com resultado                               │
│ 5. Fecha conexão                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 PASSO 6: Visualizar Resultados

### Após o benchmark terminar:

A interface exibirá:

1. **Métricas de Tempo:**
   - Serial: tempo em segundos
   - Paralelo: tempo em segundos
   - **Distribuído: tempo da operação com socket**

2. **Speedup & Eficiência:**
   - Speedup Paralelo = Tempo Serial / Tempo Paralelo
   - **Speedup Distribuído = Tempo Serial / Tempo Distribuído**
   - Eficiência = Speedup / Número de Nodos

3. **Gráficos Comparativos:**
   - Clique em **📈 Ver Gráficos (5)** para visualizar:
     - Tempos de execução
     - Speedup
     - Eficiência
     - Overhead
     - Escalabilidade

4. **Downloads:**
   - **📥 JSON**: Dados estruturados do benchmark
   - **📊 Relatório HTML**: Gráficos interativos
   - **📈 Ver Gráficos (5)**: Visualizador PNG

---

## 🔧 Troubleshooting

### ❌ "Connection refused" ao executar
**Solução:**
- Verifique se o servidor está rodando no Computador 1
- Confirme o IP correto do servidor
- Verifique firewall: `netstat -an | findstr :5001` (Windows)

### ❌ "Timeout ao conectar"
**Solução:**
- Teste ping entre os computadores: `ping 192.168.1.50`
- Verifique se ambos estão na mesma rede
- Confirme que a porta 5001 não está bloqueada

### ❌ "ModuleNotFoundError: No module named 'numpy'"
**Solução:**
```bash
pip install -r requirements.txt
```

### ❌ "Address already in use" na porta 5001
**Solução:**
```bash
# Liberar porta (Windows)
netstat -ano | findstr :5001
taskkill /PID <PID> /F
```

---

## 📋 Checklist de Verificação

- [ ] Python 3.10+ instalado em ambos os computadores
- [ ] `pip install -r requirements.txt` executado em ambos
- [ ] Ambos os computadores conectados à mesma rede local
- [ ] IPs dos computadores anotados
- [ ] Servidor iniciado no Computador 1: `python socket_server.py --host 0.0.0.0 --port 5001`
- [ ] Cliente (app.py) iniciado no Computador 2
- [ ] Navegador aberto em `http://localhost:5000`
- [ ] Valores de matriz preenchidos (M, N, P)
- [ ] Botão **▶ Executar** clicado
- [ ] Resultados exibidos na interface
- [ ] Gráficos visualizados corretamente

---

## 📝 Exemplo Completo de Execução

### Terminal 1 — Computador 1 (Servidor):
```powershell
PS C:\Users\andre\Downloads\Trabalho_AV2_Comp_paralela_concorrnte> env\Scripts\Activate.ps1
PS C:\Users\andre\Downloads\Trabalho_AV2_Comp_paralela_concorrnte> python socket_server.py --host 0.0.0.0 --port 5001

✅ Servidor Socket iniciado em 0.0.0.0:5001
   Aguardando conexões...

📡 Cliente conectado de 192.168.1.100:54321
   Processando multiplicação de bloco...
   ✓ Conexão encerrada
```

### Terminal 2 — Computador 2 (Cliente):
```powershell
PS C:\Users\andre\Downloads\Trabalho_AV2_Comp_paralela_concorrnte> env\Scripts\Activate.ps1
PS C:\Users\andre\Downloads\Trabalho_AV2_Comp_paralela_concorrnte> python app.py

✓ Servidor HTTP iniciado em http://localhost:5000
Acesso: http://localhost:5000
```

### Browser — Computador 2:
```
Abra: http://localhost:5000

Preencha:
  M: 100
  N: 100
  P: 100
  Tipo: Aleatória
  Nodos: 2

Clique: ▶ Executar

[Aguarde processamento...]

✓ Serial: 0.523 s
✓ Paralelo: 0.156 s (3.35× mais rápido)
✓ Distribuído: 0.312 s (1.67× mais rápido)
```

---

## 🎓 Conceitos-Chave

### Distribuição em Socket
- **Socket TCP**: Conexão de baixo nível entre computadores
- **JSON**: Protocolo de serialização para dados
- **Blocos de Matriz**: Divisão de A em partes menores
- **Overhead**: Tempo de comunicação de rede

### Métricas
- **Speedup**: Mede ganho de velocidade (Serial / Paralelo)
- **Eficiência**: Utilização dos recursos (Speedup / Nodos)
- **Escalabilidade**: Como a performance escala com nodos

---

## 💡 Dicas

1. **Para teste rápido**: Use matrizes pequenas (100×100)
2. **Para teste realista**: Use matrizes grandes (500×500+)
3. **Para múltiplos servidores**: Inicie vários `socket_server.py` em portas diferentes (5001, 5002, etc)
4. **Para debug**: Verifique logs do servidor no terminal

---

**✅ Pronto! Sua computação distribuída está funcionando!**
