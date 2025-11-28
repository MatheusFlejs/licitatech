import os
import requests


def baixar_pdf(url, destino="pdfs", contador=1):
    os.makedirs(destino, exist_ok=True)
    nome = os.path.join(destino, f"arquivo{contador}.pdf")

    try:
        resp = requests.get(url)
        resp.raise_for_status()

        with open(nome, "wb") as f:
            f.write(resp.content)

        return nome

    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")
        return None
