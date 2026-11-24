import os
from html import escape

ARQUIVO_LOGS = "logs.txt"
PASTA_RELATORIOS = "relatorios"
LIMITE_ALERTA = 4

os.makedirs(PASTA_RELATORIOS, exist_ok=True)

try:
    with open(ARQUIVO_LOGS, "r", encoding="utf-8") as arquivo:
        linhas = arquivo.readlines()
except FileNotFoundError:
    print(f"Arquivo '{ARQUIVO_LOGS}' não encontrado.")
    raise SystemExit(1)

total = sum(1 for linha in linhas if linha.strip())
info = sum(1 for linha in linhas if linha.strip().startswith("INFO:"))
warning = sum(1 for linha in linhas if linha.strip().startswith("WARNING:"))
error = sum(1 for linha in linhas if linha.strip().startswith("ERROR:"))

tentativas = {}
for linha in linhas:
    if linha.strip().startswith("LOGIN:"):
        partes = linha.split(":", 1)
        if len(partes) == 2:
            ip = partes[1].strip()
            if ip:
                tentativas[ip] = tentativas.get(ip, 0) + 1

ips_ordenados = sorted(tentativas.items(), key=lambda item: item[1], reverse=True)
if ips_ordenados:
    ip_principal, maior_quantidade = ips_ordenados[0]
else:
    ip_principal = "Nenhum"
    maior_quantidade = 0

alertas = [(ip, quantidade) for ip, quantidade in ips_ordenados if quantidade >= LIMITE_ALERTA]

linhas_ips_html = []
for ip, quantidade in ips_ordenados:
    if quantidade >= LIMITE_ALERTA:
        situacao = "Alerta"
        classe = "alerta"
    else:
        situacao = "Normal"
        classe = "normal"

    linhas_ips_html.append(
        f'<tr><td>{escape(ip)}</td><td>{quantidade}</td><td class="{classe}">{situacao}</td></tr>'
    )

if not linhas_ips_html:
    linhas_ips_html.append('<tr><td colspan="3">Nenhuma tentativa de login encontrada.</td></tr>')

linhas_ips = "\n".join(linhas_ips_html)

relatorio_txt = []
relatorio_txt.append("===== RELATORIO DE SEGURANCA =====")
relatorio_txt.append(f"Total de registros: {total}")
relatorio_txt.append(f"Informacoes (INFO): {info}")
relatorio_txt.append(f"Avisos (WARNING): {warning}")
relatorio_txt.append(f"Erros (ERROR): {error}")
relatorio_txt.append("")
relatorio_txt.append("===== TENTATIVAS POR IP =====")
if ips_ordenados:
    for ip, quantidade in ips_ordenados:
        relatorio_txt.append(f"{ip}: {quantidade} tentativa(s)")
else:
    relatorio_txt.append("Nenhuma tentativa de login encontrada.")
relatorio_txt.append("")
relatorio_txt.append("===== ALERTAS =====")
if alertas:
    for ip, quantidade in alertas:
        relatorio_txt.append(f"ALERTA: {ip} possui {quantidade} tentativas.")
else:
    relatorio_txt.append("Nenhum IP atingiu o limite de alerta.")
relatorio_txt.append("")
relatorio_txt.append(f"IP com mais tentativas: {ip_principal}")
relatorio_txt.append(f"Quantidade: {maior_quantidade}")

caminho_txt = os.path.join(PASTA_RELATORIOS, "relatorio.txt")
with open(caminho_txt, "w", encoding="utf-8") as arquivo:
    arquivo.write("\n".join(relatorio_txt))

html_relatorio = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Relatório de Segurança</title>
<style>
body {{
    background: #101827;
    color: white;
    font-family: Arial, sans-serif;
    padding: 30px;
    margin: 0;
}}
.container {{ max-width: 1100px; margin: auto; }}
h1 {{ color: #60a5fa; }}
.dashboard {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 15px;
    margin: 25px 0;
}}
.card {{
    background: #1e293b;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 15px;
}}
.metric {{ font-size: 30px; font-weight: bold; margin-top: 10px; }}
.info {{ color: #60a5fa; }}
.warning {{ color: #facc15; }}
.error {{ color: #f87171; }}
.ips {{ color: #4ade80; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
th, td {{
    padding: 14px;
    text-align: left;
    border-bottom: 1px solid #475569;
}}
th {{ color: #60a5fa; }}
.alerta {{ color: #f87171; font-weight: bold; }}
.normal {{ color: #4ade80; }}
@media (max-width: 600px) {{
    body {{ padding: 15px; }}
    th, td {{ padding: 9px; }}
}}
</style>
</head>
<body>
<div class="container">
<h1>Painel de Segurança</h1>
<p>Relatório de análise de logs do sistema</p>

<div class="dashboard">
    <div class="card">
        <h3>Informações</h3>
        <div class="metric info">{info}</div>
    </div>
    <div class="card">
        <h3>Avisos</h3>
        <div class="metric warning">{warning}</div>
    </div>
    <div class="card">
        <h3>Erros</h3>
        <div class="metric error">{error}</div>
    </div>
    <div class="card">
        <h3>IPs monitorados</h3>
        <div class="metric ips">{len(tentativas)}</div>
    </div>
</div>

<div class="card">
    <h2>Resumo da análise</h2>
    <p>Total de registros: {total}</p>
</div>

<div class="card">
    <h2>IP com mais tentativas</h2>
    <p>{escape(ip_principal)}: {maior_quantidade} tentativa(s)</p>
</div>

<div class="card">
    <h2>Atividade por endereço IP</h2>
    <table>
        <tr>
            <th>Endereço IP</th>
            <th>Tentativas</th>
            <th>Situação</th>
        </tr>
        {linhas_ips}
    </table>
</div>
</div>
</body>
</html>
"""

caminho_html = os.path.join(PASTA_RELATORIOS, "relatorio.html")
with open(caminho_html, "w", encoding="utf-8") as arquivo:
    arquivo.write(html_relatorio)

print("===== RESUMO =====")
print(f"Total de registros: {total}")
print(f"INFO: {info} | WARNING: {warning} | ERROR: {error}")
print(f"IPs monitorados: {len(tentativas)}")
print("\n===== ALERTAS =====")
if alertas:
    for ip, quantidade in alertas:
        print(f"ALERTA: {ip} possui {quantidade} tentativas.")
else:
    print("Nenhum IP atingiu o limite de alerta.")
print(f"\nIP com mais tentativas: {ip_principal}")
print(f"Quantidade: {maior_quantidade}")
print("\nRelatorios TXT e HTML gerados com sucesso!")
