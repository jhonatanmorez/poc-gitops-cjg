import requests

tf = open("tf.txt").read()

prompt = f"""
Analiza este terraform plan y genera un RFC profesional:

{tf}
"""

r = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }
)

open("RFC.md","w").write(r.json()["response"])