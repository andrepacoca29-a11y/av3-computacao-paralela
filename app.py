"""
APLICAÇÃO PRINCIPAL — Multiplicação de Matrizes: Serial vs Paralela vs Distribuída
Interface web para execução de benchmarks e visualização de resultados

Requisitos atendidos:
  ✓ Computação distribuída (serial, paralela, distribuída)
  ✓ Suporte a matrizes não-quadráticas (M × N × P)
  ✓ Comparação de desempenho
  ✓ Geração de gráficos comparativos (PNG)
  ✓ Armazenamento e visualização de matrizes
  ✓ Relatório HTML com resultados

Execução:  python app.py
Acesso:    http://localhost:5000
"""

import time
import json
import os
import threading
import multiprocessing
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from datetime import datetime

from matrix_operations import executar_benchmark, criar_matriz, amostrar_matriz
from graphics import GeradorGraficos, salvar_resultados_json, gerar_relatorio_html, salvar_matrizes_csv


# ═══════════════════════════════════════════════════════════════════
#  VARIÁVEIS GLOBAIS
# ═══════════════════════════════════════════════════════════════════

HISTORICO_RESULTADOS = []
RESULTADOS_JSON = "resultados/resultados.json"
RELATORIO_HTML = "resultados/relatorio.html"


def create_html(cpus):
    """Cria página HTML da interface web"""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Computação Distribuída — AV2 2026</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap" rel="stylesheet">
<style>
:root{{--bg:#09090f;--surf:#111118;--bord:#1e1e2e;--accent:#00e5ff;--green:#00ff9d;--yellow:#ffd600;--red:#ff4d6d;--text:#e0e0f0;--muted:#5a5a7a;--blue:#4d9eff}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:'Syne',sans-serif;min-height:100vh;overflow-x:hidden}}
body::before{{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(0,229,255,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(0,229,255,.03) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;z-index:0}}
.wrap{{position:relative;z-index:1;max-width:1200px;margin:0 auto;padding:40px 20px 80px}}
header{{margin-bottom:40px}}
.chip{{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--accent);border:1px solid var(--accent);padding:4px 10px;border-radius:2px;margin-bottom:12px;letter-spacing:.08em}}
h1{{font-size:2.5em;font-weight:800;line-height:1.1;letter-spacing:-.02em}}
h1 span{{color:var(--accent)}}
.sub{{margin-top:10px;color:var(--muted);font-family:'JetBrains Mono',monospace;font-size:12px}}
.card{{background:var(--surf);border:1px solid var(--bord);border-radius:12px;padding:28px;margin-bottom:22px;position:relative;overflow:hidden}}
.card::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--accent),transparent)}}
.card-title{{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--muted);letter-spacing:.1em;text-transform:uppercase;margin-bottom:20px}}
.form-row{{display:grid;grid-template-columns:1fr 1fr auto;gap:14px;align-items:end}}
@media(max-width:800px){{.form-row{{grid-template-columns:1fr}}}}
label{{display:block;font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--muted);letter-spacing:.08em;margin-bottom:6px;text-transform:uppercase}}
input[type=number]{{width:100%;background:var(--bg);border:1px solid var(--bord);border-radius:8px;color:var(--text);font-family:'JetBrains Mono',monospace;font-size:16px;font-weight:700;padding:12px;outline:none;-moz-appearance:textfield}}
input[type=number]::-webkit-outer-spin-button,input[type=number]::-webkit-inner-spin-button{{-webkit-appearance:none}}
input:focus{{border-color:var(--accent);box-shadow:0 0 0 2px rgba(0,229,255,.1)}}
.btn{{background:var(--accent);color:#000;border:none;border-radius:8px;font-family:'Syne',sans-serif;font-size:14px;font-weight:700;padding:12px 24px;cursor:pointer;transition:all .15s;white-space:nowrap}}
.btn:hover{{transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,229,255,.25)}}
.btn:disabled{{opacity:.4;cursor:not-allowed}}
.presets{{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}}
.pbtn{{font-family:'JetBrains Mono',monospace;font-size:11px;background:transparent;border:1px solid var(--bord);color:var(--muted);border-radius:6px;padding:6px 12px;cursor:pointer;transition:all .15s}}
.pbtn:hover{{border-color:var(--accent);color:var(--accent)}}
#loading{{display:none;align-items:center;gap:12px;padding:20px 0}}
.spin{{width:20px;height:20px;border:2px solid var(--bord);border-top-color:var(--accent);border-radius:50%;animation:spin .7s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
#ltxt{{font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--accent)}}
#results{{display:none}}
.metric-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:24px}}
.metric{{background:var(--bg);border:1px solid var(--bord);border-radius:10px;padding:14px}}
.mlbl{{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--muted);letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px}}
.mval{{font-family:'JetBrains Mono',monospace;font-size:18px;font-weight:700;line-height:1}}
.msub{{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--muted);margin-top:3px}}
.chart-row{{display:flex;align-items:center;gap:12px;padding:12px;background:var(--bg);border-radius:8px;border:1px solid var(--bord);margin-bottom:10px}}
.chart-lbl{{font-family:'JetBrains Mono',monospace;font-size:10px;width:90px;flex-shrink:0}}
.chart-bar{{flex:1;height:24px;background:rgba(255,255,255,.05);border-radius:3px;overflow:hidden;position:relative}}
.chart-fill{{height:100%;transition:width .6s ease;display:flex;align-items:center;justify-content:flex-end;padding-right:6px}}
.chart-text{{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;color:rgba(0,0,0,.8)}}
.matrix-section{{max-height:350px;overflow-y:auto;background:var(--bg);border-radius:8px;border:1px solid var(--bord);padding:10px}}
.mtbl{{border-collapse:collapse;font-family:'JetBrains Mono',monospace;font-size:10px;width:100%}}
.mtbl td{{padding:3px 6px;border:1px solid var(--bord);text-align:right;color:var(--muted)}}
.mtbl td:first-child{{color:var(--accent);font-weight:bold}}
.reveal{{opacity:0;transform:translateY(10px);transition:all .4s ease}}
.reveal.show{{opacity:1;transform:none}}
.download-row{{display:flex;gap:10px;margin-top:12px;flex-wrap:wrap}}
.dbtn{{font-family:'JetBrains Mono',monospace;font-size:11px;background:var(--bord);color:var(--text);border:1px solid var(--muted);border-radius:6px;padding:6px 14px;cursor:pointer;text-decoration:none;display:inline-block;transition:all .15s}}
.dbtn:hover{{background:var(--accent);color:#000;border-color:var(--accent)}}
.info{{background:rgba(0,229,255,.05);border:1px solid rgba(0,229,255,.2);border-radius:8px;padding:12px;margin:10px 0;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--muted)}}
</style>
</head>
<body>
<div class="wrap">

<header>
  <div class="chip">COMPUTAÇÃO DISTRIBUÍDA · AV2 2026 · PARALELA E CONCORRENTE</div>
  <h1>Multiplicação de<br><span>Matrizes</span></h1>
  <p class="sub">Serial vs Paralela vs Distribuída • Numpy + Multiprocessing • {cpus} núcleos detectados</p>
</header>

<div class="card">
  <div class="card-title">// Teste de Benchmark</div>
  <div class="form-row">
    <div><label for="m">Linhas A (M)</label><input type="number" id="m" value="100" min="10" max="500"></div>
    <div><label for="n">Colunas A (N)</label><input type="number" id="n" value="100" min="10" max="500"></div>
    <div><label for="p">Colunas B (P)</label><input type="number" id="p" value="100" min="10" max="500"></div>
    <button class="btn" onclick="executar()">▶ Executar</button>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px">
    <div>
      <label for="tipo-matriz">Tipo de Matriz</label>
      <select id="tipo-matriz" style="width:100%;background:var(--bg);border:1px solid var(--bord);border-radius:8px;color:var(--text);font-family:'JetBrains Mono',monospace;font-size:14px;padding:10px;outline:none">
        <option value="aleatoria">Aleatória (1-10)</option>
        <option value="zeros">Zeros</option>
        <option value="uns">Uns</option>
        <option value="identidade">Identidade</option>
        <option value="diagonal">Diagonal</option>
        <option value="triangular">Triangular</option>
      </select>
    </div>
    <div>
      <label for="num-proc">Processos / Nodos</label>
      <input type="number" id="num-proc" value="2" min="1" max="8">
    </div>
  </div>
  <div class="presets">
    <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--muted)">Presets:</span>
    <button class="pbtn" onclick="setDim(100,100,100)">100×100</button>
    <button class="pbtn" onclick="setDim(150,150,150)">150×150</button>
    <button class="pbtn" onclick="setDim(200,200,200)">200×200</button>
    <button class="pbtn" onclick="setDim(100,50,200)">100×50×200</button>
    <button class="pbtn" onclick="setDim(200,150,100)">200×150×100</button>
  </div>
</div>

<div id="loading"><div class="spin"></div><span id="ltxt">Processando...</span></div>

<div id="results">
  <div class="card reveal">
    <div class="card-title">// Resultados de Benchmark</div>
    <div class="metric-grid">
      <div class="metric"><div class="mlbl">Serial</div><div class="mval" id="m-serial" style="color:var(--blue)">—</div><div class="msub">s</div></div>
      <div class="metric"><div class="mlbl">Paralelo</div><div class="mval" id="m-paralelo" style="color:var(--green)">—</div><div class="msub">s</div></div>
      <div class="metric"><div class="mlbl">Distribuído</div><div class="mval" id="m-distribuido" style="color:var(--yellow)">—</div><div class="msub">s</div></div>
      <div class="metric"><div class="mlbl">Speedup P</div><div class="mval" id="m-sp-p" style="color:var(--green)">—</div><div class="msub">×</div></div>
      <div class="metric"><div class="mlbl">Speedup D</div><div class="mval" id="m-sp-d" style="color:var(--yellow)">—</div><div class="msub">×</div></div>
      <div class="metric"><div class="mlbl">Eficiência</div><div class="mval" id="m-efic" style="color:var(--accent)">—</div><div class="msub">%</div></div>
    </div>
    
    <div style="margin-top:20px">
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--muted);text-transform:uppercase;margin-bottom:10px">Comparação de Tempos</div>
      <div class="chart-row">
        <span class="chart-lbl" style="color:var(--blue)">Serial</span>
        <div class="chart-bar"><div class="chart-fill" id="bar-s" style="background:var(--blue)"><span class="chart-text" id="bar-s-text"></span></div></div>
      </div>
      <div class="chart-row">
        <span class="chart-lbl" style="color:var(--green)">Paralelo</span>
        <div class="chart-bar"><div class="chart-fill" id="bar-p" style="background:var(--green)"><span class="chart-text" id="bar-p-text"></span></div></div>
      </div>
      <div class="chart-row">
        <span class="chart-lbl" style="color:var(--yellow)">Distribuído</span>
        <div class="chart-bar"><div class="chart-fill" id="bar-d" style="background:var(--yellow)"><span class="chart-text" id="bar-d-text"></span></div></div>
      </div>
    </div>
  </div>

  <div class="card reveal">
    <div class="card-title">// Matriz Resultado (primeiras 6×6 células)</div>
    <div style="margin-bottom:10px;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--muted)">
      A: <span style="color:var(--accent)" id="dim-a">—</span> | 
      B: <span style="color:var(--accent)" id="dim-b">—</span> | 
      C: <span style="color:var(--green)" id="dim-c">—</span>
    </div>
    <div class="matrix-section"><table class="mtbl" id="mtbl"></table></div>
  </div>

  <div class="card reveal">
    <div class="card-title">// Validação e Downloads</div>
    <div class="info" id="validation-info"></div>
    <div class="download-row">
      <a href="/download/json" class="dbtn" id="btn-json" style="display:none">📥 JSON</a>
      <a href="/download/html" class="dbtn" id="btn-html" style="display:none">📊 Relatório HTML</a>
      <a href="/graficos" class="dbtn" id="btn-graficos-link" style="display:none; background:var(--green); color:#000">📈 Ver Gráficos (5)</a>
    </div>
  </div>
</div>

</div>

<script>
function setDim(m, n, p) {{
  document.getElementById('m').value = m;
  document.getElementById('n').value = n;
  document.getElementById('p').value = p;
}}

const historico = [];

async function executar() {{
  const M = parseInt(document.getElementById('m').value);
  const N = parseInt(document.getElementById('n').value);
  const P = parseInt(document.getElementById('p').value);
  const tipoMatriz = document.getElementById('tipo-matriz').value;
  const numProc = parseInt(document.getElementById('num-proc').value);
  
  if (!M || !N || !P || M < 10 || N < 10 || P < 10) {{
    alert('Dimensões inválidas!');
    return;
  }}
  
  document.getElementById('results').style.display = 'none';
  document.getElementById('loading').style.display = 'flex';
  
  const msgs = ['Gerando matrizes...', 'Executando serial...', 'Executando paralelo...', 'Executando distribuído...'];
  let idx = 0;
  const interval = setInterval(() => {{ 
    document.getElementById('ltxt').textContent = msgs[idx++ % msgs.length]; 
  }}, 600);
  
  try {{
    const res = await fetch(`/benchmark?m=${{M}}&n=${{N}}&p=${{P}}&tipo=${{tipoMatriz}}&proc=${{numProc}}`);
    const data = await res.json();
    
    clearInterval(interval);
    document.getElementById('loading').style.display = 'none';
    
    renderizar(data);
    historico.push(data);
    
    if (historico.length >= 2) {{
      document.getElementById('btn-json').style.display = 'inline-block';
      document.getElementById('btn-html').style.display = 'inline-block';
    }}
  }} catch(e) {{
    clearInterval(interval);
    document.getElementById('loading').style.display = 'none';
    alert('Erro: ' + e.message);
  }}
}}

function renderizar(d) {{
  document.getElementById('results').style.display = 'block';
  
  const t_s = d.tempos.serial;
  const t_p = d.tempos.paralelo;
  const t_d = d.tempos.distribuido;
  const max = Math.max(t_s, t_p, t_d);
  
  document.getElementById('m-serial').textContent = t_s.toFixed(6);
  document.getElementById('m-paralelo').textContent = t_p.toFixed(6);
  document.getElementById('m-distribuido').textContent = t_d.toFixed(6);
  document.getElementById('m-sp-p').textContent = d.speedups.paralelo.toFixed(4);
  document.getElementById('m-sp-d').textContent = d.speedups.distribuido.toFixed(4);
  document.getElementById('m-efic').textContent = d.eficiencia.paralelo.toFixed(1);
  
  setTimeout(() => {{
    document.getElementById('bar-s').style.width = ((t_s / max) * 100) + '%';
    document.getElementById('bar-s-text').textContent = t_s.toFixed(4) + 's';
    
    document.getElementById('bar-p').style.width = ((t_p / max) * 100) + '%';
    document.getElementById('bar-p-text').textContent = t_p.toFixed(4) + 's';
    
    document.getElementById('bar-d').style.width = ((t_d / max) * 100) + '%';
    document.getElementById('bar-d-text').textContent = t_d.toFixed(4) + 's';
  }}, 50);
  
  document.getElementById('dim-a').textContent = d.dimensoes.A[0] + '×' + d.dimensoes.A[1];
  document.getElementById('dim-b').textContent = d.dimensoes.B[0] + '×' + d.dimensoes.B[1];
  document.getElementById('dim-c').textContent = d.dimensoes.C[0] + '×' + d.dimensoes.C[1];
  
  const tbl = document.getElementById('mtbl');
  tbl.innerHTML = '';
  d.amostra_resultado.forEach((row, i) => {{
    const tr = document.createElement('tr');
    const ti = document.createElement('td');
    ti.textContent = `[${{i}}]`;
    tr.appendChild(ti);
    row.forEach(v => {{
      const td = document.createElement('td');
      td.textContent = Math.round(v);
      tr.appendChild(td);
    }});
    const te = document.createElement('td');
    te.textContent = '…';
    te.style.color = 'var(--bord)';
    tr.appendChild(te);
    tbl.appendChild(tr);
  }});
  
  let info = '';
  info += d.validacao.paralelo ? '✓ Paralelo OK | ' : '✗ Paralelo ERRO | ';
  info += d.validacao.distribuido ? '✓ Distribuído OK | ' : '✗ Distribuído ERRO | ';
  info += 'Overhead paralelo: ' + Math.abs(d.overhead_paralelo).toFixed(6) + 's';
  
  document.getElementById('validation-info').textContent = info;
  
  // Exibe botões de download e gráficos
  if (d.graficos_disponiveis) {{
    document.getElementById('btn-graficos-link').style.display = 'inline-block';
  }}
  
  document.getElementById('btn-json').style.display = 'inline-block';
  document.getElementById('btn-html').style.display = 'inline-block';
  
  document.querySelectorAll('.reveal').forEach((el, i) => {{
    setTimeout(() => el.classList.add('show'), i * 100);
  }});
}}

function mostrarGraficos() {{
  window.location.href = '/graficos';
}}
</script>
</body>
</html>"""


class WebHandler(BaseHTTPRequestHandler):
    """Handler para requisições HTTP da interface web"""
    
    def log_message(self, *args):
        pass
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/':
            self.enviar_html()
        elif parsed.path == '/graficos':
            self.enviar_pagina_graficos()
        elif parsed.path.startswith('/resultados/'):
            self.servir_arquivo_estatico(parsed.path)
        elif parsed.path == '/benchmark':
            self.executar_benchmark(parsed)
        elif parsed.path.startswith('/download/'):
            self.baixar_arquivo(parsed)
        else:
            self.enviar_404()
    
    def enviar_html(self):
        html = create_html(multiprocessing.cpu_count()).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(html))
        self.end_headers()
        self.wfile.write(html)
    
    def enviar_pagina_graficos(self):
        try:
            with open('graficos.html', 'r', encoding='utf-8') as f:
                html = f.read().encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(html))
            self.end_headers()
            self.wfile.write(html)
        except FileNotFoundError:
            self.enviar_erro("Página de gráficos não encontrada")
        except Exception as e:
            self.enviar_erro(str(e))
    
    def servir_arquivo_estatico(self, caminho):
        """Serve arquivos estáticos (PNG, JSON, etc) da pasta resultados/"""
        try:
            nome_arquivo = caminho.split('/')[-1]
            # Usa caminho absoluto para evitar problemas com diretório relativo
            caminho_completo = os.path.abspath(os.path.join(os.path.dirname(__file__), 'resultados', nome_arquivo))
            
            if not os.path.exists(caminho_completo):
                self.send_response(404)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Arquivo nao encontrado')
                return
            
            # Detecta tipo MIME
            if nome_arquivo.endswith('.png'):
                content_type = 'image/png'
            elif nome_arquivo.endswith('.json'):
                content_type = 'application/json'
            else:
                content_type = 'application/octet-stream'
            
            with open(caminho_completo, 'rb') as f:
                conteudo = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(conteudo))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(conteudo)
        except Exception as e:
            self.enviar_erro(f"Erro ao servir arquivo: {str(e)}")
    
    def executar_benchmark(self, parsed):
        try:
            qs = parse_qs(parsed.query)
            M = max(10, min(int(qs.get('m', ['100'])[0]), 10000))
            N = max(10, min(int(qs.get('n', ['100'])[0]), 10000))
            P = max(10, min(int(qs.get('p', ['100'])[0]), 10000))
            tipo_matriz = qs.get('tipo', ['aleatoria'])[0]
            num_proc = max(1, min(int(qs.get('proc', ['2'])[0]), multiprocessing.cpu_count()))
            
            print(f"\n[+] Benchmark: A({M}×{N}) × B({N}×{P}) = C({M}×{P})")
            print(f"    Tipo: {tipo_matriz} | Processos: {num_proc}")
            
            num_cores = multiprocessing.cpu_count()
            
            resultado = executar_benchmark(
                m=M, n=N, p=P,
                num_processos=num_proc,
                num_nodos=max(2, num_proc),
                seed_a=42, seed_b=43,
                tipo_matriz=tipo_matriz
            )
            
            HISTORICO_RESULTADOS.append(resultado)
            
            # Salva matrizes completas em CSV
            print("\n[+] Salvando matrizes completas em CSV...")
            try:
                matrizes_A = resultado.get('matrizes', {}).get('A')
                matrizes_B = resultado.get('matrizes', {}).get('B')
                amostra_C = resultado.get('amostra_resultado')
                
                if matrizes_A and matrizes_B and amostra_C:
                    from matrix_operations import multiplicar_serial
                    C_completa = multiplicar_serial(matrizes_A, matrizes_B)
                    
                    caminhos_matrizes = salvar_matrizes_csv(matrizes_A, matrizes_B, C_completa)
                    resultado['arquivos_matrizes'] = caminhos_matrizes
                    print("[✓] Matrizes salvas em CSV!")
            except Exception as e:
                print(f"[⚠] Aviso ao salvar matrizes: {e}")
            
            # Sempre gera gráficos em tempo real (não espera por 2 testes)
            print("\n[+] Gerando gráficos comparativos...")
            try:
                gerador = GeradorGraficos()
                graficos = gerador.gerar_todos(HISTORICO_RESULTADOS)
                salvar_resultados_json(HISTORICO_RESULTADOS, RESULTADOS_JSON)
                gerar_relatorio_html(HISTORICO_RESULTADOS, graficos, RELATORIO_HTML)
                print("[✓] Gráficos e relatório gerados!")
                resultado['graficos_disponiveis'] = True
                resultado['arquivos_graficos'] = list(graficos.values())
                resultado['relatorio_html'] = RELATORIO_HTML
            except Exception as e:
                print(f"[⚠] Erro ao gerar gráficos: {e}")
                resultado['graficos_disponiveis'] = False
            
            self.enviar_json(resultado)
        
        except Exception as e:
            print(f"[-] Erro: {e}")
            self.enviar_erro(str(e))
    
    def baixar_arquivo(self, parsed):
        tipo = parsed.path.split('/')[-1]
        
        try:
            if tipo == 'json':
                caminho = RESULTADOS_JSON
                content_type = 'application/json'
            elif tipo == 'html':
                caminho = RELATORIO_HTML
                content_type = 'text/html; charset=utf-8'
            else:
                self.enviar_404()
                return
            
            if not os.path.exists(caminho):
                self.enviar_erro("Arquivo não encontrado")
                return
            
            with open(caminho, 'rb') as f:
                conteudo = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(conteudo))
            self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(caminho)}"')
            self.end_headers()
            self.wfile.write(conteudo)
        
        except Exception as e:
            self.enviar_erro(str(e))
    
    def enviar_json(self, dados):
        json_str = json.dumps(dados, ensure_ascii=False, indent=2).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(json_str))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json_str)
    
    def enviar_erro(self, mensagem):
        resposta = {'status': 'erro', 'mensagem': mensagem}
        self.enviar_json(resposta)
    
    def enviar_404(self):
        self.send_response(404)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Not found')


def iniciar_servidor(porta=5000):
    """Inicia servidor web"""
    
    print(f"""
╔═══════════════════════════════════════════════════════╗
║ MULTIPLICAÇÃO DISTRIBUÍDA DE MATRIZES — AV2 2026     ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║ 🌐 Interface Web: http://localhost:{porta:<39}║
║                                                       ║
║ 📊 Recursos:                                          ║
║   • Serial: Benchmark                                 ║
║   • Paralela: Multiprocessing                         ║
║   • Distribuída: Simulado                             ║
║                                                       ║
║ ✓ Suporte a matrizes não-quadráticas                 ║
║ ✓ Gráficos comparativos                              ║
║ ✓ Armazenamento de resultados                        ║
║ ✓ Relatório HTML                                     ║
║                                                       ║
║ Núcleos detectados: {multiprocessing.cpu_count()}                              ║
║ Ctrl+C para encerrar                                 ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
""")
    
    try:
        import webbrowser
        threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{porta}')).start()
    except:
        pass
    
    try:
        servidor = HTTPServer(('localhost', porta), WebHandler)
        print("✓ Servidor iniciado e aguardando conexões...\n")
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Servidor encerrado.")
    except OSError as e:
        print(f"✗ Erro ao iniciar servidor: {e}")


if __name__ == '__main__':
    multiprocessing.freeze_support()
    iniciar_servidor(porta=5000)
