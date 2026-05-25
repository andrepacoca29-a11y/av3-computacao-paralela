# 🖥️ GUIA: Executar Distribuição em TERMINAIS LOCAIS

Você quer simular computadores diferentes **usando terminais do seu MESMO PC**.

## ✅ O Jeito Correto

### 1. **Terminal 1: Inicie o SERVIDOR**

```bash
# Use localhost (127.0.0.1) como padrão
python socket_server.py --host 127.0.0.1 --port 5001
```

**Esperado:**
```
✅ Servidor Socket iniciado em 127.0.0.1:5001
   Aguardando conexões...
```

### 2. **Terminal 2: Rode os TESTES**

```bash
# Conecta ao servidor em localhost:5001 (padrão)
python teste_conexao_rapido.py
```

**Esperado:**
```
Servidor: 127.0.0.1:5001

TESTE 1: Conexao Basica
OK: Conectado com sucesso!

TESTE 2: Ping (operacao teste)
OK: Ping respondido!

TESTE 3: Multiplicacao de Bloco Pequeno (2x3 x 3x2)
OK: Resultado correto!

TESTE 4: Multiplicacao de Bloco Medio (10x10 x 10x10)
OK: Resultado recebido (10x10)

SUCESSO: TODOS OS TESTES PASSARAM!
```

### 3. **Terminal 3: Rode a APLICAÇÃO WEB**

```bash
python app.py
```

Acesse: http://localhost:5000

Na interface:
- Teste 50×50, 100×100, etc.
- Veja "Distribuído" funcionar em tempo real!

---

## 📍 IPs LOCAIS vs REDE REAL

| Cenário | IP | Porta | Terminal |
|---------|----|----|----------|
| **LOCAL (seu PC)** | `127.0.0.1` | 5001 | Terminal 1, 2, 3 mesmo PC |
| **REDE REAL** | `172.19.9.43` | 5001 | PC diferente (servidor) |
| **REDE REAL** | seu PC | 5001 | seu PC (cliente) |

---

## 🔧 MÚLTIPLOS SERVIDORES (AVANÇADO)

Se quiser simular 2 servidores:

### Terminal 1 (Servidor 1):
```bash
python socket_server.py --host 127.0.0.1 --port 5001
```

### Terminal 2 (Servidor 2):
```bash
python socket_server.py --host 127.0.0.1 --port 5002
```

### Terminal 3 (Teste Servidor 1):
```bash
python teste_conexao_rapido.py --port 5001
```

### Terminal 4 (Teste Servidor 2):
```bash
python teste_conexao_rapido.py --port 5002
```

---

## 🚀 RÁPIDO: Start Rápido (3 Terminais)

### Terminal 1:
```bash
python socket_server.py
# Usa padrões: 127.0.0.1:5001
```

### Terminal 2:
```bash
python teste_conexao_rapido.py
# Testa padrões: 127.0.0.1:5001
```

### Terminal 3:
```bash
python app.py
# Acesse: http://localhost:5000
```

---

## 🆘 TROUBLESHOOTING

### Problema: "Connection refused"
**Solução:**
```bash
# Certifique que servidor está rodando em Terminal 1
# Se usar WSL ou Docker, talvez precise localhost vs container IP
python socket_server.py --host 0.0.0.0 --port 5001
```

### Problema: "Address already in use"
**Solução:**
```bash
# Mude a porta
python socket_server.py --port 5002  # Porta diferente
python teste_conexao_rapido.py --port 5002
```

### Problema: Sem conexão entre terminais
**Verifi que:**
1. Servidor está REALMENTE rodando (procure "Servidor Socket iniciado")
2. Você está usando MESMO IP em cliente e servidor (127.0.0.1 para local)
3. Firewall permite porta 5001 (ou a que escolheu)
4. Não há espaços/typos nos comandos

---

## 📋 CHECKLIST FINAL

- [ ] Terminal 1: `python socket_server.py` rodando
- [ ] Terminal 2: `python teste_conexao_rapido.py` mostra TODOS PASSARAM
- [ ] Terminal 3: `python app.py` disponível em http://localhost:5000
- [ ] Teste 100×100 na interface web
- [ ] Vê "Distribuído" sendo executado (sem erros)
- [ ] Números são IDÊNTICOS entre Serial, Paralelo e Distribuído

✅ Se tudo verde = distribuição FUNCIONANDO!

---

## 💡 PRÓXIMAS IDEIAS

1. **Testar com matrizes maiores**: 500×500, 1000×1000
2. **Adicionar mais servidores**: 2-3 servidores em portas diferentes
3. **Analisar overhead**: Compare tempos Serial vs Distribuído
4. **Ir para REDE REAL**: Use IPs reais em vez de localhost
