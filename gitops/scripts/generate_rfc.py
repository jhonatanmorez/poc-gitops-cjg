import requests
import os
import yaml

def generate_rfc():
    tf_file = "tf.txt"
    ansible_file = "gitops/ansible/playbook.yml"
    output_file = "RFC.md"

    # --- EXTRACCIÓN Y LIMPIEZA DE DATOS ---
    tf_data = "Actualización de recursos existentes"
    if os.path.exists(tf_file):
        with open(tf_file, "r") as f:
            lines = f.readlines()
            # Filtramos solo lo relevante para humanos
            cambios = [l.strip() for l in lines if "+" in l and "resource" in l]
            if cambios: tf_data = f"Despliegue de {len(cambios)} nuevos componentes de infraestructura."

    ansible_data = "Optimización de servicios"
    if os.path.exists(ansible_file):
        ansible_data = "Configuración automatizada de servicios web y endurecimiento de seguridad (Hardening)."

    # --- PROMPT GERENCIAL (Diseñado para TinyLlama) ---
    prompt = f"""<|system|>
Eres un Ingeniero Cloud Senior redactando un RFC para la junta directiva. No uses código técnico (+ o resource). Usa lenguaje de negocios.
<|user|>
DATOS:
Terraform: {tf_data}
Ansible: {ansible_data}

Escribe el RFC con este formato exacto:
# 📑 SOLICITUD DE CAMBIO (RFC): DESPLIEGUE DE INFRAESTRUCTURA

## 📋 1. RESUMEN EJECUTIVO
Escribe 2 frases sobre la mejora de disponibilidad y escalabilidad del servicio.

## 🛠 2. DETALLE DE IMPLEMENTACIÓN
| Capa | Acción Realizada | Beneficio de Negocio |
| :--- | :--- | :--- |
| Infraestructura | {tf_data} | Continuidad operativa |
| Configuración | {ansible_data} | Estandarización de servicios |

## 🛡 3. ANÁLISIS DE RIESGO
- **Nivel:** Mínimo.
- **Control:** Validado mediante pruebas automatizadas en CI/CD.

## 🔄 4. PLAN DE RETORNO (ROLLBACK)
Restauración inmediata del estado anterior mediante GitOps en caso de anomalía.
<|assistant|>"""

    payload = {
        "model": "tinyllama",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 700}
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        result = response.json().get("response", "").strip()
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_rfc()