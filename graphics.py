"""
Geração de gráficos comparativos dos resultados de benchmark
"""

import os
import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
from typing import List, Dict


class GeradorGraficos:
    def __init__(self, diretorio_saida: str = "resultados"):
        self.diretorio = diretorio_saida
        os.makedirs(diretorio_saida, exist_ok=True)
        
        # Configuração visual
        plt.style.use('dark_background')
        self.cores = {
            'serial': '#4d9eff',      # azul
            'paralelo': '#00ff9d',    # verde
            'distribuido': '#ffd600', # amarelo
        }
        self.tamanho_fonte = 11
    
    def salvar_figura(self, fig, nome: str) -> str:
        """Salva figura e retorna caminho"""
        caminho = os.path.join(self.diretorio, nome)
        fig.savefig(caminho, dpi=100, bbox_inches='tight', facecolor='#09090f')
        plt.close(fig)
        print(f"✓ Gráfico salvo: {caminho}")
        return caminho
    
    def grafico_tempos(self, dados_list: List[Dict]) -> str:
        """Gráfico comparativo de tempos de execução"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        tamanhos = []
        tempos_serial = []
        tempos_paralelo = []
        tempos_distribuido = []
        
        for dado in dados_list:
            # Usa área da matriz como identificador
            area = dado['dimensoes']['A'][0] * dado['dimensoes']['A'][1]
            tamanhos.append(f"{dado['dimensoes']['A'][0]}×{dado['dimensoes']['A'][1]}")
            tempos_serial.append(dado['tempos']['serial'])
            tempos_paralelo.append(dado['tempos']['paralelo'])
            tempos_distribuido.append(dado['tempos']['distribuido'])
        
        x = range(len(tamanhos))
        width = 0.25
        
        ax.bar([i - width for i in x], tempos_serial, width, label='Serial', 
               color=self.cores['serial'], alpha=0.8)
        ax.bar([i for i in x], tempos_paralelo, width, label='Paralelo', 
               color=self.cores['paralelo'], alpha=0.8)
        ax.bar([i + width for i in x], tempos_distribuido, width, label='Distribuído', 
               color=self.cores['distribuido'], alpha=0.8)
        
        ax.set_xlabel('Dimensões da Matriz', fontsize=self.tamanho_fonte, fontweight='bold')
        ax.set_ylabel('Tempo (segundos)', fontsize=self.tamanho_fonte, fontweight='bold')
        ax.set_title('Comparação de Tempos de Execução', fontsize=13, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(tamanhos, rotation=45, ha='right')
        ax.legend(fontsize=self.tamanho_fonte, loc='upper left')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        return self.salvar_figura(fig, 'grafico_tempos.png')
    
    def grafico_speedup(self, dados_list: List[Dict]) -> str:
        """Gráfico de speedup (ganho de desempenho)"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        tamanhos = []
        speedups_paralelo = []
        speedups_distribuido = []
        
        for dado in dados_list:
            tamanhos.append(f"{dado['dimensoes']['A'][0]}×{dado['dimensoes']['A'][1]}")
            speedups_paralelo.append(dado['speedups']['paralelo'])
            speedups_distribuido.append(dado['speedups']['distribuido'])
        
        x = range(len(tamanhos))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], speedups_paralelo, width, label='Speedup Paralelo',
               color=self.cores['paralelo'], alpha=0.8)
        ax.bar([i + width/2 for i in x], speedups_distribuido, width, label='Speedup Distribuído',
               color=self.cores['distribuido'], alpha=0.8)
        
        # Linha de referência ideal (speedup = 1)
        ax.axhline(y=1, color='#888', linestyle='--', linewidth=2, alpha=0.6, label='Sem ganho (1×)')
        
        ax.set_xlabel('Dimensões da Matriz', fontsize=self.tamanho_fonte, fontweight='bold')
        ax.set_ylabel('Speedup (×)', fontsize=self.tamanho_fonte, fontweight='bold')
        ax.set_title('Speedup: Paralelismo vs Serial', fontsize=13, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(tamanhos, rotation=45, ha='right')
        ax.legend(fontsize=self.tamanho_fonte, loc='upper left')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        return self.salvar_figura(fig, 'grafico_speedup.png')
    
    def grafico_eficiencia(self, dados_list: List[Dict]) -> str:
        """Gráfico de eficiência (speedup / numero de processadores)"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        tamanhos = []
        efic_paralelo = []
        efic_distribuido = []
        
        for dado in dados_list:
            tamanhos.append(f"{dado['dimensoes']['A'][0]}×{dado['dimensoes']['A'][1]}")
            efic_paralelo.append(dado['eficiencia']['paralelo'])
            efic_distribuido.append(dado['eficiencia']['distribuido'])
        
        x = range(len(tamanhos))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], efic_paralelo, width, label='Eficiência Paralela',
               color=self.cores['paralelo'], alpha=0.8)
        ax.bar([i + width/2 for i in x], efic_distribuido, width, label='Eficiência Distribuída',
               color=self.cores['distribuido'], alpha=0.8)
        
        # Linha de 100% (ideal)
        ax.axhline(y=100, color='#0f0', linestyle='--', linewidth=2, alpha=0.6, label='Eficiência 100%')
        
        ax.set_xlabel('Dimensões da Matriz', fontsize=self.tamanho_fonte, fontweight='bold')
        ax.set_ylabel('Eficiência (%)', fontsize=self.tamanho_fonte, fontweight='bold')
        ax.set_title('Eficiência: Uso de Recursos', fontsize=13, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(tamanhos, rotation=45, ha='right')
        ax.legend(fontsize=self.tamanho_fonte, loc='upper right')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_ylim([0, 120])
        
        return self.salvar_figura(fig, 'grafico_eficiencia.png')
    
    def grafico_overhead(self, dados_list: List[Dict]) -> str:
        """Gráfico de overhead de comunicação"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        tamanhos = []
        overhead_paralelo = []
        overhead_distribuido = []
        
        for dado in dados_list:
            tamanhos.append(f"{dado['dimensoes']['A'][0]}×{dado['dimensoes']['A'][1]}")
            # Valores negativos significam ganho líquido
            overhead_paralelo.append(dado['overhead_paralelo'])
            overhead_distribuido.append(dado['overhead_distribuido'])
        
        x = range(len(tamanhos))
        width = 0.35
        
        cores_paralelo = [self.cores['paralelo'] if v > 0 else '#ff0000' for v in overhead_paralelo]
        cores_distribuido = [self.cores['distribuido'] if v > 0 else '#ff0000' for v in overhead_distribuido]
        
        ax.bar([i - width/2 for i in x], overhead_paralelo, width, label='Overhead Paralelo',
               color=cores_paralelo, alpha=0.8)
        ax.bar([i + width/2 for i in x], overhead_distribuido, width, label='Overhead Distribuído',
               color=cores_distribuido, alpha=0.8)
        
        # Linha zero
        ax.axhline(y=0, color='#fff', linestyle='-', linewidth=1, alpha=0.3)
        
        ax.set_xlabel('Dimensões da Matriz', fontsize=self.tamanho_fonte, fontweight='bold')
        ax.set_ylabel('Overhead (segundos)', fontsize=self.tamanho_fonte, fontweight='bold')
        ax.set_title('Overhead de Comunicação (IPC)', fontsize=13, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(tamanhos, rotation=45, ha='right')
        ax.legend(fontsize=self.tamanho_fonte)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        return self.salvar_figura(fig, 'grafico_overhead.png')
    
    def grafico_escalabilidade(self, dados_list: List[Dict]) -> str:
        """Gráfico de escalabilidade (como o tempo varia com o tamanho)"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        tamanhos_numericos = []
        tempos_serial = []
        tempos_paralelo = []
        tempos_distribuido = []
        
        for dado in dados_list:
            area = dado['dimensoes']['A'][0] * dado['dimensoes']['A'][1]
            tamanhos_numericos.append(area)
            tempos_serial.append(dado['tempos']['serial'])
            tempos_paralelo.append(dado['tempos']['paralelo'])
            tempos_distribuido.append(dado['tempos']['distribuido'])
        
        # Gráfico 1: Tempo vs Tamanho
        ax1.plot(tamanhos_numericos, tempos_serial, 'o-', label='Serial', 
                color=self.cores['serial'], linewidth=2, markersize=8)
        ax1.plot(tamanhos_numericos, tempos_paralelo, 's-', label='Paralelo', 
                color=self.cores['paralelo'], linewidth=2, markersize=8)
        ax1.plot(tamanhos_numericos, tempos_distribuido, '^-', label='Distribuído', 
                color=self.cores['distribuido'], linewidth=2, markersize=8)
        
        ax1.set_xlabel('Área da Matriz (elementos)', fontsize=self.tamanho_fonte, fontweight='bold')
        ax1.set_ylabel('Tempo (segundos)', fontsize=self.tamanho_fonte, fontweight='bold')
        ax1.set_title('Escalabilidade: Tempo vs Tamanho', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=self.tamanho_fonte)
        ax1.grid(True, alpha=0.3, linestyle='--')
        
        # Gráfico 2: Razão paralelo/serial vs tamanho
        razoes_paralelo = [t_p / t_s if t_s > 0 else 0 for t_p, t_s in zip(tempos_paralelo, tempos_serial)]
        razoes_distribuido = [t_d / t_s if t_s > 0 else 0 for t_d, t_s in zip(tempos_distribuido, tempos_serial)]
        
        ax2.plot(tamanhos_numericos, razoes_paralelo, 's-', label='Paralelo/Serial', 
                color=self.cores['paralelo'], linewidth=2, markersize=8)
        ax2.plot(tamanhos_numericos, razoes_distribuido, '^-', label='Distribuído/Serial', 
                color=self.cores['distribuido'], linewidth=2, markersize=8)
        ax2.axhline(y=1, color='#888', linestyle='--', linewidth=2, alpha=0.6, label='Paridade')
        
        ax2.set_xlabel('Área da Matriz (elementos)', fontsize=self.tamanho_fonte, fontweight='bold')
        ax2.set_ylabel('Razão de Tempo', fontsize=self.tamanho_fonte, fontweight='bold')
        ax2.set_title('Razão: Paralelismo / Serial', fontsize=12, fontweight='bold')
        ax2.legend(fontsize=self.tamanho_fonte)
        ax2.grid(True, alpha=0.3, linestyle='--')
        
        return self.salvar_figura(fig, 'grafico_escalabilidade.png')
    
    def gerar_todos(self, dados_list: List[Dict]) -> Dict[str, str]:
        """Gera todos os gráficos de uma vez"""
        resultados = {
            'tempos': self.grafico_tempos(dados_list),
            'speedup': self.grafico_speedup(dados_list),
            'eficiencia': self.grafico_eficiencia(dados_list),
            'overhead': self.grafico_overhead(dados_list),
            'escalabilidade': self.grafico_escalabilidade(dados_list),
        }
        return resultados


def salvar_matrizes_csv(A: List, B: List, C: List, diretorio: str = "resultados") -> Dict[str, str]:
    """
    Salva as matrizes completas em arquivos CSV
    
    Args:
        A: Matriz A (M × N)
        B: Matriz B (N × P)
        C: Matriz C resultado (M × P)
        diretorio: Diretório de saída
    
    Returns:
        Dicionário com caminhos dos arquivos salvos
    """
    os.makedirs(diretorio, exist_ok=True)
    
    caminhos = {}
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # Salva Matriz A
        arquivo_a = os.path.join(diretorio, f"matriz_A_{timestamp}.csv")
        with open(arquivo_a, 'w', encoding='utf-8', newline='') as f:
            for linha in A:
                f.write(','.join(str(round(x, 4)) for x in linha) + '\n')
        caminhos['A'] = arquivo_a
        print(f"✓ Matriz A salva: {arquivo_a}")
        
        # Salva Matriz B
        arquivo_b = os.path.join(diretorio, f"matriz_B_{timestamp}.csv")
        with open(arquivo_b, 'w', encoding='utf-8', newline='') as f:
            for linha in B:
                f.write(','.join(str(round(x, 4)) for x in linha) + '\n')
        caminhos['B'] = arquivo_b
        print(f"✓ Matriz B salva: {arquivo_b}")
        
        # Salva Matriz C (resultado)
        arquivo_c = os.path.join(diretorio, f"matriz_C_resultado_{timestamp}.csv")
        with open(arquivo_c, 'w', encoding='utf-8', newline='') as f:
            for linha in C:
                f.write(','.join(str(round(x, 4)) for x in linha) + '\n')
        caminhos['C'] = arquivo_c
        print(f"✓ Matriz C (resultado) salva: {arquivo_c}")
        
        # Cria arquivo de índice
        arquivo_indice = os.path.join(diretorio, f"matrizes_indice_{timestamp}.txt")
        with open(arquivo_indice, 'w', encoding='utf-8') as f:
            f.write("ÍNDICE DE MATRIZES\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Timestamp: {timestamp}\n\n")
            f.write(f"Matriz A ({len(A)}×{len(A[0])}): {arquivo_a}\n")
            f.write(f"Matriz B ({len(B)}×{len(B[0])}): {arquivo_b}\n")
            f.write(f"Matriz C ({len(C)}×{len(C[0])}): {arquivo_c}\n\n")
            f.write("=" * 60 + "\n")
            f.write("Formato: CSV (valores separados por vírgula)\n")
            f.write("Decimais: 4 casas\n")
        caminhos['indice'] = arquivo_indice
        print(f"✓ Índice de matrizes salvo: {arquivo_indice}")
        
    except Exception as e:
        print(f"✗ Erro ao salvar matrizes: {str(e)}")
    
    return caminhos


def salvar_resultados_json(dados: List[Dict], nome_arquivo: str = "resultados/resultados.json"):
    """Salva resultados em JSON para posterior análise"""
    os.makedirs(os.path.dirname(nome_arquivo), exist_ok=True)
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'benchmarks': dados
        }, f, indent=2, ensure_ascii=False)
    print(f"✓ Resultados salvos em: {nome_arquivo}")


def gerar_relatorio_html(
    dados_list: List[Dict],
    graficos: Dict[str, str],
    nome_arquivo: str = "resultados/relatorio.html"
) -> str:
    """Gera relatório HTML com gráficos embarcados"""
    os.makedirs(os.path.dirname(nome_arquivo), exist_ok=True)
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Benchmark - Multiplicação de Matrizes Distribuída</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: #09090f;
            color: #e0e0f0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 20px; }}
        h1 {{ font-size: 2.5em; margin-bottom: 10px; color: #00e5ff; }}
        .subtitle {{ color: #5a5a7a; margin-bottom: 40px; }}
        .section {{ background: #111118; border: 1px solid #1e1e2e; border-radius: 12px; 
                     padding: 30px; margin-bottom: 30px; border-top: 3px solid #00e5ff; }}
        .section h2 {{ font-size: 1.8em; margin-bottom: 20px; color: #00ff9d; }}
        .grafico {{ text-align: center; margin: 20px 0; }}
        .grafico img {{ max-width: 100%; height: auto; border-radius: 8px; }}
        .tabela {{ overflow-x: auto; margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; font-family: 'JetBrains Mono', monospace; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #1e1e2e; }}
        th {{ background: #1e1e2e; color: #00e5ff; font-weight: bold; }}
        tr:hover {{ background: rgba(255,255,255,.03); }}
        .ok {{ color: #00ff9d; }}
        .warning {{ color: #ffd600; }}
        .error {{ color: #ff4d6d; }}
        .timestamp {{ color: #5a5a7a; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Relatório de Benchmark</h1>
        <p class="subtitle">Multiplicação de Matrizes: Serial vs Paralela vs Distribuída</p>
        <p class="timestamp">Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
        
        <div class="section">
            <h2>Resumo dos Testes</h2>
            <div class="tabela">
                <table>
                    <tr>
                        <th>Matriz A</th>
                        <th>Matriz B</th>
                        <th>Tempo Serial (s)</th>
                        <th>Tempo Paralelo (s)</th>
                        <th>Tempo Distribuído (s)</th>
                        <th>Speedup Paralelo</th>
                        <th>Speedup Distribuído</th>
                        <th>Status</th>
                    </tr>
"""
    
    for dado in dados_list:
        dims_a = f"{dado['dimensoes']['A'][0]}×{dado['dimensoes']['A'][1]}"
        dims_b = f"{dado['dimensoes']['B'][0]}×{dado['dimensoes']['B'][1]}"
        val_p = "✓" if dado['validacao']['paralelo'] else "✗"
        val_d = "✓" if dado['validacao']['distribuido'] else "✗"
        status_class = "ok" if (dado['validacao']['paralelo'] and dado['validacao']['distribuido']) else "error"
        
        html += f"""
                    <tr>
                        <td>{dims_a}</td>
                        <td>{dims_b}</td>
                        <td>{dado['tempos']['serial']:.6f}</td>
                        <td>{dado['tempos']['paralelo']:.6f}</td>
                        <td>{dado['tempos']['distribuido']:.6f}</td>
                        <td><span class="warning">{dado['speedups']['paralelo']:.4f}×</span></td>
                        <td><span class="warning">{dado['speedups']['distribuido']:.4f}×</span></td>
                        <td><span class="{status_class}">{val_p}/{val_d}</span></td>
                    </tr>
"""
    
    html += """
                </table>
            </div>
        </div>
"""
    
    # Adiciona gráficos
    for titulo, caminho in graficos.items():
        caminho_relativo = os.path.relpath(caminho, os.path.dirname(nome_arquivo))
        html += f"""
        <div class="section">
            <h2>{titulo.replace('_', ' ').title()}</h2>
            <div class="grafico">
                <img src="{caminho_relativo}" alt="{titulo}">
            </div>
        </div>
"""
    
    html += """
    </div>
</body>
</html>
"""
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Relatório HTML gerado: {nome_arquivo}")
    return nome_arquivo


if __name__ == "__main__":
    # Teste
    print("Gerador de gráficos pronto para uso")
