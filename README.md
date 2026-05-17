# Multiplicação de Matrizes Distribuída — AV2 2026

## Requisitos Atendidos ✓

- ✅ **Computação Distribuída**: Serial, Paralela (Multiprocessing) e Distribuída (Simulado)
- ✅ **Matrizes Não-Quadráticas**: Suporta A(M×N) × B(N×P) = C(M×P)
- ✅ **Comparação de Desempenho**: Speedup, Eficiência e Overhead
- ✅ **Gráficos Comparativos**: Tempos, Speedup, Eficiência, Overhead e Escalabilidade
- ✅ **Armazenamento de Resultados**: JSON e Relatório HTML
- ✅ **Visualização de Matrizes**: Amostra completa na interface web

## Estrutura do Projeto

```
app.py                      # Interface web e servidor principal
matrix_operations.py        # Operações de multiplicação de matrizes
graphics.py                 # Geração de gráficos e exportação CSV
graficos.html               # Visualizador profissional de gráficos PNG
socket_server.py            # Servidor distribuído (rede)
socket_client.py            # Cliente distribuído (rede)
server.py                   # Servidor HTTP distribuído (opcional)
client.py                   # Cliente HTTP distribuído (opcional)
benchmark_visual.py         # Benchmark standalone com ASCII graphs
requirements.txt            # Dependências Python
resultados/                 # Pasta para gráficos, CSVs e relatórios
  ├── resultados.json       # Histórico de benchmarks
  ├── relatorio.html        # Relatório HTML com gráficos embarcados
  ├── indice.csv            # Índice de matrizes exportadas
  ├── A_*.csv, B_*.csv, C_*.csv  # Matrizes completas (timestamped)
  ├── grafico_tempos.png
  ├── grafico_speedup.png
  ├── grafico_eficiencia.png
  ├── grafico_overhead.png
  └── grafico_escalabilidade.png
```

## Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

**Dependências:**
- numpy==1.24.4 — Operações matriciais otimizadas
- matplotlib==3.8.4 — Geração de gráficos

### 2. Executar a Aplicação Principal

```bash
python app.py
```

A interface web abrirá automaticamente em `http://localhost:5000`

## Como Usar

### Interface Web Principal (localhost:5000)

1. Acesse http://localhost:5000
2. Configure as dimensões das matrizes:
   - **M**: Linhas de A
   - **N**: Colunas de A = Linhas de B
   - **P**: Colunas de B
   - **Tipo**: Aleatório, Zeros, Uns, Identidade, Diagonal, Triangular
   - **Número de Processos**: Quantidade de processos paralelos (sugestão: número de núcleos)
3. Clique em **"Executar Benchmark"** para rodar comparação
4. Veja resultados em 3 abas:
   - **Resultados**: Tempos de execução, speedup, eficiência, overhead
   - **Gráficos**: Visualização dos 5 gráficos PNG gerados
   - **Matrizes**: Links para download das matrizes completas em CSV

### Visualizador de Gráficos (localhost:5000/graficos)

Acesse `/graficos` para interface profissional com:
- Display em grid responsivo dos 5 gráficos PNG
- Auto-carregamento a cada 10 segundos
- Indicadores de status (✓ carregado, ⏳ carregando, ❌ erro)
- Navegação voltando à interface principal

### Exportação de Matrizes em CSV

Após cada benchmark, as matrizes **completas** são automaticamente salvas em `resultados/`:

**Arquivos Gerados:**
- `A_{timestamp}.csv` - Matriz A original (M × N)
- `B_{timestamp}.csv` - Matriz B original (N × P)
- `C_{timestamp}.csv` - Resultado C (M × P)
- `indice.csv` - Índice mapeando os arquivos e operação

**Formato CSV:**
- Uma linha por linha da matriz
- Valores separados por vírgula
- 4 casas decimais
- Pronto para importar em Excel ou Python (pandas)

**Exemplo de uso em Python:**
```python
import pandas as pd

A = pd.read_csv('resultados/A_20260516_143022.csv', header=None)
B = pd.read_csv('resultados/B_20260516_143022.csv', header=None)
C = pd.read_csv('resultados/C_20260516_143022.csv', header=None)
```

### Componentes do Sistema

#### `app.py` — Servidor Web Principal
Interface web com endpoints:
- `GET /` — Interface principal
- `GET /benchmark?m=X&n=Y&p=Z&tipo=T&proc=P` — Executa benchmark
- `GET /graficos` — Página de visualização de gráficos
- `GET /resultados/*` — Serve gráficos PNG e arquivos CSV
- `GET /download/json|html` — Download de relatório

#### `matrix_operations.py` — Multiplicação de Matrizes
Implementa 3 métodos:

```python
# Serial (puro Python, sem numpy)
resultado = multiplicar_serial(A, B)

# Paralelo (multiprocessing com divisão de linhas)
resultado = multiplicar_paralelo(A, B, num_processos=4)

# Distribuído (sockets)
resultado = multiplicar_distribuido(A, B, num_nodos=3)

# Benchmark completo (compara todos)
dados = executar_benchmark(m=100, n=100, p=100, num_processos=4)
```

#### `graphics.py` — Gráficos e Exportação
Gera gráficos PNG e exporta matrizes:

```python
# Gerar todos os 5 gráficos
gerador = GeradorGraficos(diretorio_saida="resultados")
graficos = gerador.gerar_todos(lista_de_resultados)

# Exportar matrizes para CSV (NOVO)
caminhos = salvar_matrizes_csv(A, B, C, diretorio="resultados")
# Retorna: {'A': 'A_timestamp.csv', 'B': 'B_timestamp.csv', 'C': 'C_timestamp.csv'}

# Gerar relatório HTML com gráficos embarcados
gerar_relatorio_html(resultados, graficos, "relatorio.html")
```

#### `graficos.html` — Visualizador de Gráficos (NOVO)
Interface web profissional para visualizar gráficos PNG gerados:
- Display responsivo em grid 2×3 (5 gráficos + instruções)
- Auto-refresh a cada 10 segundos
- Indicadores de carregamento
- Compatível com Firefox, Chrome, Safari, Edge
- Acesso em: `http://localhost:5000/graficos`

## Métricas Coletadas

### Tempos
- **Serial**: Tempo de execução com numpy puro
- **Paralelo**: Tempo com multiprocessing
- **Distribuído**: Tempo simulado distribuído

### Performance
- **Speedup**: T_serial / T_paralelo (ganho de desempenho)
- **Eficiência**: Speedup / número_de_processos (uso de recursos)
- **Overhead**: Tempo_paralelo - Tempo_serial (custo de comunicação)

### Validação
- Verifica se resultados paralelo/distribuído são iguais ao serial
- Detecta possíveis problemas de sincronização

## Exemplos de Teste

### Matrizes Quadráticas
- 100×100 × 100×100 = 100×100
- 200×200 × 200×200 = 200×200

### Matrizes Retangulares
- 100×50 × 50×200 = 100×200
- 300×150 × 150×100 = 300×100

## Teste Distribuído em Rede

Para testar multiplicação em múltiplas máquinas:

### Servidor Distribuído

```bash
# Máquina Servidor (ex: 192.168.1.100)
python socket_server.py
# Escuta em porta 9999 (padrão)
# Aguarda conexões de clientes
```

### Cliente Distribuído

```bash
# Máquina Cliente
python socket_client.py
# Interface interativa para:
# 1. Definir IP do servidor (ex: 192.168.1.100)
# 2. Definir dimensões das matrizes
# 3. Enviar para servidor calcular
# 4. Receber e validar resultado
```

**Exemplo de fluxo:**
```
Cliente: Conecta a 192.168.1.100:9999
Cliente: Envia A (100×100) e B (100×100)
Servidor: Calcula C = A × B
Servidor: Envia resultado + tempo
Cliente: Compara com serial local
Cliente: Mostra comparação de performance
```

## Gráficos Gerados

1. **grafico_tempos.png**: Comparação de tempos (serial vs paralelo vs distribuído)
2. **grafico_speedup.png**: Ganho de desempenho por tamanho
3. **grafico_eficiência.png**: Uso de recursos (% por processo)
4. **grafico_overhead.png**: Overhead de comunicação IPC
5. **grafico_escalabilidade.png**: Escalabilidade com tamanho da matriz

## Relatório HTML

O arquivo `resultados/relatorio.html` contém:
- Resumo de todos os testes
- Gráficos embarcados
- Métricas detalhadas
- Status de validação

Abra em qualquer navegador para visualizar.

## Notas Técnicas

### Algoritmo Serial
```
C[i][j] = Σ(A[i][k] * B[k][j]) para k=0 até N-1
```
Complexidade: O(M × N × P)

### Divisão Paralela
- Divide as linhas de A entre processos
- Cada processo calcula seu bloco de C
- Pool automatiza sincronização e coleta

### Overhead de IPC
O overhead pode ser:
- **Positivo**: Tempo_paralelo > Tempo_serial (comunicação domina)
- **Negativo**: Tempo_paralelo < Tempo_serial (ganho líquido)

### Metodologia de Foster
1. **Partição**: A dividida por linhas
2. **Comunicação**: Cada processo recebe seu bloco + B inteira
3. **Aglomeração**: Agrupa linhas para reduzir IPC
4. **Mapeamento**: Mapeia blocos para processos do Pool

## Entendendo o Overhead de Paralelização

### Por que Paralelo é Mais Lento para Matrizes Pequenas?

**Tempo Serial (A: 100×100, B: 100×100):**
```
Multiplicação pura: ~0.01 segundos
Total: 0.01s
```

**Tempo Paralelo (4 processos):**
```
Criar 4 processos:        ~0.5s
Dividir dados:            ~0.05s
Enviar aos processos:     ~0.05s
Cálculos em paralelo:     ~0.003s (25% do tempo serial puro)
Coletar resultados:       ~0.05s
Sincronização:            ~0.05s
Total: ~0.71s
```

**Resultado:** Serial (0.01s) é **70× mais rápido** que paralelo (0.71s)!

### Break-Even Point

O ponto de equilíbrio ocorre em aproximadamente **matrizes 200×200**:
- **< 100×100**: Serial vence (overhead > benefício)
- **100×200**: Performance próxima (overhead ≈ benefício)
- **> 200×200**: Paralelo vence (benefício > overhead)

### Escalabilidade com Múltiplos Processos

Aumentar processos nem sempre melhora speedup:
```
Tamanho 500×500:
- 1 processo (serial):  1.2s (baseline)
- 2 processos:  0.7s  (Speedup 1.7×)
- 4 processos:  0.5s  (Speedup 2.4×)
- 8 processos:  0.45s (Speedup 2.7×)
- 16 processos: 0.50s (Speedup 2.4× - PIOR!)
```

Veja: Com 16 processos é **MAIS LENTO** que com 8 processos!  
Razão: Overhead de sincronização supera benefício de paralelização.

## Troubleshooting

### Porta 5000 já em uso
```bash
python app.py --porta 5001
```

### Memória insuficiente
Reduza o tamanho das matrizes no preset

### Gráficos não estão gerando
Certifique-se de:
1. Matplotlib está instalado: `pip install matplotlib`
2. Pasta `resultados/` existe e tem permissão de escrita

## Performance esperada

| Tamanho | Serial (s) | Paralelo 4P (s) | Speedup | Eficiência |
|---------|-----------|-----------------|---------|-----------|
| 100×100 | 0.01      | 0.71            | 0.01×   | 0.3%      |
| 200×200 | 0.08      | 0.15            | 0.53×   | 13.3%     |
| 300×300 | 0.27      | 0.20            | 1.35×   | 33.8%     |
| 500×500 | 1.20      | 0.50            | 2.40×   | 60%       |
| 1000×1000 | 9.60    | 2.80            | 3.43×   | 85.7%     |

*Valores podem variar significativamente com hardware, SO e carga do sistema*

## Documentação Adicional

Para análises mais profundas, consulte:
- **RESUMO_MUDANCAS.md** — Explicação técnica das implementações
- **ANALISE_OVERHEAD.md** — Deep dive no overhead de paralelização
- **CHECKLIST_REQUISITOS.md** — Verificação completa de requisitos

## Autor
AV2 — Computação Paralela e Concorrente — 2026
