import requests
import os

def generate_rfc():
    input_file = "tf.txt"
    output_file = "RFC.md"

    if not os.path.exists(input_file):
        with open(output_file, "w") as f:
            f.write("# RFC Error\nNo se encontró el plan de Terraform.")
        return

    # Leer y filtrar: buscamos líneas con (conocido después de aplicar) o cambios directos
    with open(input_file, "r") as f:
        lines = f.readlines()
    
    # Filtro más agresivo para capturar la esencia del cambio
    changes = [l.strip() for l in lines if "+" in l or "-" in l or "~" in l or "resource" in l]
    clean_plan = "\n".join(changes)[:1500] 

    # PROMPT AGRESIVO: Le decimos que NO defina qué es un RFC, sino que lo ESCRIBA
    prompt = f"""[INST] Eres un ingeniero DevOps. Analiza estos cambios de Terraform y escribe un RFC técnico breve.
NO expliques qué es un RFC. NO des definiciones.
SOLO escribe el contenido del RFC basado en estos datos:
{clean_plan}

Formato requerido:
# RFC: Actualización de Infraestructura
## Descripción de los cambios:
(Analiza aquí qué recursos se crean o modifican)
## Impacto:
(Qué infraestructura se verá afectada)
## Riesgos:
(Riesgos de este cambio)
[/INST]"""

    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "tinyllama",
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 400,
            "temperature": 0.1, # Casi 0 para que no invente y se ciña a los datos
            "top_p": 0.9
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=(10, 180))
        response.raise_for_status()
        rfc_content = response.json().get("response", "")

        with open(output_file, "w") as f:
            f.write(rfc_content)
        
    except Exception as e:
        with open(output_file, "w") as f:
            f.write(f"# Error en IA\n{str(e)}")

if __name__ == "__main__":
    generate_rfc()