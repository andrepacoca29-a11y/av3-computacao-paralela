#!/usr/bin/env python
"""
EXEMPLOS DE USO — Multiplicação Distribuída de Matrizes
Demonstra como usar os módulos do projeto diretamente
"""

from matrix_operations import executar_benchmark, criar_matriz, multiplicar_serial, multiplicar_paralelo
from graphics import GeradorGraficos, salvar_resultados_json, gerar_relatorio_html
import json


def exemplo_1_uso_basico():
    """Uso básico das funções de multiplicação"""
    print("\n" + "="*60)
    print("EXEMPLO 1: Multiplicação Básica")
    print("="*60)
    
    # Cria matrizes pequenas
    A = criar_matriz(10, 10, seed=1)
    B = criar_matriz(10, 10, seed=2)
    
    print(f"\nA: {len(A)}×{len(A[0])}")
    print(f"B: {len(B)}×{len(B[0])}")
    
    # Multiplicação serial
    C = multiplicar_serial(A, B)
    print(f"C = A × B: {len(C)}×{len(C[0])}")
    print(f"C[0][0] = {C[0][0]}")


def exemplo_2_matrizes_nao_quadraticas():
    """Exemplos com matrizes não-quadráticas"""
    print("\n" + "="*60)
    print("EXEMPLO 2: Matrizes Não-Quadráticas")
    print("="*60)
    
    # A: 50×30, B: 30×40, C: 50×40
    A = criar_matriz(50, 30, seed=1)
    B = criar_matriz(30, 40, seed=2)
    
    print(f"\nA: {len(A)}×{len(A[0])} (50×30)")
    print(f"B: {len(B)}×{len(B[0])} (30×40)")
    
    C = multiplicar_serial(A, B)
    print(f"C: {len(C)}×{len(C[0])} (50×40)")
    print(f"Amostra C[0:3, 0:3]:")
    for i in range(3):
        print(f"  {C[i][:3]}")


def exemplo_3_benchmark_completo():
    """Executa benchmark completo"""
    print("\n" + "="*60)
    print("EXEMPLO 3: Benchmark Completo")
    print("="*60)
    
    # Benchmark com matrizes 100×100
    resultado = executar_benchmark(m=100, n=100, p=100, num_processos=4, num_nodos=2)
    
    print(f"\nDimensões: A={resultado['dimensoes']['A']}, B={resultado['dimensoes']['B']}")
    print(f"\nTempos (segundos):")
    print(f"  Serial:      {resultado['tempos']['serial']:.6f}s")
    print(f"  Paralelo:    {resultado['tempos']['paralelo']:.6f}s")
    print(f"  Distribuído: {resultado['tempos']['distribuido']:.6f}s")
    
    print(f"\nSpeedup:")
    print(f"  Paralelo:    {resultado['speedups']['paralelo']:.4f}×")
    print(f"  Distribuído: {resultado['speedups']['distribuido']:.4f}×")
    
    print(f"\nEficiência:")
    print(f"  Paralelo:    {resultado['eficiencia']['paralelo']:.2f}%")
    print(f"  Distribuído: {resultado['eficiencia']['distribuido']:.2f}%")
    
    print(f"\nOverhead:")
    print(f"  Paralelo:    {resultado['overhead_paralelo']:.6f}s")
    print(f"  Distribuído: {resultado['overhead_distribuido']:.6f}s")
    
    print(f"\nValidação:")
    print(f"  Paralelo ok?    {resultado['validacao']['paralelo']}")
    print(f"  Distribuído ok? {resultado['validacao']['distribuido']}")
    
    return resultado


def exemplo_4_multiplos_testes():
    """Executa múltiplos testes com diferentes tamanhos"""
    print("\n" + "="*60)
    print("EXEMPLO 4: Múltiplos Testes (para gráficos)")
    print("="*60)
    
    tamanhos = [50, 100, 150, 200]
    resultados = []
    
    for tamanho in tamanhos:
        print(f"\nTestando {tamanho}×{tamanho}...")
        resultado = executar_benchmark(
            m=tamanho, n=tamanho, p=tamanho,
            num_processos=4, num_nodos=2
        )
        resultados.append(resultado)
        print(f"  Serial: {resultado['tempos']['serial']:.4f}s")
        print(f"  Paralelo: {resultado['tempos']['paralelo']:.4f}s")
        print(f"  Speedup: {resultado['speedups']['paralelo']:.4f}×")
    
    return resultados


def exemplo_5_gerar_graficos(resultados):
    """Gera gráficos a partir dos resultados"""
    print("\n" + "="*60)
    print("EXEMPLO 5: Gerando Gráficos")
    print("="*60)
    
    print("\nGerando gráficos...")
    gerador = GeradorGraficos(diretorio_saida="resultados_exemplo")
    
    graficos = gerador.gerar_todos(resultados)
    
    print("\nGráficos gerados:")
    for nome, caminho in graficos.items():
        print(f"  ✓ {nome}: {caminho}")
    
    # Salva resultados em JSON
    salvar_resultados_json(resultados, "resultados_exemplo/teste.json")
    
    # Gera relatório HTML
    relatorio = gerar_relatorio_html(resultados, graficos, "resultados_exemplo/teste.html")
    print(f"\n  ✓ Relatório HTML: {relatorio}")


def exemplo_6_analise_dados():
    """Análise dos dados coletados"""
    print("\n" + "="*60)
    print("EXEMPLO 6: Análise de Dados")
    print("="*60)
    
    resultado = executar_benchmark(m=150, n=150, p=150, num_processos=4)
    
    print(f"\nAnálise para matriz 150×150:")
    
    # Calcula razões
    razao_paralelo_serial = resultado['tempos']['paralelo'] / resultado['tempos']['serial']
    razao_distribuido_serial = resultado['tempos']['distribuido'] / resultado['tempos']['serial']
    
    print(f"\nRazões de tempo (vs serial):")
    print(f"  Paralelo/Serial:    {razao_paralelo_serial:.4f}")
    print(f"  Distribuído/Serial: {razao_distribuido_serial:.4f}")
    
    # Determina se paralelização é vantajosa
    print(f"\nAnálise:")
    if razao_paralelo_serial < 1.0:
        ganho = (1 - razao_paralelo_serial) * 100
        print(f"  ✓ Paralelização trouxe ganho de {ganho:.1f}%")
    elif razao_paralelo_serial > 1.2:
        perda = (razao_paralelo_serial - 1) * 100
        print(f"  ⚠ Overhead dominou, perda de {perda:.1f}%")
    else:
        print(f"  ◎ Está no ponto de equilíbrio (overhead ≈ ganho)")
    
    # Calcula limite de break-even
    print(f"\nMétricas de eficiência:")
    print(f"  Operações: {150 * 150 * 150:,} multiplicações")
    print(f"  Tempo por operação (serial): {resultado['tempos']['serial'] / (150*150*150) * 1e9:.3f} ns")
    print(f"  Tempo por operação (paralelo): {resultado['tempos']['paralelo'] / (150*150*150) * 1e9:.3f} ns")


if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════╗
║     EXEMPLOS DE USO - Multiplicação Distribuída          ║
║     de Matrizes — AV2 2026                               ║
╚════════════════════════════════════════════════════════════╝
""")
    
    # Executa exemplos
    exemplo_1_uso_basico()
    exemplo_2_matrizes_nao_quadraticas()
    resultado = exemplo_3_benchmark_completo()
    exemplo_6_analise_dados()
    
    # Exemplos que geram arquivos (comentados por padrão)
    # resultados = exemplo_4_multiplos_testes()
    # exemplo_5_gerar_graficos(resultados)
    
    print("\n" + "="*60)
    print("Exemplos concluídos!")
    print("="*60)
    print("""
Para usar a interface web, execute:
  python app.py

Para mais informações, leia:
  - README.md
  - QUICKSTART.txt
""")
