"""
EXEMPLO DE USO: MULTIPLICAÇÃO COM SOCKETS

Este script mostra como usar sockets reais para distribuição
"""

import time
import sys
import subprocess
import signal
from typing import List, Tuple
import numpy as np

from matrix_operations import (
    criar_matriz, 
    multiplicar_serial,
    multiplicar_paralelo,
    multiplicar_distribuido,
    multiplicar_distribuido_socket,
    matrizes_iguais
)


def imprimir_titulo(titulo: str):
    """Imprime título formatado"""
    print("\n" + "="*70)
    print(f"  {titulo}")
    print("="*70)


def teste_local_socket():
    """
    Teste 1: Distribuição via socket em localhost
    Usa múltiplas portas na mesma máquina
    """
    
    imprimir_titulo("TESTE 1: Distribuição Local via Socket")
    print("\nPre-requisito: Inicie os servidores em terminais diferentes:")
    print("  Terminal 1: python socket_server.py --port 5001")
    print("  Terminal 2: python socket_server.py --port 5002")
    print()
    
    input("Pressione ENTER depois que os servidores estiverem prontos...")
    
    # Criar matrizes
    print("\n📊 Criando matrizes de teste (100×100)...")
    A = criar_matriz(100, 100, tipo='aleatoria', seed=1)
    B = criar_matriz(100, 100, tipo='aleatoria', seed=2)
    
    # Calcular baseline serial
    print("⏱️  Executando SERIAL...")
    t0 = time.perf_counter()
    C_serial = multiplicar_serial(A, B)
    t_serial = time.perf_counter() - t0
    print(f"   Serial: {t_serial*1000:.2f}ms")
    
    # Configurar servidores locais
    servidores = [
        ('localhost', 5001),
        ('localhost', 5002)
    ]
    
    print(f"\n🔌 Multiplicando via SOCKET com {len(servidores)} servidores...")
    t1 = time.perf_counter()
    try:
        C_socket = multiplicar_distribuido_socket(A, B, servidores)
        t_socket = time.perf_counter() - t1
        
        if C_socket:
            print(f"   Socket: {t_socket*1000:.2f}ms")
            
            # Validar resultado
            if matrizes_iguais(C_serial, C_socket):
                print("   ✅ Resultado correto!")
                speedup = t_serial / t_socket if t_socket > 0 else 0
                print(f"   📈 Speedup: {speedup:.2f}×")
            else:
                print("   ❌ Resultado incorreto!")
        else:
            print("   ❌ Erro ao calcular via socket")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")


def teste_paralelo_vs_socket():
    """
    Teste 2: Comparar Paralelo vs Socket
    """
    
    imprimir_titulo("TESTE 2: Paralelismo Local vs Socket")
    print("\nPre-requisito: Inicie os servidores:")
    print("  Terminal 1: python socket_server.py --port 5001")
    print("  Terminal 2: python socket_server.py --port 5002")
    print()
    
    input("Pressione ENTER depois que os servidores estiverem prontos...")
    
    # Criar matrizes de teste
    print("\n📊 Criando matrizes de teste (200×200)...")
    A = criar_matriz(200, 200, tipo='aleatoria', seed=1)
    B = criar_matriz(200, 200, tipo='aleatoria', seed=2)
    
    resultados = {}
    
    # Serial
    print("\n⏱️  Teste 1: SERIAL...")
    t0 = time.perf_counter()
    C_serial = multiplicar_serial(A, B)
    resultados['serial'] = time.perf_counter() - t0
    print(f"   Tempo: {resultados['serial']*1000:.2f}ms")
    
    # Paralelo (4 processos)
    print("\n⏱️  Teste 2: PARALELO (4 núcleos)...")
    t1 = time.perf_counter()
    C_paralelo = multiplicar_paralelo(A, B, num_processos=4)
    resultados['paralelo'] = time.perf_counter() - t1
    print(f"   Tempo: {resultados['paralelo']*1000:.2f}ms")
    print(f"   Speedup: {resultados['serial']/resultados['paralelo']:.2f}×")
    
    # Socket (2 servidores)
    print("\n⏱️  Teste 3: SOCKET (2 servidores)...")
    servidores = [
        ('localhost', 5001),
        ('localhost', 5002)
    ]
    
    try:
        t2 = time.perf_counter()
        C_socket = multiplicar_distribuido_socket(A, B, servidores)
        resultados['socket'] = time.perf_counter() - t2
        print(f"   Tempo: {resultados['socket']*1000:.2f}ms")
        
        if C_socket:
            speedup_socket = resultados['serial'] / resultados['socket']
            print(f"   Speedup: {speedup_socket:.2f}×")
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Resumo
    print("\n" + "="*70)
    print("  RESUMO COMPARATIVO")
    print("="*70)
    
    print("\nTempos (ms):")
    for metodo, tempo in resultados.items():
        print(f"  {metodo:12s}: {tempo*1000:8.2f}ms")
    
    if 'paralelo' in resultados and 'socket' in resultados:
        print(f"\n🆚 Socket vs Paralelo:")
        razao = resultados['socket'] / resultados['paralelo']
        if razao < 1:
            print(f"   Socket é {1/razao:.2f}× MAIS RÁPIDO")
        else:
            print(f"   Paralelo é {razao:.2f}× MAIS RÁPIDO")
        print(f"   (Esperado: Paralelo > Socket devido à latência de rede)")


def teste_escalabilidade_socket():
    """
    Teste 3: Escalabilidade com diferentes números de servidores
    """
    
    imprimir_titulo("TESTE 3: Escalabilidade com Múltiplos Servidores")
    print("\nPre-requisito: Inicie os servidores:")
    print("  Terminal 1: python socket_server.py --port 5001")
    print("  Terminal 2: python socket_server.py --port 5002")
    print("  Terminal 3: python socket_server.py --port 5003")
    print("  Terminal 4: python socket_server.py --port 5004")
    print()
    
    input("Pressione ENTER depois que os servidores estiverem prontos...")
    
    # Criar matriz de teste
    print("\n📊 Criando matriz de teste (300×300)...")
    A = criar_matriz(300, 300, tipo='aleatoria', seed=1)
    B = criar_matriz(300, 300, tipo='aleatoria', seed=2)
    
    # Baseline serial
    print("\n⏱️  Calculando baseline SERIAL...")
    t0 = time.perf_counter()
    C_serial = multiplicar_serial(A, B)
    t_serial = time.perf_counter() - t0
    print(f"   Tempo: {t_serial*1000:.2f}ms")
    
    # Testar com diferentes números de servidores
    configuracoes = [
        (1, [('localhost', 5001)]),
        (2, [('localhost', 5001), ('localhost', 5002)]),
        (3, [('localhost', 5001), ('localhost', 5002), ('localhost', 5003)]),
        (4, [('localhost', 5001), ('localhost', 5002), ('localhost', 5003), ('localhost', 5004)])
    ]
    
    print("\n" + "="*70)
    print("  ESCALABILIDADE")
    print("="*70)
    print(f"\n{'Servidores':<15} {'Tempo (ms)':<15} {'Speedup':<15} {'Eficiência':<15}")
    print("-"*70)
    
    for num_serv, servidores in configuracoes:
        try:
            t1 = time.perf_counter()
            C_socket = multiplicar_distribuido_socket(A, B, servidores)
            t_socket = time.perf_counter() - t1
            
            if C_socket:
                speedup = t_serial / t_socket
                eficiencia = (speedup / num_serv) * 100
                print(f"{num_serv:<15} {t_socket*1000:<15.2f} {speedup:<15.2f}× {eficiencia:<15.1f}%")
            else:
                print(f"{num_serv:<15} {'ERRO':<15} {'-':<15} {'-':<15}")
                
        except Exception as e:
            print(f"{num_serv:<15} {'ERRO: ' + str(e)[:8]:<15} {'-':<15} {'-':<15}")


def guia_uso():
    """Mostra guia de uso completo"""
    
    imprimir_titulo("GUIA DE USO: SOCKETS REAIS")
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ARQUITETURA: Cliente-Servidor COM SOCKETS REAIS                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

PASSO 1: Inicie os Servidores (em terminais diferentes)
──────────────────────────────────────────────────────

Terminal 1:
  $ python socket_server.py --port 5001 --host 0.0.0.0
  
Terminal 2:
  $ python socket_server.py --port 5002 --host 0.0.0.0

Terminal 3 (opcional):
  $ python socket_server.py --port 5003 --host 0.0.0.0


PASSO 2: Execute Cálculos via Socket
──────────────────────────────────────

No seu código Python:

from matrix_operations import criar_matriz, multiplicar_distribuido_socket

# Criar matrizes
A = criar_matriz(100, 100, tipo='aleatoria')
B = criar_matriz(100, 100, tipo='aleatoria')

# Definir servidores (IP e porta)
servidores = [
    ('192.168.1.100', 5001),  # Servidor 1
    ('192.168.1.101', 5001)   # Servidor 2
]

# Para TESTE LOCAL (mesma máquina, portas diferentes):
servidores = [
    ('localhost', 5001),      # localhost, porta 5001
    ('localhost', 5002)       # localhost, porta 5002
]

# Multiplicar via socket
C = multiplicar_distribuido_socket(A, B, servidores)


PASSO 3: Ver Resultados
────────────────────────

if C:
    print(f"✅ Resultado calculado!")
    print(f"   Dimensão: {len(C)}×{len(C[0])}")
else:
    print(f"❌ Erro ao calcular")


╔══════════════════════════════════════════════════════════════════════════════╗
║  CONFIGURAÇÕES RECOMENDADAS                                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

TESTE LOCAL (sua máquina):
─────────────────────────
Terminal 1: python socket_server.py --port 5001
Terminal 2: python socket_server.py --port 5002
Código:     servidores = [('localhost', 5001), ('localhost', 5002)]


PRODUÇÃO (múltiplas máquinas):
──────────────────────────────
Máquina A: python socket_server.py --port 5001 --host 0.0.0.0
Máquina B: python socket_server.py --port 5001 --host 0.0.0.0
Código:    servidores = [('192.168.1.100', 5001), ('192.168.1.101', 5001)]

Nota: Use --host 0.0.0.0 para aceitar conexões de qualquer IP


╔══════════════════════════════════════════════════════════════════════════════╗
║  PROTOCOLO SOCKET (TCP/IP)                                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

CLIENTE → SERVIDOR:
  1. Conecta via TCP socket
  2. Envia JSON com bloco de A, matriz B, linha inicial
  3. Aguarda resposta

SERVIDOR → CLIENTE:
  1. Recebe conexão
  2. Processa JSON (multiplica bloco × B)
  3. Envia resultado em JSON
  4. Fecha conexão

Formato JSON (Cliente → Servidor):
{
  "operacao": "multiplicar_bloco",
  "bloco_a": [[...dados...]],
  "matriz_b": [[...dados...]],
  "inicio_linha": 0
}

Formato JSON (Servidor → Cliente):
{
  "status": "sucesso",
  "resultado": [[...dados...]],
  "forma": [100, 100],
  "inicio_linha": 0,
  "tempo_ms": 15.23
}


╔══════════════════════════════════════════════════════════════════════════════╗
║  DIFERENÇAS: PARALELO vs DISTRIBUÍDO                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

PARALELO (1 máquina, múltiplos núcleos):
  - Usa multiprocessing.Pool
  - Processos locais (compartilham memória)
  - Sem latência de rede
  - ✅ RÁPIDO para matrizes médias (100-500)

DISTRIBUÍDO via SOCKET (múltiplas máquinas):
  - Usa TCP sockets
  - Processos remotos (máquinas diferentes)
  - COM latência de rede
  - ✅ ESCALÁVEL para matrizes gigantes (1000+)
  - ✅ IDEAL para clusters ou computação em nuvem

Quando usar cada um:
  Paralelo:     Matrizes até 500×500, 1 máquina
  Distribuído:  Matrizes 500+, múltiplas máquinas
""")


def main():
    """Menu principal"""
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                 TESTES: SOCKET (Distribuição Real)                        ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    print("""
Opções:
  1 - Teste Básico: Distribuição Local via Socket
  2 - Comparação: Paralelo vs Socket
  3 - Escalabilidade: com 1, 2, 3, 4 servidores
  4 - Ver Guia de Uso
  0 - Sair

Obs: Antes de rodar testes 1, 2 ou 3, inicie os servidores em terminais:
     python socket_server.py --port 5001
     python socket_server.py --port 5002
     etc...
    """)
    
    while True:
        opcao = input("\nEscolha uma opção (0-4): ").strip()
        
        if opcao == '1':
            teste_local_socket()
        elif opcao == '2':
            teste_paralelo_vs_socket()
        elif opcao == '3':
            teste_escalabilidade_socket()
        elif opcao == '4':
            guia_uso()
        elif opcao == '0':
            print("\n👋 Saindo...")
            break
        else:
            print("❌ Opção inválida!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Interrompido pelo usuário")
        sys.exit(0)
