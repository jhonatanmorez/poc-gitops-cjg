import os
import re
import logging
import torch
from transformers import pipeline

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Rutas y Configuración
TF_PLAN_PATH = "gitops/terraform/environments/dev/tf.txt"
OUTPUT_FILE = "RFC.md"
MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

def parse_terraform_summary(content):
    """Extrae el resumen del plan de Terraform."""
    summary_pattern = r"Plan: (\d+) to add, (\d+) to change, (\d+) to destroy"
    match = re.search(summary_pattern, content)
    if match:
        add, change, destroy = match.groups()
        return {
            "total": int(add) + int(change) + int(destroy),
            "detail": f"{add} adiciones, {change} cambios, {destroy} eliminaciones"
        }
    cambios = [l for l in content.split('\n') if "resource" in l and any(c in l for c in ["+", "-", "~"])]
    return {"total": len(cambios), "detail": f"{len(cambios)} recursos modificados"}

def generate_rfc_local(tf_data, ansible_data):
    """Genera el RFC usando TinyLlama localmente sin Ollama."""
    logging.info("Cargando TinyLlama en memoria para generación local...")
    try:
        # Inicializar el pipeline de texto
        pipe = pipeline(
            "text-generation", 
            model=MODEL_ID, 
            torch_dtype=torch.bfloat16, 
            device_map="auto"
        )

        prompt = f"""<|system|>
Eres un Director de Infraestructura Senior. Redacta una Solicitud de Cambio (RFC) formal para un comité CAB.
Enfócate en valor de negocio, riesgo y continuidad. No uses bloques de código.
<|user|>
DATOS:
- Terraform: {tf_data}
- Ansible: {ansible_data}

FORMATO REQUERIDO:
# 📑 RFC: ACTUALIZACIÓN DE INFRAESTRUCTURA Y SEGURIDAD
## 1. RESUMEN DEL CAMBIO
## 2. JUSTIFICACIÓN DE NEGOCIO
## 3. DETALLE DE IMPLEMENTACIÓN (Capa | Acción | Impacto)
## 4. ANÁLISIS DE RIESGO
## 5. PLAN DE RETORNO (ROLLBACK)
<|assistant|>"""

        outputs = pipe(
            prompt, 
            max_new_tokens=600, 
            do_sample=True, 
            temperature=0.2, 
            top_k=50, 
            top_p=0.95,
            repetition_penalty=1.2
        )
        
        # Extraer solo la respuesta de la IA
        full_text = outputs[0]["generated_text"]
        result = full_text.split("<|assistant|>")[-1].strip()
        return result

    except Exception as e:
        logging.error(f"Error en la generación local: {e}")
        return None

def get_static_template(tf_data, ansible_data):
    """RFC Profesional de respaldo (Fallback)."""
    return f"""# 📑 RFC: ACTUALIZACIÓN DE INFRAESTRUCTURA (REPORTE ESTÁNDAR)

## 1. RESUMEN DEL CAMBIO
Actualización programada de componentes de infraestructura cloud y perfiles de seguridad de sistema.

## 2. JUSTIFICACIÓN DE NEGOCIO
Garantizar la paridad entre el código del repositorio y el entorno de producción, mejorando la postura de seguridad.

## 3. DETALLE DE IMPLEMENTACIÓN
| Capa | Acción Realizada | Impacto |
| :--- | :--- | :--- |
| Cloud | {tf_data} | Continuidad de Servicio |
| OS | {ansible_data} | Cumplimiento de Hardening |

## 4. ANÁLISIS DE RIESGO
- **Nivel:** Bajo (Cambios validados en pipeline CI/CD).
- **Control:** Verificación de integridad post-despliegue.

## 5. PLAN DE RETORNO (ROLLBACK)
Reversión automática mediante GitOps al commit anterior en caso de degradación de servicio.

---
*Generado mediante plantilla de contingencia.*"""

def generate_rfc():
    if not os.path.exists(TF_PLAN_PATH):
        logging.error(f"No se encontró el archivo: {TF_PLAN_PATH}")
        return

    with open(TF_PLAN_PATH, "r", encoding="utf-8") as f:
        tf_content = f.read()

    summary = parse_terraform_summary(tf_content)
    
    if summary["total"] == 0 or "No changes" in tf_content:
        logging.info("Sin cambios. Generando reporte de cumplimiento.")
        result = "# 📑 REPORTE DE ESTADO: INFRAESTRUCTURA SINCRONIZADA\n\nNo se detectaron desviaciones. El entorno cumple con la política definida."
    else:
        logging.info(f"Procesando {summary['total']} cambios...")
        tf_data = summary["detail"]
        ansible_data = "Configuración de servicios y hardening de seguridad"

        # Generación local con TinyLlama
        result = generate_rfc_local(tf_data, ansible_data)
        
        # Fallback si falla la carga del modelo
        if not result:
            result = get_static_template(tf_data, ansible_data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(result)
    logging.info(f"✅ RFC profesional generado en {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_rfc()