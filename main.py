import os
import time
import requests
import fitz  # PyMuPDF
import openai
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
client = openai.OpenAI(api_key="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")


# Configuração do Selenium
def iniciar_navegador():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    navegador = webdriver.Chrome(options=chrome_options)
    return navegador

# Extrair links de PDFs do site de Arapongas via data-link
def extrair_links_arapongas():
    navegador = iniciar_navegador()
    navegador.get("https://arapongas.atende.net/diariooficial/edicao")
    time.sleep(3)  # aguarda carregamento

    soup = BeautifulSoup(navegador.page_source, "html.parser")
    links_pdf = []

    for botao in soup.find_all("button", {"data-link": True}):
        link = botao["data-link"]
        if "processo=download" in link:
            links_pdf.append(link)

    navegador.quit()
    return links_pdf

# Baixar PDF com nome sequencial
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

# Ler conteúdo do PDF
def ler_pdf(caminho_pdf):
    texto = ""
    try:
        with fitz.open(caminho_pdf) as doc:
            for pagina in doc:
                texto += pagina.get_text()
    except Exception as e:
        print(f"Erro ao ler {caminho_pdf}: {e}")
    return texto

# Pipeline completo
def executar_pipeline():
    print("🔍 Buscando PDFs de Arapongas...")
    links = extrair_links_arapongas()
    print(f"✅ Encontrados {len(links)} PDFs.")

    for i, url in enumerate(links, start=1):
        print(f"\n📥 Baixando arquivo{i}.pdf")
        caminho = baixar_pdf(url, contador=i)
        if caminho:
            print("📖 Lendo conteúdo...")
            texto = ler_pdf(caminho)
            print(f"📝 Conteúdo inicial do arquivo{i}.pdf:\n")
           # print(texto[:1000])  # mostra os primeiros 1000 caracteres
            resposta = enviar_para_chatgpt(texto)
            print(resposta)
        else:
            print("⚠️ Falha no download.")

def enviar_para_chatgpt(texto):
    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um especialista em licitações públicas."},
            {"role": "user", "content": f"Analise este edital:\n\n{texto}"}
        ]
    )
    return resposta.choices[0].message.content


# Executar o processo
if __name__ == "__main__":
    executar_pipeline()
