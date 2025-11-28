import os


def salvar_json(texto, destino="resumos_JSON", contador=1):
    os.makedirs(destino, exist_ok=True)
    nome = os.path.join(destino, f"resumo{contador}.json")

    with open(nome, "w", encoding="utf-8") as f:
        f.write(texto)
