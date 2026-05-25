#!/usr/bin/env python3
"""
TESTE RÁPIDO DE CONEXÃO SOCKET
Valida protocolo de framing (tamanho + dados)

USO LOCAL (SIMULAÇÃO EM TERMINAIS DO MESMO PC):
    Terminal 1: python socket_server.py --port 5001
    Terminal 2: python teste_conexao_rapido.py

USO EM REDE (PCs DIFERENTES):
    Terminal 1 (172.19.9.43): python socket_server.py --host 0.0.0.0 --port 5001
    Terminal 2 (seu PC):      python teste_conexao_rapido.py --host 172.19.9.43
"""

import sys
import time
import argparse
from socket_client import ClienteSocket

# Padrões
HOST_PADRAO = '127.0.0.1'  # localhost (simula em terminais locais)
PORTA_PADRAO = 5001

def teste_conexao_basica(host, porta):
    """Testa conexão básica"""
    print("\n" + "="*60)
    print("🧪 TESTE 1: Conexão Básica")
    print("="*60)
    
    cliente = ClienteSocket(host, porta, timeout=30)
    
    print("📡 Tentando conectar a {}:{}...".format(host, porta))
    if not cliente.conectar():
        print("❌ FALHOU: Não conseguiu conectar")
        return False
    
    print("✅ Conectado com sucesso!")
    cliente.fechar()
    return True


def teste_ping(host, porta):
    """Testa operação 'teste' do servidor"""
    print("\n" + "="*60)
    print("🧪 TESTE 2: Ping (operação 'teste')")
    print("="*60)
    
    cliente = ClienteSocket(host, porta, timeout=30)
    
    print("📡 Conectando...")
    if not cliente.conectar():
        print("❌ Não conseguiu conectar")
        return False
    
    print("🔔 Enviando ping...")
    if not cliente.testar_conexao():
        print("❌ FALHOU: Servidor não respondeu")
        cliente.fechar()
        return False
    
    print("✅ Ping respondido!")
    cliente.fechar()
    return True


def teste_bloco_pequeno(host, porta):
    """Testa multiplicação de bloco pequeno (2×3 × 3×2)"""
    print("\n" + "="*60)
    print("🧪 TESTE 3: Multiplicação de Bloco Pequeno (2×3 × 3×2)")
    print("="*60)
    
    cliente = ClienteSocket(host, porta, timeout=30)
    
    print("📡 Conectando...")
    if not cliente.conectar():
        print("❌ Não conseguiu conectar")
        return False
    
    # Matrizes pequenas
    A = [[1, 2, 3], [4, 5, 6]]          # 2×3
    B = [[7, 8], [9, 10], [11, 12]]     # 3×2
    
    print(f"📊 Matriz A (2×3):\n{A}")
    print(f"📊 Matriz B (3×2):\n{B}")
    
    print("📤 Enviando para multiplicação remota...")
    try:
        resultado = cliente.multiplicar_bloco_puro(A, B, inicio_linha=0)
        
        if resultado and resultado.get('status') == 'sucesso':
            C = resultado.get('resultado')
            print(f"\n✅ Resultado (2×2):\n{C}")
            
            # Valida resultado manualmente
            # 1*7 + 2*9 + 3*11 = 7 + 18 + 33 = 58
            # 1*8 + 2*10 + 3*12 = 8 + 20 + 36 = 64
            # 4*7 + 5*9 + 6*11 = 28 + 45 + 66 = 139
            # 4*8 + 5*10 + 6*12 = 32 + 50 + 72 = 154
            
            esperado = [[58, 64], [139, 154]]
            if C == esperado:
                print(f"✅ Resultado correto!")
                cliente.fechar()
                return True
            else:
                print(f"❌ Resultado errado. Esperado: {esperado}")
                cliente.fechar()
                return False
        else:
            print(f"❌ Erro no servidor: {resultado}")
            cliente.fechar()
            return False
    except Exception as e:
        print(f"❌ Exceção: {e}")
        cliente.fechar()
        return False


def teste_bloco_medio(host, porta):
    """Testa multiplicação de bloco médio (10×10 × 10×10)"""
    print("\n" + "="*60)
    print("🧪 TESTE 4: Multiplicação de Bloco Médio (10×10 × 10×10)")
    print("="*60)
    
    cliente = ClienteSocket(host, porta, timeout=30)
    
    print("📡 Conectando...")
    if not cliente.conectar():
        print("❌ Não conseguiu conectar")
        return False
    
    # Matrizes médias
    A = [[i+j for j in range(10)] for i in range(10)]     # 10×10
    B = [[i+j for j in range(10)] for i in range(10)]     # 10×10
    
    print(f"📊 Matriz A (10×10): primeiros 3×3 = {A[:3]}")
    print(f"📊 Matriz B (10×10): primeiros 3×3 = {B[:3]}")
    
    print("📤 Enviando para multiplicação remota...")
    try:
        resultado = cliente.multiplicar_bloco_puro(A, B, inicio_linha=0)
        
        if resultado and resultado.get('status') == 'sucesso':
            C = resultado.get('resultado')
            print(f"✅ Resultado recebido (10×10)")
            print(f"   Primeiros 3×3: {[row[:3] for row in C[:3]]}")
            cliente.fechar()
            return True
        else:
            print(f"❌ Erro no servidor: {resultado}")
            cliente.fechar()
            return False
    except Exception as e:
        print(f"❌ Exceção: {e}")
        cliente.fechar()
        return False


if __name__ == '__main__':
    # Parsear argumentos
    parser = argparse.ArgumentParser(
        description='Teste de conexão socket para distribuição de matrizes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLOS:
  # Teste local (servidor em localhost:5001)
  python teste_conexao_rapido.py
  
  # Teste local em porta diferente
  python teste_conexao_rapido.py --port 5002
  
  # Teste em rede real (servidor em 172.19.9.43:5001)
  python teste_conexao_rapido.py --host 172.19.9.43
  
  # Teste em rede real com porta customizada
  python teste_conexao_rapido.py --host 192.168.1.100 --port 5002
        """
    )
    
    parser.add_argument('--host', '-H', 
                       default=HOST_PADRAO,
                       help='IP/hostname do servidor (padrão: {})'.format(HOST_PADRAO))
    parser.add_argument('--port', '-P', 
                       type=int,
                       default=PORTA_PADRAO,
                       help='Porta TCP do servidor (padrão: {})'.format(PORTA_PADRAO))
    
    args = parser.parse_args()
    host = args.host
    porta = args.port
    
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█  TESTE DE CONEXÃO SOCKET COM NOVO PROTOCOLO DE FRAMING" + " "*4 + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    print("\nServidor: {}:{}\n".format(host, porta))
    
    resultados = []
    
    # Testes em sequência
    resultados.append(("Conexão Básica", teste_conexao_basica(host, porta)))
    time.sleep(1)
    
    resultados.append(("Ping/Teste", teste_ping(host, porta)))
    time.sleep(1)
    
    resultados.append(("Bloco Pequeno (2×3 × 3×2)", teste_bloco_pequeno(host, porta)))
    time.sleep(1)
    
    resultados.append(("Bloco Médio (10×10 × 10×10)", teste_bloco_medio(host, porta)))
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{status}: {nome}")
    
    total_passos = len(resultados)
    passos_ok = sum(1 for _, r in resultados if r)
    
    print(f"\nResultado: {passos_ok}/{total_passos} testes passaram")
    
    if passos_ok == total_passos:
        print("\n🎉 TODOS OS TESTES PASSARAM! Distribuição pronta!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total_passos - passos_ok} teste(s) falharam")
        sys.exit(1)
