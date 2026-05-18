"""
Operações de multiplicação de matrizes — Serial, Paralela e Distribuída
Suporta TODOS os tipos de matrizes: quadráticas, retangulares, etc
Validação completa e tratamento de erros robusto
"""

import time
import random
import multiprocessing
import numpy as np
from typing import Tuple, List, Union, Optional


# ═══════════════════════════════════════════════════════════════════
#  VALIDAÇÃO E CONVERSÃO DE MATRIZES
# ═══════════════════════════════════════════════════════════════════

def validar_matriz(matriz) -> Tuple[bool, str]:
    """
    Valida se uma matriz é válida
    Retorna (é_válida, mensagem_erro)
    """
    if matriz is None:
        return False, "Matriz é None"
    
    if isinstance(matriz, np.ndarray):
        if len(matriz.shape) != 2:
            return False, f"Matriz numpy deve ser 2D, encontrado {len(matriz.shape)}D"
        return True, "OK"
    
    if not isinstance(matriz, (list, tuple)):
        return False, f"Matriz deve ser lista, tuple ou numpy array, encontrado {type(matriz)}"
    
    if len(matriz) == 0:
        return False, "Matriz tem 0 linhas"
    
    # Verifica se é lista de listas
    if not isinstance(matriz[0], (list, tuple, np.ndarray)):
        return False, "Matriz deve ser lista de listas/tuples"
    
    # Verifica se todas as linhas têm o mesmo tamanho
    num_colunas = len(matriz[0])
    if num_colunas == 0:
        return False, "Matriz tem 0 colunas"
    
    for i, linha in enumerate(matriz):
        if len(linha) != num_colunas:
            return False, f"Linha {i} tem {len(linha)} colunas, esperado {num_colunas}"
    
    return True, "OK"


def converter_matriz(matriz, dtype=np.float64) -> np.ndarray:
    """Converte qualquer formato de matriz para numpy array"""
    if isinstance(matriz, np.ndarray):
        return matriz.astype(dtype)
    return np.array(matriz, dtype=dtype)


def obter_dimensoes(matriz) -> Tuple[int, int]:
    """Obtém dimensões (linhas, colunas) de uma matriz"""
    valida, msg = validar_matriz(matriz)
    if not valida:
        raise ValueError(f"Matriz inválida: {msg}")
    
    if isinstance(matriz, np.ndarray):
        return matriz.shape[0], matriz.shape[1]
    return len(matriz), len(matriz[0])


def criar_matriz(linhas: int, colunas: int, tipo: str = "aleatoria", seed: int = 42) -> List[List[float]]:
    """
    Cria uma matriz M × N de diferentes tipos:
    - aleatoria: valores aleatórios entre 1-10
    - zeros: todos zeros
    - uns: todos uns
    - identidade: matriz identidade (apenas para quadráticas)
    - diagonal: diagonal com 1-10
    - triangular: triangular superior
    """
    if linhas <= 0 or colunas <= 0:
        raise ValueError(f"Dimensões inválidas: {linhas}×{colunas}")
    
    random.seed(seed)
    
    if tipo == "aleatoria":
        return [[random.randint(1, 10) for _ in range(colunas)] for _ in range(linhas)]
    
    elif tipo == "zeros":
        return [[0.0 for _ in range(colunas)] for _ in range(linhas)]
    
    elif tipo == "uns":
        return [[1.0 for _ in range(colunas)] for _ in range(linhas)]
    
    elif tipo == "identidade":
        if linhas != colunas:
            raise ValueError("Identidade requer matriz quadrática")
        matriz = [[0.0 for _ in range(colunas)] for _ in range(linhas)]
        for i in range(linhas):
            matriz[i][i] = 1.0
        return matriz
    
    elif tipo == "diagonal":
        matriz = [[0.0 for _ in range(colunas)] for _ in range(linhas)]
        for i in range(min(linhas, colunas)):
            matriz[i][i] = float(random.randint(1, 10))
        return matriz
    
    elif tipo == "triangular":
        return [[random.randint(1, 10) if j >= i else 0 for j in range(colunas)] for i in range(linhas)]
    
    else:
        raise ValueError(f"Tipo desconhecido: {tipo}. Use: aleatoria, zeros, uns, identidade, diagonal, triangular")


def matriz_para_numpy(matriz) -> np.ndarray:
    """Converte lista de listas para numpy array"""
    return np.array(matriz, dtype=np.float64)


def numpy_para_matriz(arr: np.ndarray) -> List[List[int]]:
    """Converte numpy array para lista de listas"""
    return arr.astype(int).tolist()


def matrizes_iguais(A, B, tolerancia: float = 0.001) -> bool:
    """Verifica se duas matrizes são iguais com tolerância (Python puro)"""
    try:
        valida_a, msg_a = validar_matriz(A)
        valida_b, msg_b = validar_matriz(B)
        
        if not (valida_a and valida_b):
            return False
        
        dim_a = obter_dimensoes(A)
        dim_b = obter_dimensoes(B)
        
        if dim_a != dim_b:
            return False
        
        m, n = dim_a
        
        # Converte para listas puras se necessário
        if isinstance(A, np.ndarray):
            A = A.tolist()
        if isinstance(B, np.ndarray):
            B = B.tolist()
        
        # Compara elemento a elemento com tolerância
        for i in range(m):
            for j in range(n):
                diferenca = abs(A[i][j] - B[i][j])
                if diferenca > tolerancia:
                    return False
        
        return True
    except:
        return False


def amostrar_matriz(matriz, max_linhas: int = 6, max_colunas: int = 6):
    """Retorna uma amostra da matriz (útil para matrizes grandes)"""
    try:
        valida, _ = validar_matriz(matriz)
        if not valida:
            return [[None]]
        
        if isinstance(matriz, np.ndarray):
            amostra = matriz[:max_linhas, :max_colunas]
            return amostra.tolist()
        
        return [linha[:max_colunas] for linha in matriz[:max_linhas]]
    except:
        return [[None]]


def descrever_matriz(matriz) -> dict:
    """Retorna descrição completa de uma matriz (Python puro)"""
    try:
        valida, msg = validar_matriz(matriz)
        if not valida:
            return {"valida": False, "erro": msg}
        
        linhas, colunas = obter_dimensoes(matriz)
        
        # Converte para lista pura se necessário
        if isinstance(matriz, np.ndarray):
            matriz = matriz.tolist()
        
        # Calcula estatísticas
        minimo = float('inf')
        maximo = float('-inf')
        soma = 0.0
        total_elementos = 0
        
        for linha in matriz:
            for elemento in linha:
                minimo = min(minimo, elemento)
                maximo = max(maximo, elemento)
                soma += elemento
                total_elementos += 1
        
        media = soma / total_elementos if total_elementos > 0 else 0.0
        
        # Calcula desvio padrão
        variancia = 0.0
        for linha in matriz:
            for elemento in linha:
                variancia += (elemento - media) ** 2
        variancia /= total_elementos if total_elementos > 0 else 1
        desvio = variancia ** 0.5
        
        return {
            "valida": True,
            "dimensoes": [linhas, colunas],
            "tipo": "quadrática" if linhas == colunas else "retangular",
            "total_elementos": total_elementos,
            "minimo": float(minimo),
            "maximo": float(maximo),
            "media": float(media),
            "desvio": float(desvio),
        }
    except Exception as e:
        return {"valida": False, "erro": str(e)}


# ═══════════════════════════════════════════════════════════════════
#  FUNÇÕES AUXILIARES (sem numpy)
# ═══════════════════════════════════════════════════════════════════

def _produto_escalar(v1: List[float], v2: List[float]) -> float:
    """Calcula o produto escalar entre dois vetores (Python puro)"""
    resultado = 0.0
    for i in range(len(v1)):
        resultado += v1[i] * v2[i]
    return resultado


def _transpor_matriz(matriz: List[List[float]]) -> List[List[float]]:
    """Transpõe uma matriz (Python puro)"""
    if not matriz:
        return []
    m = len(matriz)
    n = len(matriz[0])
    transposta = [[0.0 for _ in range(m)] for _ in range(n)]
    for i in range(m):
        for j in range(n):
            transposta[j][i] = matriz[i][j]
    return transposta


# ═══════════════════════════════════════════════════════════════════
#  MULTIPLICAÇÃO SERIAL (Python puro, sem numpy)
# ═══════════════════════════════════════════════════════════════════

def multiplicar_serial(A, B) -> List[List[float]]:
    """
    Multiplicação serial usando Python puro
    A: M × N
    B: N × P
    Resultado: M × P
    
    Suporta todos os tipos de matrizes (quadráticas, retangulares, etc)
    """
    # Validação
    valida_a, msg_a = validar_matriz(A)
    valida_b, msg_b = validar_matriz(B)
    
    if not valida_a:
        raise ValueError(f"Matriz A inválida: {msg_a}")
    if not valida_b:
        raise ValueError(f"Matriz B inválida: {msg_b}")
    
    m, n = obter_dimensoes(A)
    n_b, p = obter_dimensoes(B)
    
    if n != n_b:
        raise ValueError(f"Dimensões incompatíveis: A é {m}×{n}, B é {n_b}×{p}")
    
    # Converte para listas puras (remove numpy)
    if isinstance(A, np.ndarray):
        A = A.tolist()
    if isinstance(B, np.ndarray):
        B = B.tolist()
    
    # Transpõe B para acelerar acesso às colunas
    B_transposta = _transpor_matriz(B)
    
    # Calcula C = A × B usando Python puro
    C = []
    for i in range(m):
        linha_c = []
        for j in range(p):
            elemento = _produto_escalar(A[i], B_transposta[j])
            linha_c.append(elemento)
        C.append(linha_c)
    
    return C


# ═══════════════════════════════════════════════════════════════════
#  MULTIPLICAÇÃO PARALELA (multiprocessing com Python puro)
# ═══════════════════════════════════════════════════════════════════

def _bloco_paralelo(args):
    """
    Worker function para multiplicação paralela (Python puro)
    Calcula um bloco de linhas da matriz resultado
    """
    linhas_A, B_transposta, idx_bloco = args
    bloco_resultado = []
    
    # Para cada linha do bloco de A
    for linha_a in linhas_A:
        linha_c = []
        # Para cada coluna de B (que é uma linha de B_transposta)
        for coluna_b in B_transposta:
            # Produto escalar: elemento = linha_a · coluna_b
            elemento = _produto_escalar(linha_a, coluna_b)
            linha_c.append(elemento)
        bloco_resultado.append(linha_c)
    
    return idx_bloco, bloco_resultado


def multiplicar_paralelo(A, B, num_processos: int = 2) -> List[List[float]]:
    """
    Multiplicação paralela usando multiprocessing (Python puro)
    A: M × N
    B: N × P
    Resultado: M × P
    
    Suporta todos os tipos de matrizes
    """
    # Validação
    valida_a, msg_a = validar_matriz(A)
    valida_b, msg_b = validar_matriz(B)
    
    if not valida_a:
        raise ValueError(f"Matriz A inválida: {msg_a}")
    if not valida_b:
        raise ValueError(f"Matriz B inválida: {msg_b}")
    
    m, n = obter_dimensoes(A)
    n_b, p = obter_dimensoes(B)
    
    if n != n_b:
        raise ValueError(f"Dimensões incompatíveis: A é {m}×{n}, B é {n_b}×{p}")
    
    num_processos = max(1, min(num_processos, multiprocessing.cpu_count()))
    
    # Converte para listas puras (remove numpy)
    if isinstance(A, np.ndarray):
        A = A.tolist()
    if isinstance(B, np.ndarray):
        B = B.tolist()
    
    tam_bloco = max(1, m // num_processos)
    
    # Transpõe B uma vez (fora do loop)
    B_transposta = _transpor_matriz(B)
    
    # Divide A em blocos de linhas
    tarefas = []
    for i in range(0, m, tam_bloco):
        fim = min(i + tam_bloco, m)
        linhas_bloco = A[i:fim]
        tarefas.append((linhas_bloco, B_transposta, i))
    
    # Processa em paralelo
    with multiprocessing.Pool(processes=num_processos) as pool:
        resultados = pool.map(_bloco_paralelo, tarefas)
    
    # Monta resultado (mantém ordem)
    C = [None] * m
    for idx_bloco, bloco in resultados:
        fim_bloco = min(idx_bloco + tam_bloco, m)
        for i, linha in enumerate(bloco):
            C[idx_bloco + i] = linha
    
    return C


# ═══════════════════════════════════════════════════════════════════
#  MULTIPLICAÇÃO DISTRIBUÍDA (simulado, Python puro)
# ═══════════════════════════════════════════════════════════════════

def multiplicar_distribuido(A, B, num_nodos: int = 2) -> List[List[float]]:
    """
    Simula multiplicação distribuída entre múltiplos 'nodos' (Python puro)
    Cada nodo calcula um bloco de linhas de A
    A: M × N
    B: N × P
    Resultado: M × P
    
    Suporta todos os tipos de matrizes
    """
    # Validação
    valida_a, msg_a = validar_matriz(A)
    valida_b, msg_b = validar_matriz(B)
    
    if not valida_a:
        raise ValueError(f"Matriz A inválida: {msg_a}")
    if not valida_b:
        raise ValueError(f"Matriz B inválida: {msg_b}")
    
    m, n = obter_dimensoes(A)
    n_b, p = obter_dimensoes(B)
    
    if n != n_b:
        raise ValueError(f"Dimensões incompatíveis: A é {m}×{n}, B é {n_b}×{p}")
    
    num_nodos = max(1, num_nodos)
    
    # Converte para listas puras (remove numpy)
    if isinstance(A, np.ndarray):
        A = A.tolist()
    if isinstance(B, np.ndarray):
        B = B.tolist()
    
    tam_bloco = max(1, m // num_nodos)
    
    # Transpõe B uma vez (para otimizar)
    B_transposta = _transpor_matriz(B)
    
    # Inicializa resultado
    C = [None] * m
    
    # Simula comunicação e cálculo distribuído
    for nodo_id in range(num_nodos):
        inicio = nodo_id * tam_bloco
        fim = min(inicio + tam_bloco, m) if nodo_id < num_nodos - 1 else m
        
        # Simula: nodo recebe seu bloco de A e B
        linhas_bloco = A[inicio:fim]
        
        # Calcula o bloco de resultado
        for i, linha_a in enumerate(linhas_bloco):
            linha_c = []
            for coluna_b in B_transposta:
                elemento = _produto_escalar(linha_a, coluna_b)
                linha_c.append(elemento)
            C[inicio + i] = linha_c
    
    return C


# ═══════════════════════════════════════════════════════════════════
#  MULTIPLICAÇÃO DISTRIBUÍDA REAL (via Socket)
# ═══════════════════════════════════════════════════════════════════

def multiplicar_distribuido_real(A, B, ip_servidor: str = '172.19.9.43', porta: int = 5001) -> List[List[float]]:
    """
    Multiplicação distribuída REAL usando socket para se conectar a servidor remoto
    A: M × N
    B: N × P
    Resultado: M × P
    
    IP_SERVIDOR PADRÃO: 172.19.9.43 (seu servidor)
    CLIENTE: 172.19.9.44 (seu PC)
    
    Uso:
        resultado = multiplicar_distribuido_real(A, B, ip_servidor='172.19.9.43')
    """
    # Validação
    valida_a, msg_a = validar_matriz(A)
    valida_b, msg_b = validar_matriz(B)
    
    if not valida_a:
        raise ValueError(f"Matriz A inválida: {msg_a}")
    if not valida_b:
        raise ValueError(f"Matriz B inválida: {msg_b}")
    
    m, n = obter_dimensoes(A)
    n_b, p = obter_dimensoes(B)
    
    if n != n_b:
        raise ValueError(f"Dimensões incompatíveis: A é {m}×{n}, B é {n_b}×{p}")
    
    # Converte para numpy para usar socket_client
    if not isinstance(A, np.ndarray):
        A = np.array(A, dtype=np.float64)
    if not isinstance(B, np.ndarray):
        B = np.array(B, dtype=np.float64)
    
    # Importa cliente socket
    try:
        from socket_client import ClienteSocket
    except ImportError:
        print("❌ Erro: Não conseguiu importar ClienteSocket")
        print("   Certifique-se de que socket_client.py está no mesmo diretório")
        raise
    
    # Conecta ao servidor
    cliente = ClienteSocket(ip_servidor, porta, timeout=30)
    
    if not cliente.conectar():
        raise ConnectionError(f"Não conseguiu conectar ao servidor {ip_servidor}:{porta}")
    
    try:
        # Envia toda a matriz A para o servidor processar
        print(f"📤 Enviando matrizes para {ip_servidor}:{porta}...")
        resultado = cliente.multiplicar_bloco(A, B, inicio_linha=0)
        
        if resultado and resultado.get('status') == 'sucesso':
            C = resultado.get('resultado')
            cliente.fechar()
            return C
        else:
            raise RuntimeError(f"Erro no servidor: {resultado.get('mensagem', 'Desconhecido')}")
    
    except Exception as e:
        cliente.fechar()
        raise


# ═══════════════════════════════════════════════════════════════════
#  TESTES E BENCHMARKS
# ═══════════════════════════════════════════════════════════════════

def executar_benchmark(
    m: int,
    n: int,
    p: int,
    num_processos: int = 2,
    num_nodos: int = 2,
    seed_a: int = 1,
    seed_b: int = 2,
    tipo_matriz: str = "aleatoria"
) -> dict:
    """
    Executa benchmark completo: serial, paralelo e distribuído
    Suporta todos os tipos de matrizes
    
    Parâmetros:
    - m, n, p: dimensões (A: m×n, B: n×p, C: m×p)
    - num_processos: número de processos para paralelização
    - num_nodos: número de nodos simulados
    - seed_a, seed_b: seeds para geração de matrizes
    - tipo_matriz: tipo de valores (aleatoria, zeros, uns, identidade, diagonal, triangular)
    
    Retorna: dict com tempos, speedups, eficiência, validação
    """
    
    # Validação de dimensões
    if m <= 0 or n <= 0 or p <= 0:
        raise ValueError(f"Dimensões inválidas: {m}×{n}×{p}")
    
    if m > 10000 or n > 10000 or p > 10000:
        raise ValueError(f"Dimensões muito grandes (máximo 10000×10000×10000)")
    
    # Gera matrizes
    try:
        A = criar_matriz(m, n, tipo=tipo_matriz, seed=seed_a)
        B = criar_matriz(n, p, tipo=tipo_matriz, seed=seed_b)
    except Exception as e:
        raise ValueError(f"Erro ao criar matrizes: {str(e)}")
    
    # Serial
    t0 = time.perf_counter()
    try:
        C_serial = multiplicar_serial(A, B)
    except Exception as e:
        raise ValueError(f"Erro na multiplicação serial: {str(e)}")
    t_serial = time.perf_counter() - t0
    
    # Paralelo
    t1 = time.perf_counter()
    try:
        C_paralelo = multiplicar_paralelo(A, B, num_processos)
    except Exception as e:
        raise ValueError(f"Erro na multiplicação paralela: {str(e)}")
    t_paralelo = time.perf_counter() - t1
    
    # Distribuído (REAL com Socket)
    t2 = time.perf_counter()
    try:
        # Usa socket real para conectar ao servidor 172.19.9.43
        print("[+] Tentando conectar ao servidor distribuído (172.19.9.43:5001)...")
        C_distribuido = multiplicar_distribuido_real(A, B, ip_servidor='172.19.9.43', porta=5001)
        print("[✓] Multiplicação distribuída concluída!")
    except Exception as e:
        print(f"[⚠] Aviso: Distribuição real falhou, usando simulada: {str(e)}")
        # Fallback para simulado se socket falhar
        C_distribuido = multiplicar_distribuido(A, B, num_nodos)
    t_distribuido = time.perf_counter() - t2
    
    # Validação
    valido_paralelo = matrizes_iguais(C_serial, C_paralelo)
    valido_distribuido = matrizes_iguais(C_serial, C_distribuido)
    
    # Cálculos
    speedup_paralelo = t_serial / t_paralelo if t_paralelo > 0 else 0
    speedup_distribuido = t_serial / t_distribuido if t_distribuido > 0 else 0
    eficiencia_paralelo = (speedup_paralelo / num_processos * 100) if t_paralelo > 0 else 0
    eficiencia_distribuido = (speedup_distribuido / num_nodos * 100) if t_distribuido > 0 else 0
    
    amostra = amostrar_matriz(C_serial, 6, 6)
    
    return {
        "dimensoes": {"A": [m, n], "B": [n, p], "C": [m, p]},
        "tipo_matriz": tipo_matriz,
        "tempos": {
            "serial": round(t_serial, 6),
            "paralelo": round(t_paralelo, 6),
            "distribuido": round(t_distribuido, 6),
        },
        "speedups": {
            "paralelo": round(speedup_paralelo, 4),
            "distribuido": round(speedup_distribuido, 4),
        },
        "eficiencia": {
            "paralelo": round(eficiencia_paralelo, 2),
            "distribuido": round(eficiencia_distribuido, 2),
        },
        "validacao": {
            "paralelo": valido_paralelo,
            "distribuido": valido_distribuido,
        },
        "overhead_paralelo": round(t_paralelo - t_serial, 6),
        "overhead_distribuido": round(t_distribuido - t_serial, 6),
        "amostra_resultado": amostra,
        "num_processos": num_processos,
        "num_nodos": num_nodos,
        "matrizes": {
            "A": A,
            "B": B,
            "C": C_serial,
        },
    }



def teste_tipos_matrizes() -> dict:
    """
    Testa todos os tipos de matrizes suportados
    Retorna resultados de testes para:
    - Quadráticas
    - Retangulares (mais linhas)
    - Retangulares (mais colunas)
    - 1×1, 1×N, M×1
    - Matrizes especiais (zeros, uns, identidade, diagonal, triangular)
    """
    resultados = {}
    
    casos = [
        # (nome, m, n, p, tipo)
        ("Quadrática 3×3", 3, 3, 3, "aleatoria"),
        ("Retangular 4×3", 4, 3, 3, "aleatoria"),
        ("Retangular 3×4", 3, 4, 4, "aleatoria"),
        ("Vetor linha 1×5", 1, 5, 5, "aleatoria"),
        ("Vetor coluna 5×1", 5, 1, 1, "aleatoria"),
        ("1×1", 1, 1, 1, "aleatoria"),
        ("Grandes 100×100", 100, 100, 100, "aleatoria"),
        ("Zeros", 3, 3, 3, "zeros"),
        ("Uns", 3, 3, 3, "uns"),
        ("Identidade", 4, 4, 4, "identidade"),
        ("Diagonal", 4, 4, 4, "diagonal"),
        ("Triangular", 4, 4, 4, "triangular"),
    ]
    
    for nome, m, n, p, tipo in casos:
        try:
            resultado = executar_benchmark(m, n, p, num_processos=2, num_nodos=2, tipo_matriz=tipo)
            resultados[nome] = {
                "status": "✓ OK",
                "dimensoes": resultado["dimensoes"],
                "tipo_matriz": tipo,
                "tempos": resultado["tempos"],
            }
        except Exception as e:
            resultados[nome] = {
                "status": "✗ ERRO",
                "erro": str(e),
            }
    
    return resultados


def teste_tipos_entrada() -> dict:
    """
    Testa se as funções aceitam diferentes tipos de entrada:
    - Listas de listas
    - Numpy arrays
    - Tuples
    """
    resultados = {}
    
    # Cria matrizes em diferentes formatos
    A_lista = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    A_numpy = np.array(A_lista, dtype=np.float64)
    A_tuple = tuple(tuple(row) for row in A_lista)
    
    B_lista = [[1, 2], [3, 4], [5, 6]]
    B_numpy = np.array(B_lista, dtype=np.float64)
    B_tuple = tuple(tuple(row) for row in B_lista)
    
    # Testa combinações
    combos = [
        ("Lista × Lista", A_lista, B_lista),
        ("NumPy × NumPy", A_numpy, B_numpy),
        ("Tuple × Tuple", A_tuple, B_tuple),
        ("Lista × NumPy", A_lista, B_numpy),
        ("NumPy × Lista", A_numpy, B_lista),
    ]
    
    for nome, A, B in combos:
        try:
            C = multiplicar_serial(A, B)
            resultados[nome] = {
                "status": "✓ OK",
                "tipo_resultado": type(C).__name__,
                "dimensoes": [len(C), len(C[0])],
            }
        except Exception as e:
            resultados[nome] = {
                "status": "✗ ERRO",
                "erro": str(e),
            }
    
    return resultados


def teste_validacoes() -> dict:
    """
    Testa se as validações funcionam corretamente
    para matrizes inválidas e dimensões incompatíveis
    """
    resultados = {}
    
    casos_invalidos = [
        ("None", None),
        ("String", "nao_eh_matriz"),
        ("Lista vazia", []),
        ("Linhas desiguais", [[1, 2], [3, 4, 5]]),
        ("Colunas vazias", [[None], [None]]),
    ]
    
    for nome, matriz in casos_invalidos:
        valida, msg = validar_matriz(matriz)
        resultados[nome] = {
            "valida": valida,
            "mensagem": msg,
        }
    
    # Testes de dimensões incompatíveis
    A = [[1, 2, 3], [4, 5, 6]]
    B = [[1, 2], [3, 4]]  # B precisa ter 3 linhas
    
    try:
        multiplicar_serial(A, B)
        resultados["Dimensões incompatíveis"] = {
            "status": "✗ FALHOU", 
            "mensagem": "Deveria ter lançado erro"
        }
    except ValueError as e:
        resultados["Dimensões incompatíveis"] = {
            "status": "✓ OK", 
            "erro_detectado": str(e)
        }
    
    return resultados


if __name__ == "__main__":
    # Testes rápidos
    print("=" * 60)
    print("TESTE 1: Validações")
    print("=" * 60)
    testes = teste_validacoes()
    for nome, resultado in testes.items():
        print(f"{nome}: {resultado.get('valida', resultado.get('status'))}")
    
    print("\n" + "=" * 60)
    print("TESTE 2: Tipos de entrada")
    print("=" * 60)
    testes = teste_tipos_entrada()
    for nome, resultado in testes.items():
        print(f"{nome}: {resultado['status']}")
    
    print("\n" + "=" * 60)
    print("TESTE 3: Tipos de matrizes (amostra)")
    print("=" * 60)
    testes = teste_tipos_matrizes()
    for nome, resultado in testes.items():
        status = resultado['status']
        if 'erro' in resultado:
            print(f"{nome}: {status} - {resultado['erro'][:50]}")
        else:
            print(f"{nome}: {status}")
    
    print("\n" + "=" * 60)
    print("TESTE 4: Benchmark 50×50")
    print("=" * 60)
    resultado = executar_benchmark(50, 50, 50, num_processos=2, num_nodos=2)
    print(f"Serial: {resultado['tempos']['serial']}s")
    print(f"Paralelo: {resultado['tempos']['paralelo']}s")
    print(f"Distribuído: {resultado['tempos']['distribuido']}s")
