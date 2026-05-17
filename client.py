"""
CLIENTE DISTRIBUÍDO — Multiplicação de Matrizes em Rede
Divide o trabalho entre múltiplos servidores remotos
"""

import socket
import json
import time
import requests
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np


class ClienteDistribuido:
    """Cliente para multiplicação distribuída de matrizes"""
    
    def __init__(self, servidores: List[str], timeout: int = 30):
        """
        Inicializa cliente distribuído
        
        Args:
            servidores: Lista de URLs dos servidores (ex: ['http://localhost:5001', 'http://localhost:5002'])
            timeout: Tempo máximo para requisição (segundos)
        """
        self.servidores = servidores
        self.timeout = timeout
        self.validar_servidores()
    
    def validar_servidores(self):
        """Verifica quais servidores estão online"""
        online = []
        offline = []
        
        print(f"[+] Validando {len(self.servidores)} servidor(es)...")
        
        for servidor in self.servidores:
            try:
                resposta = requests.get(f"{servidor}/health", timeout=2)
                if resposta.status_code == 200:
                    online.append(servidor)
                    print(f"  ✓ {servidor}")
                else:
                    offline.append(servidor)
                    print(f"  ✗ {servidor} (Status: {resposta.status_code})")
            except Exception as e:
                offline.append(servidor)
                print(f"  ✗ {servidor} ({type(e).__name__})")
        
        self.servidores = online
        
        if not online:
            raise ConnectionError("Nenhum servidor disponível!")
        
        print(f"[+] {len(online)} servidor(es) online, {len(offline)} offline\n")
    
    def multiplicar_distribuido(
        self,
        A: List[List[int]],
        B: List[List[int]]
    ) -> Tuple[List[List[int]], Dict]:
        """
        Multiplica A × B de forma distribuída
        Divide as linhas de A entre os servidores
        
        Args:
            A: Matriz M × N
            B: Matriz N × P
        
        Returns:
            (resultado, stats)
        """
        
        M = len(A)  # linhas de A
        N = len(A[0])  # colunas de A = linhas de B
        P = len(B[0])  # colunas de B
        num_servidores = len(self.servidores)
        
        print(f"[*] Multiplicação distribuída: {M}×{N} × {N}×{P}")
        print(f"[*] Dividindo entre {num_servidores} servidor(es)\n")
        
        # Calcula tamanho do bloco
        tam_bloco = max(1, M // num_servidores)
        
        # Prepara tarefas
        tarefas = {}
        for servidor_id, servidor in enumerate(self.servidores):
            inicio = servidor_id * tam_bloco
            fim = min(inicio + tam_bloco, M) if servidor_id < num_servidores - 1 else M
            
            linhas_bloco = A[inicio:fim]
            tarefas[servidor_id] = {
                'servidor': servidor,
                'task_id': f"task_{servidor_id}",
                'linhas': (inicio, fim),
                'matriz_a': linhas_bloco,
                'matriz_b': B,
            }
        
        # Executa em paralelo
        t_inicio = time.perf_counter()
        
        resultados_blocos = {}
        tempos_servidor = {}
        
        with ThreadPoolExecutor(max_workers=num_servidores) as executor:
            futures = {}
            
            for srv_id, tarefa in tarefas.items():
                future = executor.submit(self._executar_tarefa, tarefa)
                futures[future] = srv_id
            
            for future in as_completed(futures):
                srv_id = futures[future]
                try:
                    bloco_resultado, tempo_servidor = future.result()
                    resultados_blocos[srv_id] = bloco_resultado
                    tempos_servidor[srv_id] = tempo_servidor
                except Exception as e:
                    print(f"  ✗ Erro no servidor {srv_id}: {e}")
                    raise
        
        t_total = time.perf_counter() - t_inicio
        
        # Monta resultado final
        C = [None] * M
        for srv_id in sorted(resultados_blocos.keys()):
            inicio, fim = tarefas[srv_id]['linhas']
            bloco = resultados_blocos[srv_id]
            for off, linha in enumerate(bloco):
                C[inicio + off] = linha
        
        # Estatísticas
        stats = {
            'tempo_total': round(t_total, 6),
            'tempo_por_servidor': tempos_servidor,
            'num_servidores': num_servidores,
            'dimensoes': {
                'A': [M, N],
                'B': [N, P],
                'C': [M, P]
            }
        }
        
        return C, stats
    
    def _executar_tarefa(self, tarefa: Dict) -> Tuple[List[List[int]], float]:
        """Executa tarefa em um servidor remoto"""
        
        payload = {
            'matriz_a': tarefa['matriz_a'],
            'matriz_b': tarefa['matriz_b'],
            'task_id': tarefa['task_id'],
        }
        
        try:
            resposta = requests.post(
                f"{tarefa['servidor']}/multiply",
                json=payload,
                timeout=self.timeout
            )
            
            if resposta.status_code != 200:
                raise Exception(f"Status {resposta.status_code}: {resposta.text}")
            
            dados = resposta.json()
            
            if dados.get('status') != 'success':
                raise Exception(f"Erro: {dados.get('mensagem', 'Desconhecido')}")
            
            print(f"  ✓ {tarefa['task_id']} concluído em {dados['tempo']:.4f}s")
            
            return dados['resultado'], dados['tempo']
        
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Timeout ao comunicar com {tarefa['servidor']}")
        except Exception as e:
            raise Exception(f"Erro em {tarefa['servidor']}: {str(e)}")


def testar_cliente():
    """Testa cliente distribuído"""
    
    # Tenta conectar a servidores locais
    servidores = [
        'http://localhost:5001',
        'http://localhost:5002',
        'http://localhost:5003',
    ]
    
    try:
        cliente = ClienteDistribuido(servidores)
        
        # Teste com matrizes pequenas
        A = np.random.randint(1, 10, (50, 50)).tolist()
        B = np.random.randint(1, 10, (50, 50)).tolist()
        
        resultado, stats = cliente.multiplicar_distribuido(A, B)
        
        print("[+] Resultado:")
        print(f"    Amostra [0:3, 0:3]:")
        for i in range(min(3, len(resultado))):
            print(f"      {resultado[i][:3]}")
        print(f"\n[+] Estatísticas:")
        print(f"    Tempo total: {stats['tempo_total']}s")
        print(f"    Servidores: {stats['num_servidores']}")
        
    except Exception as e:
        print(f"[-] Erro: {e}")


if __name__ == '__main__':
    testar_cliente()
