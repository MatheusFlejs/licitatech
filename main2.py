import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pathlib
from google import genai
from google.genai import types
import json

# 🔐 Configuração da API Gemini
os.environ["GOOGLE_API_KEY"] = "AIzaSyBWOMcssQFdCHNTx1MePoL19YNPYL53D8g"
gemini_client = genai.Client()

# 🧭 Configuração do Selenium
def iniciar_navegador():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=chrome_options)

# 🔗 Extrair links de PDFs do site de Arapongas
def extrair_links_arapongas():
    navegador = iniciar_navegador()
    navegador.get("https://arapongas.atende.net/diariooficial/edicao")
    time.sleep(3)
    soup = BeautifulSoup(navegador.page_source, "html.parser")
    links_pdf = [btn["data-link"] for btn in soup.find_all("button", {"data-link": True}) if "processo=download" in btn["data-link"]]
    navegador.quit()
    return links_pdf

# Link para editas
#https://arapongas.atende.net/transparencia/item/licitacoes-gerais

# 📥 Baixar PDF
def baixar_pdf(url, destino="pdfs", contador=1):
    os.makedirs(destino, exist_ok=True)
    nome_arquivo = os.path.join(destino, f"arquivo{contador}.pdf")
    try:
        resposta = requests.get(url)
        resposta.raise_for_status()
        with open(nome_arquivo, "wb") as f:
            f.write(resposta.content)
        return nome_arquivo
    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")
        return None

# 🧠 Resumo com Gemini
def enviar_para_gemini(caminho_pdf):
    try:
        prompt = (
            "Extraia os seguintes dados deste edital de licitação e retorne em formato JSON:\n"
            "Data do edital, número do edital, data de abertura das propostas, data de fechamento das propostas, órgão responsável, objeto da contratação, modalidade, prazo, itens principais."
            "As datas devem estar no formato de SQL completo com horário"
        )
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[
                types.Part.from_bytes(
                    data=pathlib.Path(caminho_pdf).read_bytes(),
                    mime_type='application/pdf',
                ),
                prompt
            ]
        )
        return response.text
    except Exception as e:
        return f"Erro ao usar Gemini: {e}"

# 🎨 Gerar HTML com CSS moderno
def gerar_html(dados, destino="resumos_html", contador=1):
    os.makedirs(destino, exist_ok=True)
    nome_arquivo = os.path.join(destino, f"resumo{contador}.html")
    titulo = dados.get("numero", f"Edital {contador}")

    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Resumo do {titulo}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f9f9f9;
            padding: 30px;
            color: #333;
        }}
        .container {{
            max-width: 800px;
            margin: auto;
            background-color: #fff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #005a9c;
        }}
        dl {{
            display: grid;
            grid-template-columns: max-content 1fr;
            row-gap: 10px;
            column-gap: 20px;
        }}
        dt {{
            font-weight: bold;
            color: #005a9c;
        }}
        dd {{
            margin: 0;
        }}
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
            <dt>Modalidade:</dt><dd>{dados.get("modalidade", "Não informado")}</dd>
            <dt>Prazo:</dt><dd>{dados.get("prazo", "Não informado")}</dd>
            <dt>Itens Principais:</dt><dd>{dados.get("itens", "Não informado")}</dd>
        </dl>
    </div>
</body>
</html>
"""
    try:
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"📁 HTML salvo em: {nome_arquivo}")
        return f"resumo{contador}.html"
    except Exception as e:
        print(f"Erro ao salvar HTML: {e}")
        return None

def gerar_html_bruto_formatado(texto, destino="resumos_html", contador=1):
    import re
    os.makedirs(destino, exist_ok=True)
    nome_arquivo = os.path.join(destino, f"resumo{contador}.html")

    # Remove blocos de código e caracteres especiais
    texto_limpo = re.sub(r"[`\[\]{}()]", "", texto)
    texto_limpo = texto_limpo.replace("json", "").strip()

    # Tenta extrair os campos principais
    linhas = texto_limpo.split("\n")
    campos = {}
    itens_principais = []

    for linha in linhas:
        if ":" in linha:
            chave, valor = linha.split(":", 1)
            chave = chave.strip()
            valor = valor.strip()
            if chave.lower().startswith("empresa") or chave.lower().startswith("cnpj") or chave.lower().startswith("evento") or chave.lower().startswith("valor") or chave.lower().startswith("quantidade"):
                itens_principais.append((chave, valor))
            else:
                campos[chave] = valor

    # Gera HTML
    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Resumo bruto {contador}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f9f9f9;
            padding: 30px;
            color: #333;
        }}
        .container {{
            max-width: 800px;
            margin: auto;
            background-color: #fff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #005a9c;
            margin-bottom: 20px;
        }}
        h2 {{
            color: #333;
            margin-top: 30px;
        }}
        p {{
            margin: 10px 0;
        }}
        .label {{
            font-weight: bold;
            color: #005a9c;
        }}
        ul {{
            margin: 10px 0 20px 20px;
        }}
        li {{
            margin-bottom: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Resumo do Edital</h1>
"""

    for chave, valor in campos.items():
        html += f'<p><span class="label">{chave}:</span> {valor}</p>\n'

    if itens_principais:
        html += "<h2>Itens Principais</h2>\n<ul>\n"
        for chave, valor in itens_principais:
            html += f"<li><span class='label'>{chave}:</span> {valor}</li>\n"
        html += "</ul>\n"

    html += """
    </div>
</body>
</html>
"""

    try:
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"📁 HTML formatado salvo em: {nome_arquivo}")
        return f"resumo{contador}.html"
    except Exception as e:
        print(f"Erro ao salvar HTML formatado: {e}")
        return None

# 📝 Salvar conteúdo bruto como JSON
def salvar_json(texto, destino="resumos_JSON", contador=1):
    os.makedirs(destino, exist_ok=True)
    nome_arquivo = os.path.join(destino, f"resumo{contador}.json")
    try:
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(texto)
        print(f"📝 JSON salvo em: {nome_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar JSON: {e}")

# 📚 Gerar índice com links para os resumos
def gerar_indice_html(lista_resumos, destino="resumos_html"):
    nome_arquivo = os.path.join(destino, "index.html")
    html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Índice de Editais</title>
    <style>
        body { font-family: Arial; padding: 30px; background: #f0f0f0; }
        h1 { color: #005a9c; }
        ul { list-style: none; padding: 0; }
        li { margin: 10px 0; }
        a { text-decoration: none; color: #333; }
        a:hover { color: #005a9c; }
    </style>
</head>
<body>
    <h1>Índice de Editais</h1>
    <ul>
"""
    for nome in lista_resumos:
        html += f'<li><a href="{nome}">{nome}</a></li>\n'

    html += """
    </ul>
</body>
</html>
"""
    try:
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"📁 Índice salvo em: {nome_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar índice: {e}")

# 🔄 Pipeline completo
def executar_pipeline():
    print("🔍 Buscando PDFs de Arapongas...")
    links = extrair_links_arapongas()
    print(f"✅ Encontrados {len(links)} PDFs.")

    resumos_gerados = []

    for i, url in enumerate(links, start=1):
        print(f"\n📥 Baixando arquivo{i}.pdf")
        caminho = baixar_pdf(url, contador=i)
        if caminho:
            print("🧠 Resumindo com Gemini...")
            resumo_json = enviar_para_gemini(caminho)

            try:
                dados = json.loads(resumo_json)
                nome_html = gerar_html(dados, contador=i)
                if nome_html:
                    resumos_gerados.append(nome_html)
            except Exception as e:
                print(f"⚠️ Erro ao interpretar o resumo como JSON: {e}")
                print("📝 Conteúdo bruto:\n", resumo_json)
                salvar_json(resumo_json, contador=i)
                nome_html = gerar_html_bruto_formatado(resumo_json, contador=i)
                if nome_html:
                    resumos_gerados.append(nome_html)
        else:
            print("⚠️ Falha no download.")

    if resumos_gerados:
        gerar_indice_html(resumos_gerados)

# 🚀 Executar
if __name__ == "__main__":
    executar_pipeline()