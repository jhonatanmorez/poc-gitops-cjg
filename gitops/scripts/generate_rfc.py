import os
import re
import logging
from datetime import datetime

# IA opcional
try:
    import torch
    from transformers import pipeline
    HAS_AI = True
except ImportError:
    HAS_AI = False

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

TF_PLAN_PATH = "gitops/terraform/environments/dev/tf.txt"
ANSIBLE_PATH = "gitops/ansible/playbook.yml"
OUTPUT_FILE = "gitops/terraform/environments/dev/RFC.md"

MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# -----------------------------
# 🔍 PARSER TERRAFORM AVANZADO
# -----------------------------
def parse_terraform(content):
    summary = {"add": 0, "change": 0, "destroy": 0, "resources": []}

    plan_match = re.search(r"Plan:\s(\d+)\sto add,\s(\d+)\sto change,\s(\d+)\sto destroy", content)
    if plan_match:
        summary["add"], summary["change"], summary["destroy"] = map(int, plan_match.groups())

    # detectar recursos
    for line in content.splitlines():
        if line.strip().startswith("#"):
            action = None
            if "will be created" in line:
                action = "CREATE"
            elif "will be destroyed" in line:
                action = "DELETE"
            elif "will be updated" in line:
                action = "UPDATE"

            if action:
                resource = line.split()[1]
                summary["resources"].append({"resource": resource, "action": action})

    return summary

# -----------------------------
# 🔍 PARSER ANSIBLE
# -----------------------------
def parse_ansible():
    if not os.path.exists(ANSIBLE_PATH):
        return "No se detectaron cambios en configuración OS"

    try:
        with open(ANSIBLE_PATH) as f:
            content = f.read()

        tasks = re.findall(r"- name:\s(.+)", content)
        return f"{len(tasks)} tareas detectadas: {', '.join(tasks[:3])}..."
    except:
        return "Configuración OS detectada"

# -----------------------------
# 📊 ANÁLISIS DE RIESGO
# -----------------------------
def calculate_risk(tf_summary):
    total = tf_summary["add"] + tf_summary["change"] + tf_summary["destroy"]

    if tf_summary["destroy"] > 0:
        return "ALTO", "Se eliminan recursos, posible impacto en disponibilidad"

    if total > 5:
        return "MEDIO", "Cambios múltiples en infraestructura"

    return "BAJO", "Cambios controlados y automatizados"

# -----------------------------
# 📄 TEMPLATE PROFESIONAL CAB
# -----------------------------
def build_static_rfc(tf_summary, ansible_summary):
    risk_level, risk_desc = calculate_risk(tf_summary)

    resources_detail = "\n".join(
        [f"- {r['action']}: {r['resource']}" for r in tf_summary["resources"][:10]]
    ) or "Sin detalle específico"

    return f"""
# 📑 RFC - REQUEST FOR CHANGE (CAB)

## 1. INFORMACIÓN GENERAL
- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- Tipo de cambio: Infraestructura como Código (IaC)
- Origen: GitOps Pipeline

---

## 2. RESUMEN EJECUTIVO
Se ejecutará un cambio automatizado en la infraestructura cloud y configuración del sistema operativo basado en repositorio Git.

---

## 3. DETALLE DEL CAMBIO

### 🌐 Infraestructura (Terraform)
- Recursos a crear: {tf_summary['add']}
- Recursos a modificar: {tf_summary['change']}
- Recursos a eliminar: {tf_summary['destroy']}

#### Recursos afectados:
{resources_detail}

### 🖥️ Configuración (Ansible)
{ansible_summary}

---

## 4. IMPACTO
- Impacto esperado: Bajo impacto en usuarios finales
- Tipo: Cambios automatizados y controlados
- Ventana: Deployment CI/CD

---

## 5. ANÁLISIS DE RIESGO
- Nivel: {risk_level}
- Descripción: {risk_desc}

---

## 6. PLAN DE IMPLEMENTACIÓN
1. Ejecución automática vía pipeline GitHub Actions
2. Aplicación de Terraform
3. Configuración mediante Ansible

---

## 7. PLAN DE ROLLBACK
- Reversión mediante rollback de commit en Git
- Ejecución de Terraform apply sobre estado anterior

---

## 8. VALIDACIÓN POST-CAMBIO
- Verificación de recursos en AWS
- Validación de servicios (ej: Nginx activo)
- Revisión de logs

---

## 9. APROBACIÓN
Este cambio requiere aprobación del CAB antes de ejecución en producción.

---
"""

# -----------------------------
# 🤖 IA MEJORADA
# -----------------------------
def generate_with_ai(tf_summary, ansible_summary):
    if not HAS_AI:
        return None

    try:
        logging.info("Generando RFC con TinyLlama...")

        pipe = pipeline(
            "text-generation",
            model=MODEL_ID,
            device_map="auto"
        )

        prompt = f"""
Eres un arquitecto cloud senior.

Genera un RFC profesional tipo CAB.

Datos:
Terraform: {tf_summary}
Ansible: {ansible_summary}

Incluye:
- resumen ejecutivo
- impacto
- riesgo
- rollback
- validación
"""

        output = pipe(prompt, max_new_tokens=500, temperature=0.2)
        return output[0]["generated_text"]

    except Exception as e:
        logging.error(f"Error IA: {e}")
        return None

# -----------------------------
# 🚀 MAIN
# -----------------------------
def generate_rfc():
    if not os.path.exists(TF_PLAN_PATH):
        logging.error("No existe tf.txt")
        return

    with open(TF_PLAN_PATH) as f:
        tf_content = f.read()

    tf_summary = parse_terraform(tf_content)
    ansible_summary = parse_ansible()

    total_changes = tf_summary["add"] + tf_summary["change"] + tf_summary["destroy"]

    if total_changes == 0:
        result = "# ✅ SIN CAMBIOS\nInfraestructura alineada con estado deseado."
    else:
        result = generate_with_ai(tf_summary, ansible_summary)

        if not result:
            logging.info("Usando RFC estático profesional")
            result = build_static_rfc(tf_summary, ansible_summary)

    with open(OUTPUT_FILE, "w") as f:
        f.write(result)

    logging.info(f"RFC generado: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_rfc()