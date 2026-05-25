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
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.conectado = False
        
    def conectar(self) -> bool:
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
        if not self.conectado:
            return False
        
        try:
            resposta = self._enviar_comando({'operacao': 'teste'})
            if resposta and resposta.get('status') == 'sucesso':
                print(f"✅ Servidor respondeu: {resposta.get('mensagem')}")
                return True
            else:
                print(f"❌ Resposta inválida: {resposta}")
                return False
        except Exception as e:
            print(f"❌ Erro ao testar conexão: {e}")
            return False
    
    def multiplicar_bloco(self, bloco_a: np.ndarray, matriz_b: np.ndarray, inicio_linha: int = 0) -> Optional[Dict[str, Any]]:
        if not self.conectado:
            print("❌ Não conectado ao servidor")
            return None
        
        try:
            comando = {
                'operacao': 'multiplicar_bloco',
                'bloco_a': bloco_a.tolist(),
                'matriz_b': matriz_b.tolist(),
                'inicio_linha': inicio_linha
            }
            
            resposta = self._enviar_comando(comando)
            
            if resposta and resposta.get('status') == 'sucesso':
                return resposta
            else:
                msg = resposta.get('mensagem') if resposta else "Sem resposta"
                print(f"❌ Erro no servidor: {msg}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao multiplicar bloco: {e}")
            self.conectado = False
            return None
    
    def _enviar_comando(self, comando: dict) -> Optional[dict]:
        """Envia comando JSON e recebe resposta com proteção contra fragmentação TCP"""
        try:
            json_str = json.dumps(comando)
            self.socket.sendall(json_str.encode('utf-8'))
            
            resposta_completa = b''
            tamanho_chunk = 1024 * 1024  # 1MB por chunk
            
            while True:
                chunk = self.socket.recv(tamanho_chunk)
                if not chunk:
                    break
                
                resposta_completa += chunk
                
                try:
                    resposta_json = resposta_completa.decode('utf-8')
                    resposta = json.loads(resposta_json)
                    return resposta
                except json.JSONDecodeError:
                    continue
            
            return None
            
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
        self.servidores = servidores
        self.clientes = {}
        self.conectados = 0
        
    def conectar_todos(self) -> int:
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
        print(f"\n🧪 Testando {len(self.clientes)} conexões...")
        respondendo = 0
        for idx, cliente in self.clientes.items():
            if cliente and cliente.testar_conexao():
                respondendo += 1
        
        print(f"✅ {respondendo}/{len(self.clientes)} servidores respondendo")
        return respondendo
    
    def distribuir_blocos(self, matriz_a: np.ndarray, matriz_b: np.ndarray) -> Optional[np.ndarray]:
        import concurrent.futures # Importação necessária para a concorrência
        
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
            
            print(f"\n📤 Distribuindo {m} linhas entre {self.conectados} servidores (CONCORRENTE)")
            
            resultados = {}
            tempo_inicio = time.time()
            
            # Função auxiliar que a Thread vai executar
            def processar_bloco(idx, bloco_info):
                cliente = self.clientes.get(idx)
                if not cliente or not cliente.conectado:
                    return idx, None
                
                inicio = bloco_info['inicio']
                bloco = bloco_info['bloco']
                
                print(f"   📡 A enviar bloco {idx} (linhas {inicio}-{bloco_info['fim']})...")
                resposta = cliente.multiplicar_bloco(bloco, matriz_b, inicio)
                
                if resposta and resposta.get('status') == 'sucesso':
                    print(f"      ✅ Recebido resultado do bloco {idx}")
                    return idx, {
                        'inicio': inicio,
                        'resultado': np.array(resposta.get('resultado', []))
                    }
                return idx, None

            # Dispara todos os pedidos AO MESMO TEMPO
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.conectados) as executor:
                futuros = []
                for idx, bloco_info in enumerate(blocos):
                    futuros.append(executor.submit(processar_bloco, idx, bloco_info))
                
                # Aguarda e recolhe os resultados assim que chegam
                for futuro in concurrent.futures.as_completed(futuros):
                    idx, res = futuro.result()
                    if res:
                        resultados[idx] = res
            
            tempo_total = time.time() - tempo_inicio
            
            # Remontar o resultado
            if len(resultados) == self.conectados:
                c = np.zeros((m, p))
                for idx in range(self.conectados):
                    if idx in resultados:
                        inicio = resultados[idx]['inicio']
                        resultado = resultados[idx]['resultado']
                        fim = inicio + resultado.shape[0]
                        c[inicio:fim] = resultado
                
                print(f"\n✅ Distribuição concorrente concluída em {tempo_total*1000:.2f}ms")
                return c
            else:
                print(f"❌ Apenas {len(resultados)}/{self.conectados} resultados")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao distribuir: {e}")
            return None
    
    def fechar_todos(self) -> None:
        print(f"\n🔌 Fechando {len(self.clientes)} conexões...")
        for cliente in self.clientes.values():
            if cliente:
                cliente.fechar()
        self.clientes.clear()
        self.conectados = 0
    
    def __del__(self):
        self.fechar_todos()