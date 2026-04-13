import requests
import os
import sys

def generate_rfc():
    input_file = "tf.txt"
    output_file = "RFC.md"

    # 1. Verificar si existe el plan de Terraform
    if not os.path.exists(input_file):
        print(f"Error: No se encontró el archivo {input_file}")
        with open(output_file, "w") as f:
            f.write("# RFC Error\nNo se encontró el plan de Terraform para analizar.")
        return

    # 2. Leer y filtrar el plan (Limpieza de ruido para la IA)
    with open(input_file, "r") as f:
        lines = f.readlines()
    
    # Filtramos solo cambios relevantes para no saturar la CPU
    filtered_changes = [line.strip() for line in lines if any(x in line for x in ["+", "-", "~", "resource", "instance_type"])]
    clean_plan = "\n".join(filtered_changes)[:1200] 

    # 3. Prompt optimizado para respuesta en ESPAÑOL
    # Usamos instrucciones claras para que el modelo no se confunda
    prompt = f"""Genera un documento RFC (Request for Comments) breve en español.
Contexto: Terraform aplicará los siguientes cambios en la infraestructura:
{clean_plan}

Instrucciones:
- Título: Actualización de Infraestructura
- Secciones: Descripción, Impacto, Riesgos.
- Idioma: Español.
- Sé conciso y técnico.
Respuesta:"""

    # 4. Configuración de la petición a Ollama
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "tinyllama",
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 300,    # Un poco más de margen para el español
            "temperature": 0.2,    # Baja temperatura para evitar alucinaciones
            "top_p": 0.9
        }
    }

    print(f"Enviando solicitud a Ollama (TinyLlama) en español...")
    
    try:
        # Timeout de conexión: 10s, Timeout de lectura: 180s (3 min)
        response = requests.post(url, json=payload, timeout=(10, 180))
        response.raise_for_status()
        
        rfc_content = response.json().get("response", "No se recibió respuesta de la IA.")

        # 5. Escribir el resultado con encabezado en español
        with open(output_file, "w") as f:
            f.write("# Solicitud de Comentarios (RFC) - Autogenerado\n")
            f.write(rfc_content)
        
        print(f"RFC generado exitosamente en español en {output_file}")

    except requests.exceptions.Timeout:
        error_msg = "Error: Tiempo de espera agotado (Timeout)."
        print(error_msg)
        with open(output_file, "w") as f:
            f.write(f"# RFC (Generación fallida)\n{error_msg}")
            
    except Exception as e:
        error_msg = f"Error inesperado: {str(e)}"
        print(error_msg)
        with open(output_file, "w") as f:
            f.write(f"# RFC (Generación fallida)\nOcurrió un error al procesar la solicitud.")

if __name__ == "__main__":
    generate_rfc()