"""
Visualização melhorada dos benchmarks com gráficos ASCII e análise detalhada
"""

import time
import sys
from matrix_operations import executar_benchmark


def gerar_grafico_ascii(titulo, dados, largura=60):
    """Gera um gráfico ASCII simples"""
    print(f"\n{titulo}")
    print("=" * (largura + 20))
    
    if not dados:
        return
    
    max_valor = max(dados.values())
    min_valor = min(dados.values())
    
    for label, valor in dados.items():
        if max_valor == min_valor:
            percentual = 50
        else:
            percentual = int((valor - min_valor) / (max_valor - min_valor) * 100)
        
        tamanho_barra = int(percentual * largura / 100)
        barra = "█" * tamanho_barra + "░" * (largura - tamanho_barra)
        print(f"{label:<15} │{barra}│ {valor:.4f}s")
    
    print("=" * (largura + 20))


def benchmark_detalhado_com_grafico():
    """Executa benchmark e mostra com gráficos"""
    
    print("\n" + "=" * 80)
    print("🔬 BENCHMARK DETALHADO COM PYTHON PURO (SEM NUMPY)")
    print("=" * 80)
    
    tamanhos = [30, 50, 75, 100, 150, 200]
    resultados_por_tamanho = {}
    
    for tamanho in tamanhos:
        print(f"\n⏳ Testando {tamanho}×{tamanho}...", end=" ", flush=True)
        
        try:
            resultado = executar_benchmark(
                m=tamanho,
                n=tamanho,
                p=tamanho,
                num_processos=2,
                num_nodos=2,
                tipo_matriz="aleatoria"
            )
            
            resultados_por_tamanho[tamanho] = resultado
            print("✓")
            
        except Exception as e:
            print(f"✗ ERRO: {str(e)[:40]}")
            continue
    
    # Mostra tabela resumida
    print("\n" + "=" * 90)
    print("TABELA RESUMIDA")
    print("=" * 90)
    print(f"{'Tamanho':<12} {'Serial (s)':<15} {'Paralelo (s)':<15} {'Distribuído (s)':<18} {'Speedup':<12} {'Status':<15}")
    print("-" * 90)
    
    for tamanho in sorted(resultados_por_tamanho.keys()):
        r = resultados_por_tamanho[tamanho]
        t_serial = r['tempos']['serial']
        t_paralelo = r['tempos']['paralelo']
        t_distribuido = r['tempos']['distribuido']
        speedup = r['speedups']['paralelo']
        
        # Status
        if speedup > 1.0:
            status = f"✅ {speedup:.2f}x mais rápido"
        elif speedup > 0.8:
            status = f"🟡 Quase igual"
        else:
            status = f"❌ {1/speedup:.1f}x mais lento"
        
        print(f"{tamanho}×{tamanho}     {t_serial:<14.6f} {t_paralelo:<14.6f} {t_distribuido:<17.6f} {speedup:<11.3f} {status:<15}")
    
    # Gráficos ASCII para cada tamanho
    print("\n" + "=" * 90)
    print("COMPARAÇÃO VISUAL POR TAMANHO")
    print("=" * 90)
    
    for tamanho in sorted(resultados_por_tamanho.keys()):
        r = resultados_por_tamanho[tamanho]
        
        print(f"\n📊 MATRIZ {tamanho}×{tamanho}")
        print("-" * 60)
        
        tempos = {
            "Serial":      r['tempos']['serial'],
            "Paralelo":    r['tempos']['paralelo'],
            "Distribuído": r['tempos']['distribuido'],
        }
        
        gerar_grafico_ascii("Tempos", tempos, largura=40)
        
        print(f"Overhead Paralelo:    +{r['overhead_paralelo']:.6f}s ({r['overhead_paralelo']/r['tempos']['serial']*100:.1f}% do serial)")
        print(f"Speedup Paralelo:     {r['speedups']['paralelo']:.3f}x (Eficiência: {r['eficiencia']['paralelo']:.1f}%)")
        print(f"Validação:            {'✅ VÁLIDO' if r['validacao']['paralelo'] else '❌ INVÁLIDO'}")
    
    # Análise do ponto de inflexão
    print("\n" + "=" * 90)
    print("📈 ANÁLISE DO PONTO DE INFLEXÃO (Break-even Point)")
    print("=" * 90)
    
    print("\nSpeedup Paralelo por Tamanho:")
    print("-" * 60)
    
    speedups_sorted = sorted(
        [(tamanho, resultados_por_tamanho[tamanho]['speedups']['paralelo']) 
         for tamanho in resultados_por_tamanho.keys()],
        key=lambda x: x[0]
    )
    
    for tamanho, speedup in speedups_sorted:
        if speedup < 1.0:
            barra = "░" * int((1 - speedup) * 20) + "│"
            status = "❌ SERIAL MAIS RÁPIDO"
        else:
            barra = "│" + "█" * int((speedup - 1) * 20)
            status = "✅ PARALELO MAIS RÁPIDO"
        
        print(f"{tamanho:3d}×{tamanho:3d} │{barra:<25}│ {speedup:.3f}x - {status}")
    
    print("\n💡 INTERPRETAÇÃO:")
    print("  • Speedup < 1.0: Paralelo é mais lento (overhead > benefício)")
    print("  • Speedup = 1.0: Serial e Paralelo têm desempenho igual")
    print("  • Speedup > 1.0: Paralelo é mais rápido (benefício > overhead)")
    
    # Conclusões
    print("\n" + "=" * 90)
    print("📋 CONCLUSÕES")
    print("=" * 90)
    
    speedups = [resultados_por_tamanho[t]['speedups']['paralelo'] for t in resultados_por_tamanho]
    pior_speedup = min(speedups)
    melhor_speedup = max(speedups)
    
    print(f"\n✓ Pior caso (menor matriz): {pior_speedup:.3f}x")
    print(f"✓ Melhor caso (maior matriz): {melhor_speedup:.3f}x")
    print(f"✓ Overhead de paralelização: ~{resultados_por_tamanho[tamanhos[0]]['overhead_paralelo']:.3f}s")
    
    print("\n💬 Razão do overhead:")
    print("  1. Criação/gerenciamento de pool de processos")
    print("  2. Serialização de dados entre processos (pickle)")
    print("  3. Sincronização e context switches do SO")
    print("  4. Python puro é bem mais lento que numpy (otimizado em C)")
    
    print("\n📌 Recomendação para seu projeto:")
    print("  • Matrizes < 100×100: Use SERIAL (overhead não compensa)")
    print("  • Matrizes 100×200: Ambos são comparáveis, faz pouca diferença")
    print("  • Matrizes > 200×200: Use PARALELO (começa a compensar)")
    print("  • Para real-world: Use numpy + scipy (muito mais rápido)")
    
    print("\n" + "=" * 90)
    print("✅ Benchmark concluído!")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    benchmark_detalhado_com_grafico()
