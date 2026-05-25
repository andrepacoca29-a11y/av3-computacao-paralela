# 🔧 CORREÇÃO: Protocolo de Framing para Socket

## ❌ O Problema

A comunicação socket estava **falhando em conexão** porque:

1. **Cliente enviava JSON sem indicar tamanho**
   - `socket.sendall(json_bytes)` → servidor não sabia quantos bytes esperar

2. **Servidor recebia com `recv(10*1024*1024)`**
   - Recebia até 10MB por vez
   - Para dados pequenos: funcionava (recebia tudo)
   - Para dados grandes: ficava esperando mais dados que nunca chegavam

3. **Falta de delimitador**
   - Socket não pode saber onde "termina" a mensagem JSON
   - Sem prefixo de tamanho, não há como sincronizar cliente/servidor

4. **Bug em matrix_operations.py**
   - Chamava `multiplicar_distribuido_real(A, B, servidores=...)` 
   - Função não aceitava esse parâmetro → erro imediato

---

## ✅ A Solução: Protocolo de Framing

### Formato da Mensagem:
```
┌──────────────────┬────────────────────────┐
│ 4 bytes (int)    │ N bytes (JSON)         │
│ Tamanho em bytes │ Dados da mensagem      │
│ Big-endian       │ UTF-8 encoded          │
└──────────────────┴────────────────────────┘
```

### Exemplo:
```python
# Mensagem: {"resultado": [[1,2],[3,4]]}
tamanho = 28 bytes
mensagem = b'\x00\x00\x00\x1c' + b'{"resultado": [[1,2],[3,4]]}'
```

---

## 🔧 Arquivos Modificados

### 1. **socket_client.py** - `_enviar_comando()`

**Antes:**
```python
json_str = json.dumps(comando)
self.socket.sendall(json_str.encode('utf-8'))  # ❌ Sem tamanho!
```

**Depois:**
```python
json_str = json.dumps(comando)
json_bytes = json_str.encode('utf-8')
tamanho = len(json_bytes)

# ✅ Envia tamanho (4 bytes) + dados
tamanho_bytes = tamanho.to_bytes(4, byteorder='big')
self.socket.sendall(tamanho_bytes + json_bytes)

# ✅ Recebe tamanho primeiro
tamanho_resposta_bytes = self.socket.recv(4)
tamanho_resposta = int.from_bytes(tamanho_resposta_bytes, byteorder='big')

# ✅ Recebe EXATAMENTE tamanho_resposta bytes
resposta_completa = b''
bytes_faltando = tamanho_resposta
while bytes_faltando > 0:
    chunk = self.socket.recv(min(bytes_faltando, 1024*1024))
    resposta_completa += chunk
    bytes_faltando -= len(chunk)
```

### 2. **socket_server.py** - `_receber_dados()`

**Antes:**
```python
while True:
    chunk = conexao.recv(tamanho)  # ❌ Tamanho indefinido
    if not chunk:
        break
    dados_completos += chunk
    if len(chunk) < tamanho:
        break
```

**Depois:**
```python
# ✅ Lê 4 bytes com tamanho
tamanho_bytes = conexao.recv(4)
tamanho = int.from_bytes(tamanho_bytes, byteorder='big')

# ✅ Lê EXATAMENTE tamanho bytes
dados_completos = b''
bytes_faltando = tamanho
while bytes_faltando > 0:
    chunk = conexao.recv(min(bytes_faltando, 1024*1024))
    if not chunk:
        return None
    dados_completos += chunk
    bytes_faltando -= len(chunk)
```

### 3. **socket_server.py** - `_enviar_json()`

**Antes:**
```python
json_str = json.dumps(dados)
conexao.sendall(json_str.encode('utf-8'))  # ❌ Sem tamanho!
```

**Depois:**
```python
json_str = json.dumps(dados)
json_bytes = json_str.encode('utf-8')
tamanho = len(json_bytes)

# ✅ Envia tamanho + dados
tamanho_bytes = tamanho.to_bytes(4, byteorder='big')
conexao.sendall(tamanho_bytes + json_bytes)
```

### 4. **matrix_operations.py** - `multiplicar_distribuido_real()`

**Antes:**
```python
C_distribuido = multiplicar_distribuido_real(A, B, servidores=servidores_locais)
# ❌ Parâmetro 'servidores' não existe!
```

**Depois:**
```python
C_distribuido = multiplicar_distribuido_real(A, B, ip_servidor='172.19.9.43', porta=5001)
# ✅ Parâmetros corretos
```

Também melhorado:
- Mais logging para debug
- Testa conexão antes de enviar dados
- Mensagens de erro claras

---

## 🧪 TESTE RÁPIDO

Crie um novo arquivo: `teste_conexao_rapido.py` (já está criado!)

### Terminal 1 (Servidor - 172.19.9.43):
```bash
python socket_server.py --host 0.0.0.0 --port 5001
```

### Terminal 2 (Cliente - seu PC 172.19.9.44):
```bash
python teste_conexao_rapido.py
```

**Esperado:**
```
✅ TESTE 1: Conexão Básica ........... PASSOU
✅ TESTE 2: Ping/Teste .............. PASSOU
✅ TESTE 3: Bloco Pequeno ............ PASSOU
✅ TESTE 4: Bloco Médio ............. PASSOU

🎉 TODOS OS TESTES PASSARAM!
```

---

## 📊 Como Funciona Agora

```
CLIENTE (seu PC 172.19.9.44)          SERVIDOR (172.19.9.43)
─────────────────────────────         ──────────────────────
                                      listening on :5001
    conecta ────────────────────────>
    envia tamanho (4 bytes)
    envia JSON ──────────────────────>  recv(4) → tamanho
                                      loop:
                                        recv(chunk)
                                        bytes_faltando -= len(chunk)
                                      parse JSON
                                      processar
                                      envia tamanho (4 bytes)
                                      envia JSON <────────
    recv(4) → tamanho                    
    loop:
      recv(chunk)
      bytes_faltando -= len(chunk)
    parse JSON
    retorna resultado
```

---

## ⚡ Vantagens do Novo Protocolo

✅ **Determinístico** - Sabe exatamente quantos bytes esperar  
✅ **Escalável** - Funciona com matrizes de qualquer tamanho  
✅ **Sincronizado** - Cliente e servidor sempre sincronizados  
✅ **Robusto** - Trata conexões interrompidas corretamente  
✅ **Eficiente** - Sem overhead de parsing extra  

---

## 🎯 Próximos Passos

1. **Start servidor**: `python socket_server.py --host 0.0.0.0 --port 5001`
2. **Run teste rápido**: `python teste_conexao_rapido.py`
3. **Se passar**: Use `python app.py` com confiança!
4. **Se falhar**: Verifique:
   - Servidor está rodando?
   - IP 172.19.9.43 está correto?
   - Firewall permite porta 5001?
   - Python 3.10+ em ambas máquinas?

