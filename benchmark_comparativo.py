"""
Benchmark comparativo: Serial vs Paralelo com Python puro
Mostra quando a paralelização compensa o overhead
"""

import time
from matrix_operations import (
    criar_matriz,
    executar_benchmark,
)


def teste_crescente():
    """Testa múltiplos tamanhos de matriz para ver o ponto de inflexão"""
    print("=" * 80)
    print("BENCHMARK COMPARATIVO: Serial × Paralelo × Distribuído")
    print("=" * 80)
    print()
    print(f"{'Tamanho':<12} {'Serial (s)':<15} {'Paralelo (s)':<15} {'Distribuído (s)':<15} {'Speedup':<10}")
    print("-" * 80)
    
    tamanhos = [10, 20, 30, 50, 75, 100, 150, 200, 250, 300]
    
    for tamanho in tamanhos:
        try:
            resultado = executar_benchmark(
                m=tamanho,
                n=tamanho,
                p=tamanho,
                num_processos=2,
                num_nodos=2,
                tipo_matriz="aleatoria"
            )
            
            t_serial = resultado['tempos']['serial']
            t_paralelo = resultado['tempos']['paralelo']
            t_distribuido = resultado['tempos']['distribuido']
            speedup = resultado['speedups']['paralelo']
            
            # Validação
            val_paralelo = "✓" if resultado['validacao']['paralelo'] else "✗"
            val_distribuido = "✓" if resultado['validacao']['distribuido'] else "✗"
            
            print(f"{tamanho}×{tamanho}     {t_serial:<14.6f} {t_paralelo:<14.6f} {t_distribuido:<14.6f} {speedup:<9.3f} {val_paralelo} {val_distribuido}")
            
        except Exception as e:
            print(f"{tamanho}×{tamanho}     ERRO: {str(e)[:50]}")
    
    print()
    print("Observações:")
    print("- Speedup > 1.0 = paralelo é mais rápido")
    print("- Speedup < 1.0 = serial é mais rápido (overhead > benefício)")
    print("- ✓ = resultado validado | ✗ = resultado incorreto")
    print()


def analise_detalhada():
    """Análise detalhada de um tamanho intermediário"""
    print("=" * 80)
    print("ANÁLISE DETALHADA: Matriz 200×200")
    print("=" * 80)
    print()
    
    resultado = executar_benchmark(
        m=200,
        n=200,
        p=200,
        num_processos=2,
        num_nodos=2,
        tipo_matriz="aleatoria"
    )
    
    print(f"Dimensões: A={resultado['dimensoes']['A']}, B={resultado['dimensoes']['B']}, C={resultado['dimensoes']['C']}")
    print()
    print("TEMPOS:")
    print(f"  Serial:      {resultado['tempos']['serial']:.6f}s")
    print(f"  Paralelo:    {resultado['tempos']['paralelo']:.6f}s")
    print(f"  Distribuído: {resultado['tempos']['distribuido']:.6f}s")
    print()
    print("SPEEDUPS:")
    print(f"  Paralelo:    {resultado['speedups']['paralelo']:.3f}x ({resultado['eficiencia']['paralelo']:.1f}% eficiência)")
    print(f"  Distribuído: {resultado['speedups']['distribuido']:.3f}x ({resultado['eficiencia']['distribuido']:.1f}% eficiência)")
    print()
    print("OVERHEAD (tempo extra gasto):")
    print(f"  Paralelo:    +{resultado['overhead_paralelo']:.6f}s")
    print(f"  Distribuído: +{resultado['overhead_distribuido']:.6f}s")
    print()
    print("VALIDAÇÃO:")
    print(f"  Paralelo:    {'✓ VÁLIDO' if resultado['validacao']['paralelo'] else '✗ INVÁLIDO'}")
    print(f"  Distribuído: {'✓ VÁLIDO' if resultado['validacao']['distribuido'] else '✗ INVÁLIDO'}")
    print()


if __name__ == "__main__":
    print("\n🔬 INICIANDO BENCHMARKS...\n")
    
    # Teste crescente
    teste_crescente()
    
    print("\n" + "=" * 80)
    print()
    
    # Análise detalhada
    analise_detalhada()
    
    print("=" * 80)
    print("✅ Benchmarks concluídos!")
    print("=" * 80)
