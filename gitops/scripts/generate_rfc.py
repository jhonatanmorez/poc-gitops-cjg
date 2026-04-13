import requests

tf = open("tf.txt").read()

prompt = f"""
Eres arquitecto cloud. Genera RFC profesional:

{tf}

Incluye:
- descripcion
- impacto
- riesgo
- rollback
"""

r = requests.post(
 "http://localhost:11434/api/generate",
 json={"model":"mistral","prompt":prompt,"stream":False}
)

open("RFC.md","w").write(r.json()["response"])