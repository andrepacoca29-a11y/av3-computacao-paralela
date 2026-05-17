"""
SERVIDOR DISTRIBUÍDO — Multiplicação de Matrizes
Escuta por requisições de clientes e executa multiplicação de matrizes
"""

import socket
import json
import time
import argparse
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
# Certifique-se de que este arquivo matrix_operations.py existe no seu diretório
try:
    from matrix_operations import multiplicar_serial
except ImportError:
    # Fallback caso o módulo não exista para teste
    def multiplicar_serial(A, B):
        return [[sum(a*b for a, b in zip(A_row, B_col)) for B_col in zip(*B)] for A_row in A]

class MatrixServerHandler(BaseHTTPRequestHandler):
    """Handler para requisições HTTP de multiplicação de matrizes"""
    
    def log_message(self, format, *args):
        """Silencia logs padrão no terminal"""
        pass
    
    def do_GET(self):
        """Processa GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.send_status_page()
        elif parsed_path.path == '/health':
            self.health_check()
        else:
            self.send_error_response(404, "Rota não encontrada")
    
    def do_POST(self):
        """Processa POST requests com multiplicação"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/multiply':
            self.handle_multiply()
        else:
            self.send_error_response(404, "Rota não encontrada")
    
    def handle_multiply(self):
        """Multiplica duas matrizes recebidas via POST JSON"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())
            
            # Valida presença das chaves
            if 'matriz_a' not in data or 'matriz_b' not in data:
                self.send_error_response(400, "Faltam matrizes A e/ou B")
                return
            
            A = data['matriz_a']
            B = data['matriz_b']
            task_id = data.get('task_id', 'unknown')
            
            # Validação de tipo e conteúdo
            if not isinstance(A, list) or not isinstance(B, list) or not A or not B:
                self.send_error_response(400, "Matrizes devem ser listas não vazias")
                return
            
            # Validação de dimensões (Colunas de A devem ser iguais às Linhas de B)
            if len(B) != len(A[0]):
                self.send_error_response(400, f"Dimensoes incompativeis: A_cols={len(A[0])}, B_rows={len(B)}")
                return
            
            # Executa multiplicação
            print(f"  [TASK {task_id}] Recebido: A[{len(A)}x{len(A[0])}] x B[{len(B)}x{len(B[0])}]")
            
            t_inicio = time.perf_counter()
            resultado = multiplicar_serial(A, B)
            t_decorrido = time.perf_counter() - t_inicio
            
            print(f"  [TASK {task_id}] Concluido em {t_decorrido:.4f}s")
            
            # Retorna resultado
            resposta = {
                'status': 'success',
                'task_id': task_id,
                'resultado': resultado,
                'dimensoes': {
                    'A': [len(A), len(A[0])],
                    'B': [len(B), len(B[0])],
                    'C': [len(resultado), len(resultado[0])]
                },
                'tempo': round(t_decorrido, 6),
            }
            
            self.send_json_response(200, resposta)
        
        except json.JSONDecodeError:
            self.send_error_response(400, "JSON invalido")
        except Exception as e:
            self.send_error_response(500, f"Erro no servidor: {str(e)}")
    
    def health_check(self):
        """Verificação de saúde do servidor"""
        resposta = {
            'status': 'online',
            'servico': 'Servidor de Multiplicacao de Matrizes',
            'timestamp': time.time(),
        }
        self.send_json_response(200, resposta)
    
    def send_status_page(self):
        """Página de status HTML"""
        html = """<!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <title>Servidor de Matrizes</title>
                <style>
                    body { background: #09090f; color: #e0e0f0; font-family: sans-serif; padding: 40px; }
                    .card { background: #111118; border: 2px solid #00e5ff; border-radius: 8px; padding: 20px; max-width: 600px; }
                    h1 { color: #00e5ff; }
                    .endpoint { background: #1e1e2e; padding: 10px; margin: 10px 0; border-radius: 4px; }
                    .method { color: #00ff9d; font-weight: bold; }
                    .path { color: #ffd600; }
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>✓ Servidor Online</h1>
                    <p>Servidor de Multiplicação de Matrizes Distribuída</p>
                    <h2>Endpoints:</h2>
                    <div class="endpoint">
                        <div><span class="method">GET</span> <span class="path">/health</span></div>
                        <p>Verificação de saúde</p>
                    </div>
                    <div class="endpoint">
                        <div><span class="method">POST</span> <span class="path">/multiply</span></div>
                        <pre>{"matriz_a": [...], "matriz_b": [...]}</pre>
                    </div>
                </div>
            </body>
            </html>"""
        
        # Codificamos a string para bytes em UTF-8 antes de enviar
        html_bytes = html.encode('utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(html_bytes))
        self.end_headers()
        self.wfile.write(html_bytes)
    
    def send_json_response(self, code: int, data: dict):
        """Envia resposta JSON"""
        json_data = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(json_data))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json_data)
    
    def send_error_response(self, code: int, mensagem: str):
        """Envia resposta de erro"""
        resposta = {'status': 'error', 'mensagem': mensagem}
        self.send_json_response(code, resposta)


def iniciar_servidor(porta: int, host: str = '0.0.0.0'):
    """Inicia servidor de multiplicação de matrizes"""
    print(f"Tentando iniciar servidor em {host}:{porta}...")
    try:
        servidor = HTTPServer((host, porta), MatrixServerHandler)
        print(f"✓ Servidor iniciado com sucesso na porta {porta}")
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Servidor encerrado.")
    except Exception as e:
        print(f"✗ Erro: {e}")
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--porta', type=int, default=5001)
    parser.add_argument('--host', type=str, default='0.0.0.0')
    args = parser.parse_args()
    
    iniciar_servidor(args.porta, args.host)