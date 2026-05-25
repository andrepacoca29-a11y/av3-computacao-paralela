"""
SERVIDOR SOCKET PARA DISTRIBUIÇÃO REAL (PYTHON PURO)

Recebe blocos de matriz + matriz completa via socket
Multiplica o bloco pela matriz usando Python Puro (sem Numpy)
Retorna resultado
"""

import socket
import json
import argparse
import time
import sys
from typing import Tuple, List

class ServidorSocket:
    """Servidor Socket para multiplicação distribuída de matrizes"""
    
    def __init__(self, host: str = 'localhost', port: int = 5001, max_conexoes: int = 5):
        self.host = host
        self.port = port
        self.max_conexoes = max_conexoes
        self.servidor = None
        self.operacoes_processadas = 0
        self.tempo_total = 0
        
    def iniciar(self) -> None:
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.servidor.bind((self.host, self.port))
            self.servidor.listen(self.max_conexoes)
            print(f"✅ Servidor Socket iniciado em {self.host}:{self.port}")
            print(f"   Aguardando ligações...")
            
            self._aceitar_conexoes()
            
        except Exception as e:
            print(f"❌ Erro ao iniciar servidor: {e}")
            sys.exit(1)
        finally:
            self.parar()
    
    def _aceitar_conexoes(self) -> None:
        try:
            while True:
                conexao, endereco = self.servidor.accept()
                print(f"\n📡 Cliente ligado de {endereco[0]}:{endereco[1]}")
                
                try:
                    self._processar_cliente(conexao, endereco)
                except Exception as e:
                    print(f"   ❌ Erro ao processar cliente: {e}")
                finally:
                    conexao.close()
                    print(f"   ✓ Ligação encerrada")
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Servidor interrompido pelo utilizador")
        except Exception as e:
            print(f"\n❌ Erro fatal: {e}")
    
    def _processar_cliente(self, conexao: socket.socket, endereco: Tuple) -> None:
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
            print(f"   ❌ Erro ao descodificar JSON: {e}")
            self._enviar_erro(conexao, "JSON inválido")
        except Exception as e:
            print(f"   ❌ Erro ao processar: {e}")
            self._enviar_erro(conexao, str(e))
    
    def _multiplicar_bloco(self, conexao: socket.socket, dados: dict, endereco: Tuple) -> None:
        """Multiplica bloco de A × B completa usando listas nativas do Python"""
        
        inicio_linha = dados.get('inicio_linha', 0)
        
        # Obter as listas puras sem numpy
        bloco_a = dados.get('bloco_a', [])
        matriz_b = dados.get('matriz_b', [])
        
        linhas_a = len(bloco_a)
        
        print(f"   📊 Multiplicando bloco:")
        print(f"      Linhas recebidas: {linhas_a}")
        print(f"      A iniciar cálculo em Python puro...")
        
        try:
            tempo_inicio = time.time()
            
            # Importar a sua função pura já construída
            from matrix_operations import multiplicar_serial
            
            # Cálculo intensivo em Python puro
            resultado = multiplicar_serial(bloco_a, matriz_b)
            
            tempo_decorrido = time.time() - tempo_inicio
            
            linhas_c = len(resultado)
            colunas_c = len(resultado[0]) if linhas_c > 0 else 0
            
            resposta = {
                'status': 'sucesso',
                'resultado': resultado,
                'forma': [linhas_c, colunas_c],
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
        resposta = {
            'status': 'sucesso',
            'mensagem': 'Servidor ligado e a funcionar',
            'operacoes': self.operacoes_processadas,
            'tempo_total_ms': self.tempo_total * 1000
        }
        self._enviar_json(conexao, resposta)
    
    def _receber_dados(self, conexao: socket.socket, tamanho: int = 10*1024*1024) -> str:
        """Recebe dados garantindo a leitura completa dos pacotes TCP fragmentados"""
        try:
            dados_completos = b''
            while True:
                chunk = conexao.recv(tamanho)
                if not chunk:
                    break
                
                dados_completos += chunk
                
                try:
                    texto_json = dados_completos.decode('utf-8')
                    json.loads(texto_json)
                    return texto_json
                except json.JSONDecodeError:
                    continue
            
            if not dados_completos:
                print("   ⚠️ Cliente desligou sem enviar dados")
                return None
                
        except Exception as e:
            print(f"   ❌ Erro ao receber dados: {e}")
            return None
    
    def _enviar_json(self, conexao: socket.socket, dados: dict) -> None:
        try:
            json_str = json.dumps(dados)
            conexao.sendall(json_str.encode('utf-8'))
        except Exception as e:
            print(f"   ❌ Erro ao enviar resposta: {e}")
    
    def _enviar_erro(self, conexao: socket.socket, mensagem: str) -> None:
        erro = {'status': 'erro', 'mensagem': mensagem}
        self._enviar_json(conexao, erro)
    
    def parar(self) -> None:
        if self.servidor:
            self.servidor.close()
            print("\n🛑 Servidor encerrado")


def main():
    parser = argparse.ArgumentParser(
        description='Servidor Socket para Multiplicação Distribuída de Matrizes'
    )
    parser.add_argument('--host', default='0.0.0.0', 
                       help='Host para escutar (padrão: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5001,
                       help='Porta TCP (padrão: 5001)')
    parser.add_argument('--max-conexoes', type=int, default=5,
                       help='Máximo de ligações simultâneas (padrão: 5)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔌 SERVIDOR SOCKET - Multiplicação de Matrizes Distribuída")
    print("=" * 60)
    print(f"Host: {args.host}")
    print(f"Porta: {args.port}")
    print(f"Máx ligações: {args.max_conexoes}")
    print("=" * 60)
    
    servidor = ServidorSocket(
        host=args.host,
        port=args.port,
        max_conexoes=args.max_conexoes
    )
    
    servidor.iniciar()

if __name__ == '__main__':
    main()