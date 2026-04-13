import requests
import os

def generate_rfc():
    input_file = "tf.txt"
    output_file = "RFC.md"

    if not os.path.exists(input_file):
        return

    with open(input_file, "r") as f:
        content = f.read()
    
    # BUSQUEDA QUIRÚRGICA: 
    # Extraemos solo las líneas que realmente nos dicen qué se va a crear.
    important_lines = []
    for line in content.split('\n'):
        if "resource" in line or "will be created" in line or "+" in line:
            if "known after apply" not in line: # Quitamos el ruido de IDs desconocidos
                important_lines.append(line.strip())
    
    clean_plan = "\n".join(important_lines)[:1000]

    # PROMPT DE ROL DE INGENIERO:
    # Le damos un ejemplo de CÓMO queremos que responda (Few-Shot Prompting)
    prompt = f"""<|system|>
Eres un bot que resume planes de Terraform en español. Sé breve y directo. 
No expliques conceptos técnicos. No digas "Este RFC describe...".
Ejemplo de respuesta:
- Se creará una instancia EC2 tipo t3.micro.
- Se usará la AMI ami-04680790a315cd58d.
- Etiquetas: Name=web01, Env=dev.
<|user|>
Resume estos cambios de Terraform:
{clean_plan}
<|assistant|>"""

    payload = {
        "model": "tinyllama",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 200,
            "stop": ["<|user|>", "<|system|>"] # Evitamos que la IA siga hablando sola
        }
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        result = response.json().get("response", "Error al procesar")
        
        with open(output_file, "w") as f:
            f.write("# 🚀 Resumen de Cambios de Infraestructura\n\n")
            f.write(result.strip())
    except Exception as e:
        with open(output_file, "w") as f:
            f.write(f"Error: {str(e)}")

if __name__ == "__main__":
    generate_rfc()