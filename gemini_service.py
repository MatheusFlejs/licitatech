import pathlib
from google.genai import types
from config import gemini_client


def enviar_para_gemini(caminho_pdf):
    try:
        prompt = (
            "Extraia os seguintes dados deste edital de licitação e retorne em JSON:\n"
            "Data, número, abertura, fechamento, órgão, objeto, modalidade, prazo, "
            "itens, valor unitário, valor máximo, quantidade, modo de disputa, setor, cidade, estado.\n"
            "Datas no formato SQL com horário."
        )

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[
                types.Part.from_bytes(
                    data=pathlib.Path(caminho_pdf).read_bytes(),
                    mime_type='application/pdf'
                ),
                prompt
            ]
        )

        return response.text

    except Exception as e:
        return f"Erro ao usar Gemini: {e}"
