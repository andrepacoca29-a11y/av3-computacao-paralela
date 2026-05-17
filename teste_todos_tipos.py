#!/usr/bin/env python3
"""
TESTE COMPLETO: Todos os tipos de matrizes suportados
Demonstra que o sistema pode trabalhar com:
- Matrizes quadráticas (M×M)
- Matrizes retangulares (M×N com M≠N)
- Vetores (1×N, M×1)
- Casos extremos (1×1)
- Matrizes especiais (zeros, uns, identidade, diagonal, triangular)
- Diferentes tipos de entrada (listas, numpy arrays, tuples)
"""

import sys
import json
from datetime import datetime
from matrix_operations import (
    criar_matriz,
    multiplicar_serial,
    multiplicar_paralelo,
    multiplicar_distribuido,
    executar_benchmark,
    teste_tipos_matrizes,
    teste_tipos_entrada,
    teste_validacoes,
    descrever_matriz,
    amostrar_matriz,
    validar_matriz,
    obter_dimensoes,
)


def linha(char="=", tamanho=80):
    """Imprime uma linha de separação"""
    print(char * tamanho)


def titulo(texto):
    """Imprime um título com formatação"""
    linha()
    print(f"  {texto}")
    linha()


def secao(texto):
    """Imprime uma seção"""
    print(f"\n▶ {texto}")
    print("-" * 60)


def teste_1_tipos_basicos():
    """Testa tipos básicos de matrizes"""
    titulo("TESTE 1: TIPOS BÁSICOS DE MATRIZES")
    
    casos = [
        ("Quadrática 2×2", 2, 2, 2),
        ("Quadrática 3×3", 3, 3, 3),
        ("Retangular 2×3 × 3×2", 2, 3, 2),
        ("Retangular 3×2 × 2×3", 3, 2, 3),
        ("Vetor linha 1×3 × 3×2", 1, 3, 2),
        ("Vetor coluna 3×1 × 1×2", 3, 1, 2),
        ("1×1", 1, 1, 1),
    ]
    
    for nome, m, n, p in casos:
        try:
            A = criar_matriz(m, n, seed=1)
            B = criar_matriz(n, p, seed=2)
            C = multiplicar_serial(A, B)
            print(f"✓ {nome:30} → Resultado {len(C)}×{len(C[0])}")
        except Exception as e:
            print(f"✗ {nome:30} → ERRO: {str(e)[:40]}")


def teste_2_tipos_especiais():
    """Testa matrizes especiais"""
    titulo("TESTE 2: MATRIZES ESPECIAIS")
    
    tipos = ["zeros", "uns", "identidade", "diagonal", "triangular"]
    
    for tipo in tipos:
        try:
            A = criar_matriz(3, 3, tipo=tipo, seed=1)
            B = criar_matriz(3, 3, tipo="aleatoria", seed=2)
            C = multiplicar_serial(A, B)
            
            desc = descrever_matriz(A)
            print(f"✓ Matriz {tipo:12} (3×3)")
            print(f"  ├─ Min: {desc['minimo']:6.2f}, Max: {desc['maximo']:6.2f}")
            print(f"  ├─ Média: {desc['media']:6.2f}, Desvio: {desc['desvio']:6.2f}")
            print(f"  └─ Resultado: {len(C)}×{len(C[0])}")
        except Exception as e:
            print(f"✗ Matriz {tipo:12} → ERRO: {str(e)[:40]}")


def teste_3_tipos_entrada():
    """Testa diferentes tipos de entrada"""
    titulo("TESTE 3: TIPOS DE ENTRADA")
    
    import numpy as np
    
    A_lista = [[1, 2], [3, 4], [5, 6]]
    A_numpy = np.array(A_lista, dtype=np.float64)
    A_tuple = tuple(tuple(row) for row in A_lista)
    
    B_lista = [[1, 2, 3], [4, 5, 6]]
    B_numpy = np.array(B_lista, dtype=np.float64)
    
    tipos_entrada = [
        ("Lista × Lista", A_lista, B_lista),
        ("NumPy × NumPy", A_numpy, B_numpy),
        ("Tuple × Tuple", A_tuple, tuple(tuple(row) for row in B_lista)),
        ("Lista × NumPy", A_lista, B_numpy),
        ("NumPy × Lista", A_numpy, B_lista),
    ]
    
    for nome, A, B in tipos_entrada:
        try:
            C = multiplicar_serial(A, B)
            dim_c = (len(C), len(C[0]))
            print(f"✓ {nome:20} → Resultado {dim_c}")
        except Exception as e:
            print(f"✗ {nome:20} → ERRO: {str(e)[:40]}")


def teste_4_validacoes():
    """Testa validações de matrizes inválidas"""
    titulo("TESTE 4: VALIDAÇÕES")
    
    casos_invalidos = [
        ("None", None),
        ("String", "matriz"),
        ("Lista vazia", []),
        ("Linhas desiguais", [[1, 2], [3, 4, 5]]),
        ("Integer", 42),
        ("Float", 3.14),
    ]
    
    for nome, matriz in casos_invalidos:
        valida, msg = validar_matriz(matriz)
        status = "✗ Corretamente rejeitada" if not valida else "✓ Aceita"
        print(f"{status}: {nome:20} - {msg}")


def teste_5_dimensoes_incompativeis():
    """Testa detecção de dimensões incompatíveis"""
    titulo("TESTE 5: DIMENSÕES INCOMPATÍVEIS")
    
    casos = [
        ("2×3 × 2×3", [[1, 2, 3], [4, 5, 6]], [[1, 2, 3], [4, 5, 6]]),
        ("3×3 × 2×3", [[1]*3]*3, [[1]*3]*2),
        ("1×5 × 3×2", [[1]*5], [[1]*2]*3),
    ]
    
    for nome, A, B in casos:
        try:
            C = multiplicar_serial(A, B)
            print(f"✗ {nome:20} → ACEITA (erro na validação!)")
        except ValueError as e:
            print(f"✓ {nome:20} → Corretamente rejeitada")
            print(f"  └─ {str(e)[:50]}")


def teste_6_algoritmos():
    """Testa e compara os três algoritmos"""
    titulo("TESTE 6: COMPARAÇÃO DE ALGORITMOS")
    
    casos = [
        ("Pequena 10×10", 10, 10, 10),
        ("Média 50×50", 50, 50, 50),
        ("Retangular 20×30", 20, 30, 20),
    ]
    
    for nome, m, n, p in casos:
        print(f"\n{nome}:")
        try:
            A = criar_matriz(m, n, seed=1)
            B = criar_matriz(n, p, seed=2)
            
            # Serial
            import time
            t0 = time.perf_counter()
            C_serial = multiplicar_serial(A, B)
            t_serial = time.perf_counter() - t0
            
            # Paralelo
            t1 = time.perf_counter()
            C_paralelo = multiplicar_paralelo(A, B, 2)
            t_paralelo = time.perf_counter() - t1
            
            # Distribuído
            t2 = time.perf_counter()
            C_distribuido = multiplicar_distribuido(A, B, 2)
            t_distribuido = time.perf_counter() - t2
            
            print(f"  Serial:       {t_serial*1000:8.3f} ms")
            print(f"  Paralelo (2):  {t_paralelo*1000:8.3f} ms (speedup: {t_serial/t_paralelo:.2f}x)")
            print(f"  Distribuído:   {t_distribuido*1000:8.3f} ms (speedup: {t_serial/t_distribuido:.2f}x)")
            
        except Exception as e:
            print(f"  ✗ ERRO: {str(e)[:50]}")


def teste_7_casos_extremos():
    """Testa casos extremos"""
    titulo("TESTE 7: CASOS EXTREMOS")
    
    casos = [
        ("1×1 com 1×1", 1, 1, 1),
        ("1×100 com 100×1", 1, 100, 1),
        ("100×1 com 1×100", 100, 1, 100),
        ("Vetor linha muito grande 1×500", 1, 500, 500),
        ("Vetor coluna muito grande 500×1", 500, 1, 1),
    ]
    
    for nome, m, n, p in casos:
        try:
            A = criar_matriz(m, n, seed=1)
            B = criar_matriz(n, p, seed=2)
            C = multiplicar_serial(A, B)
            dim_c = (len(C), len(C[0]))
            print(f"✓ {nome:35} → {dim_c}")
        except Exception as e:
            print(f"✗ {nome:35} → ERRO: {str(e)[:35]}")


def teste_8_benchmark_completo():
    """Executa benchmark completo"""
    titulo("TESTE 8: BENCHMARK COMPLETO")
    
    tamanhos = [
        ("Pequena", 25, 25, 25),
        ("Média", 100, 100, 100),
    ]
    
    for nome, m, n, p in tamanhos:
        print(f"\n{nome} ({m}×{n} × {n}×{p}):")
        try:
            resultado = executar_benchmark(m, n, p, num_processos=2, num_nodos=2)
            
            print(f"  Serial:       {resultado['tempos']['serial']*1000:8.3f} ms")
            print(f"  Paralelo:     {resultado['tempos']['paralelo']*1000:8.3f} ms")
            print(f"  Distribuído:  {resultado['tempos']['distribuido']*1000:8.3f} ms")
            print(f"  Validação: Paralelo={resultado['validacao']['paralelo']}, Distribuído={resultado['validacao']['distribuido']}")
            
        except Exception as e:
            print(f"  ✗ ERRO: {str(e)[:50]}")


def gerar_relatorio():
    """Gera relatório final em JSON"""
    titulo("GERANDO RELATÓRIO FINAL")
    
    relatorio = {
        "timestamp": datetime.now().isoformat(),
        "testes_tipos_matrizes": teste_tipos_matrizes(),
        "testes_tipos_entrada": teste_tipos_entrada(),
        "testes_validacoes": teste_validacoes(),
    }
    
    # Salva em arquivo
    with open("relatorio_tipos_matrizes.json", "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    
    print("\n✓ Relatório salvo em: relatorio_tipos_matrizes.json")
    
    # Resumo
    print("\nRESUMO:")
    print(f"  Tipos de matrizes testados: {len(relatorio['testes_tipos_matrizes'])}")
    ok_tipos = sum(1 for t in relatorio['testes_tipos_matrizes'].values() if 'OK' in t.get('status', ''))
    print(f"  ├─ OK: {ok_tipos}")
    print(f"  └─ ERRO: {len(relatorio['testes_tipos_matrizes']) - ok_tipos}")
    
    print(f"  Tipos de entrada testados: {len(relatorio['testes_tipos_entrada'])}")
    ok_entrada = sum(1 for t in relatorio['testes_tipos_entrada'].values() if 'OK' in t.get('status', ''))
    print(f"  ├─ OK: {ok_entrada}")
    print(f"  └─ ERRO: {len(relatorio['testes_tipos_entrada']) - ok_entrada}")


def main():
    """Executa todos os testes"""
    print("\n")
    linha("═", 80)
    print("  SUITE DE TESTES COMPLETA: TODOS OS TIPOS DE MATRIZES")
    linha("═", 80)
    
    try:
        teste_1_tipos_basicos()
        teste_2_tipos_especiais()
        teste_3_tipos_entrada()
        teste_4_validacoes()
        teste_5_dimensoes_incompativeis()
        teste_6_algoritmos()
        teste_7_casos_extremos()
        teste_8_benchmark_completo()
        gerar_relatorio()
        
        linha("═", 80)
        print("  ✓ TODOS OS TESTES COMPLETOS")
        linha("═", 80)
        
    except Exception as e:
        print(f"\n✗ ERRO CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
