# 🔍 CHECKLIST DE REQUISITOS - TRABALHO AV2

## Requisitos do Trabalho
```
Atividade Prática: Construir um software que simule a computação distribuída 
entre duas ou mais máquinas. O software deve aplicar multiplicação de matrizes 
e distribuir entre as máquinas (cliente e outra servidora por exemplo) o 
processo de execução dessa multiplicação. Resultados com diferentes testes e 
valores envolvendo execução paralela e serial devem ser apresentados. 
O software pode ser feito em Python. Além disso ele deve permitir matrizes 
além das quadráticas, deve gerar imagens de gráficos de comparação de todos 
os resultados, também ele tem que mostrar as matrizes geradas completas em 
algum local, e plotar gráficos comparativos.
```

---

## ✅ / ❌ CHECKLIST DETALHADO

### 1. **Simular Computação Distribuída Entre Máquinas**
- ✅ **IMPLEMENTADO**
  - `server.py` - Servidor HTTP que recebe requisições de multiplicação
  - `client.py` - Cliente distribuído que divide trabalho entre múltiplos servidores
  - `socket_server.py` - Servidor com socket TCP para comunicação real
  - `socket_client.py` - Cliente socket para conectar a servidores remotos
  - Suporte a múltiplos nodos/processos

### 2. **Aplicar Multiplicação de Matrizes**
- ✅ **IMPLEMENTADO** (Python puro, sem numpy na parte serial/paralela)
  - `multiplicar_serial(A, B)` - Multiplicação sequencial
  - `multiplicar_paralelo(A, B, num_processos)` - Multiplicação paralela com multiprocessing
  - `multiplicar_distribuido(A, B, num_nodos)` - Multiplicação distribuída simulada

### 3. **Distribuir Processo Entre Máquinas**
- ✅ **IMPLEMENTADO**
  - `ClienteDistribuido` em `client.py` divide linhas de A entre servidores
  - Suporta múltiplos servidores (lista de URLs)
  - Validação automática de servidores online/offline
  - Agregação de resultados

### 4. **Resultados com Diferentes Testes (Serial, Paralelo, Distribuído)**
- ✅ **IMPLEMENTADO**
  - `executar_benchmark()` - Executa os 3 métodos e retorna comparações
  - Calcula: tempos, speedups, eficiência, overhead
  - `benchmark_comparativo.py` - Testa múltiplos tamanhos
  - `benchmark_visual.py` - Testes com visualização

### 5. **Suporte a Matrizes Além de Quadráticas**
- ✅ **IMPLEMENTADO**
  - Suporta A (M×N) × B (N×P) → C (M×P)
  - `criar_matriz(linhas, colunas, tipo)` - Gera qualquer tamanho
  - Exemplos em `app.py`: 100×50×200, 200×150×100, etc.
  - Interface web com campos: M (linhas), N (colunas), P (colunas)

### 6. **Gerar Imagens de Gráficos Comparativos**
- ✅ **IMPLEMENTADO**
  - `GeradorGraficos` em `graphics.py` gera 5 gráficos PNG:
    1. `grafico_tempos.png` - Comparação de tempos
    2. `grafico_speedup.png` - Speedup (ganho de desempenho)
    3. `grafico_eficiencia.png` - Eficiência de recursos
    4. `grafico_overhead.png` - Overhead de comunicação
    5. `grafico_escalabilidade.png` - Tempo vs Tamanho
  - Salva em `resultados/` com matplotlib
  - Acesso via web: `/graficos`

### 7. **Mostrar Matrizes Geradas Completas**
- ✅ **PARCIALMENTE IMPLEMENTADO**
  - Interface web mostra amostra (primeiras 6×6 células)
  - Relatório JSON salva todos os resultados
  - ❌ **FALTA:** Arquivo com matrizes COMPLETAS em formato legível (CSV ou TXT)
  - Deveria salvar A, B, C completas para referência

### 8. **Plotar Gráficos Comparativos**
- ✅ **IMPLEMENTADO**
  - 5 gráficos em PNG (item 6)
  - Visualizador web em `/graficos` para exibir as imagens
  - Gráficos embarcados em HTML no relatório
  - Gráficos ASCII em `benchmark_visual.py`

### 9. **Página Web Para Visualização**
- ✅ **IMPLEMENTADO**
  - Interface moderna em `app.py` 
  - Endpoints HTTP:
    - `/` - Interface principal
    - `/benchmark` - Executar benchmark
    - `/graficos` - Visualizar gráficos PNG
    - `/download/json` - Baixar resultados
    - `/download/html` - Baixar relatório
    - `/resultados/*` - Servir arquivos estáticos

### 10. **Relatório HTML**
- ✅ **IMPLEMENTADO**
  - `gerar_relatorio_html()` em `graphics.py`
  - Embarca gráficos como base64
  - Resumo de todos os testes
  - Tabelas com resultados

---

## ⚠️ O QUE FALTA OU PRECISA MELHORAR

### 1. **Matrizes Completas Não São Salvas em Arquivo**
**Status:** ❌ FALTA

O sistema salva:
- Apenas amostra (6×6) na web
- Dados de benchmark em JSON

Deveria adicionar:
- Arquivo CSV/TXT com matrizes A, B, C completas
- Opção de download das matrizes

**Impacto:** Requisito não totalmente atendido

### 2. **Arquivo `graficos.html` Referenciado Mas Não Existe**
**Status:** ❌ FALTA

`app.py` linha 363 tenta abrir `graficos.html` que não existe:
```python
def enviar_pagina_graficos(self):
    try:
        with open('graficos.html', 'r', encoding='utf-8') as f:  # ← ARQUIVO NÃO EXISTE!
```

Deveria gerar dinamicamente ou criar o arquivo.

**Impacto:** Endpoint `/graficos` não funciona corretamente

### 3. **Distribuição Real (Socket) Não Está Integrada**
**Status:** ⚠️ PARCIALMENTE

Existem:
- `socket_server.py` - Implementado
- `socket_client.py` - Implementado
- `server.py` - Implementado
- `client.py` - Implementado

Mas:
- Não há um script de teste integrado
- Socket não é usado pela interface web
- Falta documentação de como usar

**Impacto:** Funcionalidade existe mas não está integrada na aplicação principal

### 4. **Teste com Múltiplos Servidores Não Está Documentado**
**Status:** ⚠️ FALTA DOCUMENTAÇÃO

Como testar com 2 ou mais máquinas:
- Precisaria iniciar `server.py` em portas diferentes
- Usar `client.py` para conectar

Não há instrução de uso completo.

**Impacto:** Requisito existe mas falta modo prático de testar

---

## 📋 RESUMO FINAL

| Requisito | Status | Completo | Notas |
|-----------|--------|----------|-------|
| Computação distribuída | ✅ | 100% | Serial, Paralelo, Distribuído |
| Multiplicação de matrizes | ✅ | 100% | Python puro, suporta M×N×P |
| Distribuição entre máquinas | ✅ | 90% | Implementado mas não integrado |
| Testes comparativos | ✅ | 100% | 5 benchmarks diferentes |
| Matrizes retangulares | ✅ | 100% | Suporta qualquer dimensão |
| Gráficos em PNG | ✅ | 100% | 5 gráficos gerados |
| Matrizes completas exibidas | ⚠️ | 50% | Só amostra na web, faltam arquivos |
| Gráficos comparativos | ✅ | 100% | 5 gráficos + interface web |
| Interface web | ✅ | 95% | Funciona mas `/graficos` com bug |
| Relatório HTML | ✅ | 100% | Completo e funcional |

---

## 🔴 PRIORITÁRIO - O QUE FALTA PARA COMPLETAR

### 1. **Criar arquivo `graficos.html`** (CRÍTICO)
- Arquivo que lista e exibe os 5 gráficos PNG gerados
- Sem isso o endpoint `/graficos` não funciona

### 2. **Salvar Matrizes Completas em Arquivo** (IMPORTANTE)
- Função para salvar A, B, C em CSV ou TXT
- Integrar com interface web para download

### 3. **Integrar Socket com Interface Web** (DESEJÁVEL)
- Modo "remote" na interface para usar socket em vez de multiprocessing
- Ou documentar como usar socket_server + socket_client

### 4. **Documentação de Teste Real Distribuído** (IMPORTANTE)
- README com instruções de como testar com 2+ máquinas
- Scripts de exemplo

---

## 💡 CONCLUSÃO

**Trabalho está ~90% completo.**

- ✅ Todos os requisitos principais implementados
- ❌ Faltam detalhes de integração (gráficos, matrizes completas)
- ⚠️ Socket distribuído existe mas não é usado pela web
- 📊 Análise e benchmarks estão excelentes

**Tempo estimado para completar: 30-45 minutos**
