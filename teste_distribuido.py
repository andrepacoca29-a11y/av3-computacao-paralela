"""
TESTE DE COMUNICAÇÃO DISTRIBUÍDA
Valida se o cliente consegue conectar ao servidor
"""

import sys
import socket
import numpy as np
from socket_client import ClienteSocket

def teste_ping(host: str, port: int = 5001) -> bool:
    """Testa se consegue conectar ao servidor"""
    print(f"\n{'='*60}")
    print(f"🔍 TESTE 1: Conectando em {host}:{port}...")
    print(f"{'='*60}")
    
    try:
        # Tenta conectar
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        sock.close()
        
        print(f"✅ Conexão bem-sucedida!")
        print(f"   → Servidor está RODANDO em {host}:{port}")
        return True
        
    except ConnectionRefusedError:
        print(f"❌ Conexão RECUSADA")
        print(f"   → Servidor NÃO está rodando")
        print(f"   → Execute no outro PC: python socket_server.py --host 0.0.0.0 --port 5001")
        return False
        
    except socket.timeout:
        print(f"❌ TIMEOUT - Servidor não respondeu")
        print(f"   → Verifique firewall/rede")
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def teste_envio_bloco(host: str, port: int = 5001) -> bool:
    """Testa envio de bloco de matriz"""
    print(f"\n{'='*60}")
    print(f"🔍 TESTE 2: Enviando bloco de matriz...")
    print(f"{'='*60}")
    
    try:
        # Cria cliente
        cliente = ClienteSocket(host, port, timeout=10)
        
        # Conecta
        if not cliente.conectar():
            print(f"❌ Falhou ao conectar")
            return False
        
        # Cria matrizes pequenas de teste
        bloco_a = np.array([[1, 2, 3], [4, 5, 6]])  # 2×3
        matriz_b = np.array([[1, 2], [3, 4], [5, 6]])  # 3×2
        
        print(f"\n📤 Enviando:")
        print(f"   Bloco A: {bloco_a.shape}")
        print(f"   Matriz B: {matriz_b.shape}")
        
        # Testa multiplicação
        resultado = cliente.multiplicar_bloco(bloco_a, matriz_b, inicio_linha=0)
        
        if resultado and resultado.get('status') == 'sucesso':
            print(f"\n✅ Resposta recebida!")
            print(f"   → Resultado: {resultado.get('resultado')}")
            cliente.fechar()
            return True
        else:
            print(f"❌ Resposta inválida: {resultado}")
            cliente.fechar()
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def teste_benchmark_distribuido() -> bool:
    """Testa benchmark distribuído via socket"""
    print(f"\n{'='*60}")
    print(f"🔍 TESTE 3: Benchmark distribuído completo...")
    print(f"{'='*60}")
    
    try:
        from matrix_operations import criar_matriz, multiplicar_serial
        import time
        
        # Pergunta IP
        host = input("\n📍 IP do Servidor Remoto (ex: 172.19.9.88): ").strip()
        if not host:
            print("❌ IP vazio")
            return False
        
        port = 5001
        
        print(f"\n🔄 Conectando em {host}:{port}...")
        cliente = ClienteSocket(host, port, timeout=30)
        
        if not cliente.conectar():
            return False
        
        # Testa com matrizes maiores
        print(f"\n📊 Criando matrizes...")
        m, n, p = 50, 50, 50
        A = criar_matriz(m, n, "aleatoria")
        B = criar_matriz(n, p, "aleatoria")
        
        print(f"   A: {m}×{n}")
        print(f"   B: {n}×{p}")
        print(f"   Esperado: C será {m}×{p}")
        
        # Calcula serial localmente
        print(f"\n⏱️  Calculando serial (referência)...")
        t0 = time.perf_counter()
        C_serial = multiplicar_serial(A, B)
        t_serial = time.perf_counter() - t0
        print(f"   ✓ Serial: {t_serial:.4f}s")
        
        # Envia para servidor
        print(f"\n📤 Enviando para distribuído...")
        A_np = np.array(A)
        B_np = np.array(B)
        
        t1 = time.perf_counter()
        resultado = cliente.multiplicar_bloco(A_np, B_np, inicio_linha=0)
        t_distribuido = time.perf_counter() - t1
        
        if resultado and resultado.get('status') == 'sucesso':
            C_distribuido = np.array(resultado.get('resultado'))
            
            print(f"   ✓ Distribuído: {t_distribuido:.4f}s")
            
            # Valida
            print(f"\n✅ Validando resultado...")
            if np.allclose(C_serial, C_distribuido, atol=1e-5):
                print(f"   ✓ Resultado CORRETO!")
                speedup = t_serial / t_distribuido
                print(f"\n📈 Métricas:")
                print(f"   Serial:      {t_serial:.4f}s")
                print(f"   Distribuído: {t_distribuido:.4f}s")
                print(f"   Speedup:     {speedup:.2f}×")
                cliente.fechar()
                return True
            else:
                print(f"   ❌ Resultado INCORRETO!")
                print(f"   Diferença máxima: {np.max(np.abs(np.array(C_serial) - C_distribuido))}")
                cliente.fechar()
                return False
        else:
            print(f"❌ Erro ao processar no servidor")
            cliente.fechar()
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*60)
    print("🧪 TESTE DE COMUNICAÇÃO DISTRIBUÍDA")
    print("="*60)
    
    # Pergunta IP
    host = input("\n📍 IP do Servidor Remoto: ").strip()
    if not host:
        print("❌ IP vazio")
        return
    
    print(f"\n🎯 Testando conexão com {host}:5001...")
    
    # Teste 1: Ping
    if not teste_ping(host):
        print("\n" + "="*60)
        print("❌ TESTE 1 FALHOU - Servidor não está acessível")
        print("="*60)
        print("\n🔧 SOLUÇÃO:")
        print("1. Execute no outro PC: python socket_server.py --host 0.0.0.0 --port 5001")
        print("2. Verifique se firewall permite porta 5001")
        print("3. Teste ping: ping " + host)
        return
    
    # Teste 2: Envio de bloco
    if teste_envio_bloco(host):
        print("\n" + "="*60)
        print("✅ TESTE 2 PASSOU - Comunicação funcionando!")
        print("="*60)
        
        # Teste 3: Benchmark
        print("\nDeseja executar benchmark distribuído? (S/N)")
        resp = input("> ").strip().upper()
        if resp == 'S':
            teste_benchmark_distribuido()
    else:
        print("\n" + "="*60)
        print("❌ TESTE 2 FALHOU - Erro na comunicação")
        print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Teste cancelado")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
