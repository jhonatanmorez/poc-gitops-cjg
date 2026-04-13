import requests
import os

print("Cargando archivo tf.txt...")
if not os.path.exists("tf.txt"):
    print("ERROR: tf.txt no encontrado")
    exit(1)

tf = open("tf.txt").read()
prompt = f"Eres arquitecto cloud. Genera RFC profesional:\n{tf}\nIncluye: descripcion, impacto, riesgo, rollback"

print("Enviando petición a Ollama (esto puede tardar)...")
try:
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt, "stream": False},
        timeout=300 # 5 minutos máximo
    )
    r.raise_for_status()
    
    print("Respuesta recibida. Escribiendo RFC.md...")
    with open("RFC.md", "w") as f:
        f.write(r.json()["response"])
    print("Proceso completado.")

except Exception as e:
    print(f"ERROR: {e}")
    with open("RFC.md", "w") as f:
        f.write("# RFC Error\nNo se pudo generar el RFC por timeout o error de IA.")