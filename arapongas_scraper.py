import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def iniciar_navegador():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=chrome_options)


def extrair_links_arapongas():
    navegador = iniciar_navegador()
    navegador.get("https://arapongas.atende.net/diariooficial/edicao")
    time.sleep(3)

    soup = BeautifulSoup(navegador.page_source, "html.parser")
    navegador.quit()

    return [
        btn["data-link"]
        for btn in soup.find_all("button", {"data-link": True})
        if "processo=download" in btn["data-link"]
    ]
