"""
SERVIDOR SOCKET PARA DISTRIBUIÇÃO REAL

Recebe blocos de matriz + matriz completa via socket
Multiplica o bloco pela matriz
Retorna resultado

Uso:
    python socket_server.py --port 5001 --host 0.0.0.0
    
Exemplo de cliente conectando:
    socket_client.connect('192.168.1.100', 5001)
    socket_client.enviar_bloco(A_bloco, B, inicio_linha)
"""

import socket
import json
import numpy as np
import argparse
import time
import sys
from typing import Tuple, List

class ServidorSocket:
    """Servidor Socket para multiplicação distribuída de matrizes"""
    
    def __init__(self, host: str = 'localhost', port: int = 5001, max_conexoes: int = 5):
        """
        Inicializa servidor socket
        
        Args:
            host: IP para escutar (0.0.0.0 para aceitar de qualquer IP)
            port: Porta TCP
            max_conexoes: Número máximo de conexões simultâneas
        """
        self.host = host
        self.port = port
        self.max_conexoes = max_conexoes
        self.servidor = None
        self.operacoes_processadas = 0
        self.tempo_total = 0
        
    def iniciar(self) -> None:
        """Inicia o servidor socket"""
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.servidor.bind((self.host, self.port))
            self.servidor.listen(self.max_conexoes)
            print(f"✅ Servidor Socket iniciado em {self.host}:{self.port}")
            print(f"   Aguardando conexões...")
            
            self._aceitar_conexoes()
            
        except Exception as e:
            print(f"❌ Erro ao iniciar servidor: {e}")
            sys.exit(1)
        finally:
            self.parar()
    
    def _aceitar_conexoes(self) -> None:
        """Loop principal: aceita e processa conexões"""
        try:
            while True:
                conexao, endereco = self.servidor.accept()
                print(f"\n📡 Cliente conectado de {endereco[0]}:{endereco[1]}")
                
                try:
                    self._processar_cliente(conexao, endereco)
                except Exception as e:
                    print(f"   ❌ Erro ao processar cliente: {e}")
                finally:
                    conexao.close()
                    print(f"   ✓ Conexão encerrada")
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Servidor interrompido pelo usuário")
        except Exception as e:
            print(f"\n❌ Erro fatal: {e}")
    
    def _processar_cliente(self, conexao: socket.socket, endereco: Tuple) -> None:
        """Processa requisição de um cliente"""
        
        # Receber dados do cliente (JSON)
        dados_json = self._receber_dados(conexao)
        if not dados_json:
            return
        
        try:
            dados = json.loads(dados_json)
            operacao = dados.get('operacao')
            
            if operacao == 'multiplicar_bloco':
                self._multiplicar_bloco(conexao, dados, endereco)
            elif operacao == 'teste':
                self._responder_teste(conexao)
            else:
                self._enviar_erro(conexao, f"Operação desconhecida: {operacao}")
                
        except json.JSONDecodeError as e:
            print(f"   ❌ Erro ao decodificar JSON: {e}")
            self._enviar_erro(conexao, "JSON inválido")
        except Exception as e:
            print(f"   ❌ Erro ao processar: {e}")
            self._enviar_erro(conexao, str(e))
    
    def _multiplicar_bloco(self, conexao: socket.socket, dados: dict, endereco: Tuple) -> None:
        """Multiplica bloco de A × B completa"""
        
        inicio_linha = dados.get('inicio_linha', 0)
        bloco_a = np.array(dados.get('bloco_a', []))
        matriz_b = np.array(dados.get('matriz_b', []))
        
        print(f"   📊 Multiplicando bloco:")
        print(f"      Bloco A: {bloco_a.shape}")
        print(f"      Matriz B: {matriz_b.shape}")
        print(f"      Linhas: {inicio_linha}-{inicio_linha + bloco_a.shape[0]}")
        
        try:
            tempo_inicio = time.time()
            
            # Multiplicar bloco × B
            resultado = np.dot(bloco_a, matriz_b)
            
            tempo_decorrido = time.time() - tempo_inicio
            
            # Enviar resposta
            resposta = {
                'status': 'sucesso',
                'resultado': resultado.tolist(),
                'forma': resultado.shape,
                'inicio_linha': inicio_linha,
                'tempo_ms': tempo_decorrido * 1000
            }
            
            self.operacoes_processadas += 1
            self.tempo_total += tempo_decorrido
            
            print(f"   ✅ Cálculo concluído em {tempo_decorrido*1000:.2f}ms")
            
            self._enviar_json(conexao, resposta)
            
        except Exception as e:
            print(f"   ❌ Erro no cálculo: {e}")
            self._enviar_erro(conexao, str(e))
    
    def _responder_teste(self, conexao: socket.socket) -> None:
        """Responde para teste de conexão"""
        resposta = {
            'status': 'sucesso',
            'mensagem': 'Servidor conectado e funcionando',
            'operacoes': self.operacoes_processadas,
            'tempo_total_ms': self.tempo_total * 1000
        }
        self._enviar_json(conexao, resposta)
    
    def _receber_dados(self, conexao: socket.socket, tamanho: int = 65536) -> str:
        """Recebe dados JSON do cliente"""
        try:
            dados = conexao.recv(tamanho).decode('utf-8')
            if not dados:
                print("   ⚠️ Cliente desconectou sem enviar dados")
                return None
            return dados
        except Exception as e:
            print(f"   ❌ Erro ao receber dados: {e}")
            return None
    
    def _enviar_json(self, conexao: socket.socket, dados: dict) -> None:
        """Envia resposta JSON para cliente"""
        try:
            json_str = json.dumps(dados)
            conexao.sendall(json_str.encode('utf-8'))
        except Exception as e:
            print(f"   ❌ Erro ao enviar resposta: {e}")
    
    def _enviar_erro(self, conexao: socket.socket, mensagem: str) -> None:
        """Envia mensagem de erro para cliente"""
        erro = {'status': 'erro', 'mensagem': mensagem}
        self._enviar_json(conexao, erro)
    
    def parar(self) -> None:
        """Para o servidor"""
        if self.servidor:
            self.servidor.close()
            print("\n🛑 Servidor encerrado")


def main():
    """Função principal - inicializa servidor"""
    
    parser = argparse.ArgumentParser(
        description='Servidor Socket para Multiplicação Distribuída de Matrizes'
    )
    parser.add_argument('--host', default='0.0.0.0', 
                       help='Host para escutar (padrão: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5001,
                       help='Porta TCP (padrão: 5001)')
    parser.add_argument('--max-conexoes', type=int, default=5,
                       help='Máximo de conexões simultâneas (padrão: 5)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔌 SERVIDOR SOCKET - Multiplicação de Matrizes Distribuída")
    print("=" * 60)
    print(f"Host: {args.host}")
    print(f"Porta: {args.port}")
    print(f"Máx conexões: {args.max_conexoes}")
    print("=" * 60)
    
    servidor = ServidorSocket(
        host=args.host,
        port=args.port,
        max_conexoes=args.max_conexoes
    )
    
    servidor.iniciar()


if __name__ == '__main__':
    main()
