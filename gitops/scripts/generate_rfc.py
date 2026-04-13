import requests
import os

def generate_rfc():
    input_file = "tf.txt"
    output_file = "RFC.md"

    if not os.path.exists(input_file):
        return

    with open(input_file, "r") as f:
        content = f.read()
    
    # Limpieza del plan: Capturamos lo relevante para no saturar el contexto de la IA
    important_lines = []
    for line in content.split('\n'):
        if "+" in line and ":" in line: # Cambios que se añaden
            important_lines.append(line.strip())
    
    clean_plan = "\n".join(important_lines)[:1500]

    # PROMPT ESTRATÉGICO PARA GERENCIA
    prompt = f"""<|system|>
Eres un Ingeniero de Infraestructura Senior. Tu tarea es redactar un "Request for Change" (RFC) profesional en ESPAÑOL basado en un plan de Terraform.
Usa un tono formal. Estructura la información en una tabla comparativa y secciones de riesgo.
<|user|>
Analiza este plan de Terraform y genera el RFC:
{clean_plan}

REGLAS DE FORMATO:
1. Título: # 📑 RFC: Despliegue de Infraestructura PoC
2. Incluye una Tabla con: | Recurso | Acción | Detalle Técnico |
3. Incluye una sección de "Impacto y Riesgo" breve.
<|assistant|>"""

    payload = {
        "model": "tinyllama",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2, # Baja temperatura para mayor consistencia
            "num_predict": 500,
            "top_p": 0.9
        }
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=180)
        result = response.json().get("response", "Error al procesar el resumen.")
        
        with open(output_file, "w", encoding="utf-8") as f:
            # No agregamos el título aquí porque ya lo pedimos en el prompt para que sea parte del estilo
            f.write(result.strip())
            
    except Exception as e:
        with open(output_file, "w") as f:
            f.write(f"# ❌ Error en Generación de RFC\n\nDetalle: {str(e)}")

if __name__ == "__main__":
    generate_rfc()