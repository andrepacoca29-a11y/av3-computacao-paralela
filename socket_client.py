"""
CLIENTE SOCKET PARA DISTRIBUIÇÃO REAL

Conecta aos servidores remotos e envia blocos de matrizes

Uso:
    from socket_client import ClienteSocket
    
    cliente = ClienteSocket('172.19.9.43', 5001)  # IP DO SERVIDOR
    resultado = cliente.multiplicar_bloco(bloco_a, matriz_b, inicio_linha)
    cliente.fechar()
"""

import socket
import json
import numpy as np
import time
from typing import Tuple, Optional, List, Dict, Any


class ClienteSocket:
    """Cliente Socket para enviar blocos de matrizes a servidores remotos"""
    
    def __init__(self, host: str, port: int, timeout: int = 30):
        """
        Inicializa cliente socket
        
        Args:
            host: IP do servidor remoto
            port: Porta TCP do servidor
            timeout: Timeout em segundos
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.conectado = False
        
    def conectar(self) -> bool:
        """
        Conecta ao servidor remoto
        
        Returns:
            True se conectado com sucesso, False caso contrário
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            self.conectado = True
            print(f"✅ Conectado a {self.host}:{self.port}")
            return True
            
        except socket.timeout:
            print(f"❌ Timeout ao conectar em {self.host}:{self.port}")
            self.conectado = False
            return False
        except ConnectionRefusedError:
            print(f"❌ Conexão recusada por {self.host}:{self.port}")
            print(f"   Verifique se o servidor está rodando")
            self.conectado = False
            return False
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            self.conectado = False
            return False
    
    def testar_conexao(self) -> bool:
        """
        Testa se a conexão está funcionando
        
        Returns:
            True se servidor está respondendo
        """
        if not self.conectado:
            return False
        
        try:
            resposta = self._enviar_comando({
                'operacao': 'teste'
            })
            
            if resposta.get('status') == 'sucesso':
                print(f"✅ Servidor respondeu: {resposta.get('mensagem')}")
                return True
            else:
                print(f"❌ Resposta inválida: {resposta}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao testar conexão: {e}")
            return False
    
    def multiplicar_bloco(self, 
                         bloco_a: np.ndarray, 
                         matriz_b: np.ndarray, 
                         inicio_linha: int = 0) -> Optional[Dict[str, Any]]:
        """
        Envia bloco da matriz A e matriz B completa para multiplicar remotamente
        
        Args:
            bloco_a: Bloco de linhas da matriz A (forma: linhas × colunas)
            matriz_b: Matriz B completa
            inicio_linha: Número da primeira linha do bloco em A original
            
        Returns:
            Dict com resultado, ou None se erro
            
        Exemplo:
            bloco_a = A[0:25]  # Primeiras 25 linhas
            resultado = cliente.multiplicar_bloco(bloco_a, B, 0)
        """
        
        if not self.conectado:
            print("❌ Não conectado ao servidor")
            return None
        
        try:
            # Preparar comando
            comando = {
                'operacao': 'multiplicar_bloco',
                'bloco_a': bloco_a.tolist(),
                'matriz_b': matriz_b.tolist(),
                'inicio_linha': inicio_linha
            }
            
            # Enviar e receber resposta
            resposta = self._enviar_comando(comando)
            
            if resposta.get('status') == 'sucesso':
                return resposta
            else:
                print(f"❌ Erro no servidor: {resposta.get('mensagem')}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao multiplicar bloco: {e}")
            self.conectado = False
            return None
    
    def _enviar_comando(self, comando: dict) -> Optional[dict]:
        """
        Envia comando JSON e recebe resposta
        Suporta dados de até 10MB
        
        Args:
            comando: Dicionário com comando
            
        Returns:
            Resposta JSON ou None se erro
        """
        try:
            # Enviar comando
            json_str = json.dumps(comando)
            self.socket.sendall(json_str.encode('utf-8'))
            
            # Receber resposta em chunks (máx 10MB)
            resposta_completa = b''
            tamanho_chunk = 1024 * 1024  # 1MB por chunk
            
            while True:
                chunk = self.socket.recv(tamanho_chunk)
                if not chunk:
                    break
                resposta_completa += chunk
                # Se recebeu menos que o tamanho do chunk, provavelmente é o final
                if len(chunk) < tamanho_chunk:
                    break
            
            resposta_json = resposta_completa.decode('utf-8')
            resposta = json.loads(resposta_json)
            
            return resposta
            
        except socket.timeout:
            print("❌ Timeout aguardando resposta do servidor")
            self.conectado = False
            return None
        except Exception as e:
            print(f"❌ Erro na comunicação: {e}")
            self.conectado = False
            return None
    
    def fechar(self) -> None:
        """Fecha conexão com servidor"""
        if self.socket:
            try:
                self.socket.close()
                self.conectado = False
                print(f"✓ Conexão fechada com {self.host}:{self.port}")
            except:
                pass
    
    def __del__(self):
        """Garante que conexão seja fechada"""
        self.fechar()


class GerenciadorServidoresSocket:
    """Gerencia múltiplas conexões socket com servidores remotos"""
    
    def __init__(self, servidores: List[Tuple[str, int]]):
        """
        Inicializa gerenciador
        
        Args:
            servidores: Lista de tuplas (host, port)
            
        Exemplo:
            servidores = [
                ('192.168.1.100', 5001),
                ('192.168.1.101', 5001)
            ]
            gerenciador = GerenciadorServidoresSocket(servidores)
        """
        self.servidores = servidores
        self.clientes = {}
        self.conectados = 0
        
    def conectar_todos(self) -> int:
        """
        Conecta a todos os servidores
        
        Returns:
            Número de conexões bem-sucedidas
        """
        print(f"\n🔌 Conectando a {len(self.servidores)} servidores...")
        
        for idx, (host, port) in enumerate(self.servidores):
            cliente = ClienteSocket(host, port)
            if cliente.conectar():
                self.clientes[idx] = cliente
                self.conectados += 1
            else:
                self.clientes[idx] = None
        
        print(f"✅ {self.conectados}/{len(self.servidores)} conexões estabelecidas")
        return self.conectados
    
    def testar_todos(self) -> int:
        """
        Testa todos os servidores
        
        Returns:
            Número de servidores respondendo
        """
        print(f"\n🧪 Testando {len(self.clientes)} conexões...")
        respondendo = 0
        
        for idx, cliente in self.clientes.items():
            if cliente and cliente.testar_conexao():
                respondendo += 1
        
        print(f"✅ {respondendo}/{len(self.clientes)} servidores respondendo")
        return respondendo
    
    def distribuir_blocos(self, 
                         matriz_a: np.ndarray, 
                         matriz_b: np.ndarray) -> Optional[np.ndarray]:
        """
        Distribui linhas de A entre servidores para multiplicar por B
        
        Args:
            matriz_a: Matriz A
            matriz_b: Matriz B
            
        Returns:
            Matriz C resultado (A × B), ou None se erro
        """
        
        if self.conectados == 0:
            print("❌ Nenhum servidor conectado")
            return None
        
        try:
            m, n = matriz_a.shape
            p = matriz_b.shape[1]
            
            # Dividir A em blocos
            tam_bloco = m // self.conectados
            blocos = []
            
            for i in range(self.conectados):
                inicio = i * tam_bloco
                fim = inicio + tam_bloco if i < self.conectados - 1 else m
                blocos.append({
                    'inicio': inicio,
                    'fim': fim,
                    'bloco': matriz_a[inicio:fim]
                })
            
            print(f"\n📤 Distribuindo {m} linhas entre {self.conectados} servidores")
            
            # Enviar blocos e receber resultados
            resultados = {}
            tempo_inicio = time.time()
            
            for idx, bloco_info in enumerate(blocos):
                cliente = self.clientes.get(idx)
                if not cliente or not cliente.conectado:
                    print(f"   ⚠️ Servidor {idx} não conectado, pulando...")
                    continue
                
                inicio = bloco_info['inicio']
                bloco = bloco_info['bloco']
                
                print(f"   📡 Enviando bloco {idx} (linhas {inicio}-{bloco_info['fim']})")
                
                resposta = cliente.multiplicar_bloco(bloco, matriz_b, inicio)
                
                if resposta and resposta.get('status') == 'sucesso':
                    resultados[idx] = {
                        'inicio': inicio,
                        'resultado': np.array(resposta.get('resultado', []))
                    }
                    print(f"      ✅ Recebido resultado")
                else:
                    print(f"      ❌ Erro ao receber resultado")
            
            tempo_total = time.time() - tempo_inicio
            
            # Remontar resultado
            if len(resultados) == self.conectados:
                c = np.zeros((m, p))
                for idx in range(self.conectados):
                    if idx in resultados:
                        inicio = resultados[idx]['inicio']
                        resultado = resultados[idx]['resultado']
                        fim = inicio + resultado.shape[0]
                        c[inicio:fim] = resultado
                
                print(f"\n✅ Distribuição concluída em {tempo_total*1000:.2f}ms")
                return c
            else:
                print(f"❌ Apenas {len(resultados)}/{self.conectados} resultados")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao distribuir: {e}")
            return None
    
    def fechar_todos(self) -> None:
        """Fecha todas as conexões"""
        print(f"\n🔌 Fechando {len(self.clientes)} conexões...")
        for cliente in self.clientes.values():
            if cliente:
                cliente.fechar()
        self.clientes.clear()
        self.conectados = 0
    
    def __del__(self):
        """Garante que conexões sejam fechadas"""
        self.fechar_todos()
