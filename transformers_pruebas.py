from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

MODEL_NAME = "google/flan-t5-large"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


def generar_analisis(origen, rutas, iteraciones, total_nodos) -> str:
    rutas_texto = ""
    for r in rutas:
        rutas_texto += (
            f"- Destino: {r['destino']}\n"
            f"  Distancia mínima: {r['distancia']}\n"
            f"  Ruta óptima: {r['ruta']}\n\n"
        )

    prompt = f"""
    INSTRUCCIÓN:
    Redacta un texto académico EN ESPAÑOL y con lenguaje matemático formal.
    NO repitas el enunciado del problema.
    RESPONDE ÚNICAMENTE con las secciones solicitadas.

    ESTRUCTURA OBLIGATORIA (respétala exactamente):

    ANÁLISIS DE SENSIBILIDAD:
    (explica cómo cambios en los pesos afectan las rutas óptimas)

    CONCLUSIONES:
    (interpreta el comportamiento matemático del sistema)

    RECOMENDACIONES:
    (propón mejoras a la red y decisiones operativas)

    DATOS DEL PROBLEMA:
    Nodo origen: {origen}
    Total de nodos: {total_nodos}
    Iteraciones: {iteraciones}

    RUTAS ÓPTIMAS CALCULADAS:
    {rutas_texto}
    """

    # 🔍 DEBUG CRÍTICO
    print("\n================ PROMPT ENVIADO AL MODELO ================\n")
    print(prompt)
    print("\n===========================================================\n")

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    )

    print("🔢 Tokens de entrada:", inputs["input_ids"].shape)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=350,
            do_sample=False,
            repetition_penalty=1.3,
            no_repeat_ngram_size=3
        )

    respuesta = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print("\n================ RESPUESTA RAW DEL MODELO ================\n")
    print(respuesta)
    print("\n==========================================================\n")

    return respuesta
