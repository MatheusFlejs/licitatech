import os
import re


def gerar_html(dados, destino="resumos_html", contador=1):
    os.makedirs(destino, exist_ok=True)
    nome = os.path.join(destino, f"resumo{contador}.html")

    titulo = dados.get("numero", f"Edital {contador}")

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Resumo do {titulo}</title>
    <style>
        body {{ font-family: Arial; background:#f9f9f9; padding:30px; }}
        .container {{ max-width:800px; margin:auto; background:#fff; padding:30px; border-radius:10px; }}
        dt {{ font-weight:bold; color:#005a9c; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Resumo do Edital</h1>
        <dl>
            <dt>Data:</dt><dd>{dados.get("data", "Não informado")}</dd>
            <dt>Número:</dt><dd>{dados.get("numero", "Não informado")}</dd>
            <dt>Órgão:</dt><dd>{dados.get("orgao", "Não informado")}</dd>
            <dt>Objeto:</dt><dd>{dados.get("objeto", "Não informado")}</dd>
        </dl>
    </div>
</body>
</html>
"""

    with open(nome, "w", encoding="utf-8") as f:
        f.write(html)

    return f"resumo{contador}.html"


def gerar_html_bruto_formatado(texto, destino="resumos_html", contador=1):
    os.makedirs(destino, exist_ok=True)
    nome = os.path.join(destino, f"resumo{contador}.html")

    texto = re.sub(r"[`\[\]{}()]", "", texto)
    linhas = texto.split("\n")
    campos = {}

    for linha in linhas:
        if ":" in linha:
            k, v = linha.split(":", 1)
            campos[k.strip()] = v.strip()

    html = "<html><body><h1>Resumo Bruto</h1>"
    for k, v in campos.items():
        html += f"<p><b>{k}:</b> {v}</p>"
    html += "</body></html>"

    with open(nome, "w", encoding="utf-8") as f:
        f.write(html)

    return f"resumo{contador}.html"


def gerar_indice_html(lista_resumos, destino="resumos_html"):
    nome = os.path.join(destino, "index.html")

    html = """<html><body><h1>Índice</h1><ul>"""
    for r in lista_resumos:
        html += f'<li><a href="{r}">{r}</a></li>'
    html += "</ul></body></html>"

    with open(nome, "w", encoding="utf-8") as f:
        f.write(html)
