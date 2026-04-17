import os
import re
import logging

# Intentar importar librerías de IA. Si fallan, el script NO se rompe.
try:
    import torch
    from transformers import pipeline
    HAS_AI_LIBS = True
except ImportError:
    HAS_AI_LIBS = False

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

TF_PLAN_PATH = "gitops/terraform/environments/dev/tf.txt" # Simplificado para que coincida con tu comando 'cp'
OUTPUT_FILE = "gitops/terraform/environments/dev/RFC.md"
MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

def parse_terraform_summary(content):
    summary_pattern = r"Plan: (\d+) to add, (\d+) to change, (\d+) to destroy"
    match = re.search(summary_pattern, content)
    if match:
        add, change, destroy = match.groups()
        return {"total": int(add) + int(change) + int(destroy), "detail": f"{add} adiciones, {change} cambios, {destroy} eliminaciones"}
    cambios = [l for l in content.split('\n') if "resource" in l and any(c in l for c in ["+", "-", "~"])]
    return {"total": len(cambios), "detail": f"{len(cambios)} recursos modificados"}

def get_static_template(tf_data, ansible_data):
    """RFC Profesional estático para el CAB."""
    return f"""# 📑 RFC: ACTUALIZACIÓN DE INFRAESTRUCTURA (REPORTE CAB)

## 1. RESUMEN DEL CAMBIO
Despliegue automatizado de infraestructura cloud y perfiles de configuración de seguridad.

## 2. JUSTIFICACIÓN DE NEGOCIO
Asegurar que la infraestructura en la nube refleje los cambios aprobados en el repositorio de GitOps.

## 3. DETALLE DE IMPLEMENTACIÓN
| Capa | Acción | Impacto |
| :--- | :--- | :--- |
| Cloud | {tf_data} | Continuidad |
| OS | {ansible_data} | Seguridad |

## 4. ANÁLISIS DE RIESGO
- **Nivel:** Bajo. Validado en pipeline CI/CD.
- **Plan de Retorno:** Reversión vía GitOps mediante rollback de commit.
"""

def generate_rfc_local(tf_data, ansible_data):
    if not HAS_AI_LIBS:
        return None
    try:
        logging.info("Generando RFC con TinyLlama nativo...")
        pipe = pipeline("text-generation", model=MODEL_ID, torch_dtype=torch.bfloat16, device_map="auto")
        prompt = f"<|system|>Director de Infraestructura Senior.<|user|>Escribe un RFC para: {tf_data} y {ansible_data}<|assistant|>"
        outputs = pipe(prompt, max_new_tokens=400, do_sample=True, temperature=0.2)
        return outputs[0]["generated_text"].split("<|assistant|>")[-1].strip()
    except Exception as e:
        logging.error(f"IA falló por recursos: {e}")
        return None

def generate_rfc():
    if not os.path.exists(TF_PLAN_PATH):
        logging.error(f"No existe {TF_PLAN_PATH}")
        return

    with open(TF_PLAN_PATH, "r") as f:
        tf_content = f.read()

    summary = parse_terraform_summary(tf_content)
    tf_data = summary["detail"]
    ansible_data = "Hardening de seguridad Nginx"

    if summary["total"] == 0:
        result = "# 📑 REPORTE: SIN CAMBIOS\nInfraestructura sincronizada."
    else:
        # Intentar con IA, si falla (por librerías o RAM), usar el template
        result = generate_rfc_local(tf_data, ansible_data)
        if not result:
            logging.info("Usando plantilla profesional estática.")
            result = get_static_template(tf_data, ansible_data)

    with open(OUTPUT_FILE, "w") as f:
        f.write(result)
    logging.info(f"✅ RFC generado en {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_rfc()