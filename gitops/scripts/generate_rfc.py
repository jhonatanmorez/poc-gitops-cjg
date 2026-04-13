import requests
import os

# 1. Verificar el archivo de Terraform
if not os.path.exists("tf.txt"):
    with open("RFC.md", "w") as f:
        f.write("# RFC Error\nNo se encontró el plan de Terraform.")
    exit(0)

tf_content = open("tf.txt").read()

# 2. Prompt optimizado para un modelo pequeño
prompt = f"""Generate a professional RFC (Request for Comments) based on this Terraform plan:
{tf_content}

Include sections: Description, Impact, Risks, and Rollback.
Respond only with the RFC content in Markdown format."""

# 3. Petición a Ollama usando tinyllama
try:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "tinyllama", 
            "prompt": prompt, 
            "stream": False
        },
        timeout=180 # TinyLlama debería responder en menos de 1 minuto
    )
    response.raise_for_status()
    rfc_text = response.json().get("response", "No se generó contenido.")

    # 4. Guardar resultado
    with open("RFC.md", "w") as f:
        f.write(rfc_text)
    print("RFC generado correctamente con TinyLlama.")

except Exception as e:
    print(f"Error: {e}")
    with open("RFC.md", "w") as f:
        f.write("# RFC (Generación fallida)\nOcurrió un error con la IA local.")