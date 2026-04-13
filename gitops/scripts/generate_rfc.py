import requests
import os

def generate_rfc():
    input_file = "tf.txt"
    output_file = "RFC.md"

    if not os.path.exists(input_file): return

    with open(input_file, "r") as f:
        content = f.read()
    
    # Extraemos líneas con cambios (+)
    clean_plan = "\n".join([l.strip() for l in content.split('\n') if "+" in l])[:1500]

    prompt = f"""<|system|>
Eres un Ingeniero Cloud Senior. Genera un reporte de cambio (RFC) formal para GERENCIA en ESPAÑOL.
Usa tablas de Markdown y un tono ejecutivo.
<|user|>
Resume este plan de Terraform:
{clean_plan}

REQUERIMIENTOS:
1. Usa una tabla con: | Componente | Acción | Detalle |
2. Agrega una sección de "Resumen Ejecutivo".
3. Agrega una sección de "Análisis de Riesgo".
<|assistant|>"""

    payload = {
        "model": "tinyllama",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 600}
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        result = response.json().get("response", "Error")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.strip())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_rfc()