import requests
import os
import yaml

def generate_rfc():
    tf_file = "tf.txt"
    ansible_file = "gitops/ansible/playbook.yml"
    output_file = "RFC.md"

    # --- 1. PREPARACIÓN DE DATOS (Limpieza extrema para TinyLlama) ---
    tf_summary = "Sin cambios (Infraestructura Estable)."
    if os.path.exists(tf_file):
        with open(tf_file, "r") as f:
            lines = f.readlines()
            # Capturamos solo la acción y el recurso (ej: + aws_instance.web)
            changes = [l.strip() for l in lines if ("+" in l or "~" in l or "-" in l) and "resource" in l]
            if changes:
                tf_summary = " | ".join(changes[:5]) # Limitamos a 5 cambios para no saturar la memoria del modelo

    ansible_summary = "Configuración base."
    if os.path.exists(ansible_file):
        try:
            with open(ansible_file, "r") as f:
                playbook = yaml.safe_load(f)
                tasks = [t.get('name', 'Tarea') for play in playbook for t in play.get('tasks', [])]
                ansible_summary = " -> ".join(tasks[:5])
        except:
            ansible_summary = "Instalación de servicios y hardening."

    # --- 2. EL PROMPT MAESTRO (Optimizado para modelos 1.1B) ---
    # Usamos un formato de "Completar la frase" que es donde TinyLlama brilla.
    prompt = f"""<|system|>
Eres un Ingeniero Cloud. Escribe un RFC técnico. Sé breve y usa tablas.
<|user|>
DATOS TÉCNICOS:
Terraform (Infraestructura): {tf_summary}
Ansible (Configuración): {ansible_summary}

TAREA: Escribe el RFC siguiendo este modelo exacto:
# 📑 RFC: Actualización de Plataforma
## 📋 Resumen
Se detallan cambios en recursos AWS y software.
## 🛠 Tabla de Cambios
| Capa | Acción | Detalle |
| :--- | :--- | :--- |
| Infra | Aplicar | {tf_summary} |
| Software | Configurar | {ansible_summary} |
## 🛡 Riesgo
Bajo. Cambios validados por pipeline.
<|assistant|>
# 📑 RFC: Despliegue Automatizado"""

    payload = {
        "model": "tinyllama",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,  # Casi 0 para que no invente palabras raras
            "top_p": 0.7,
            "num_predict": 500,
            "stop": ["<|user|>", "DATOS TÉCNICOS:"] # Para que no repita tus instrucciones
        }
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        result = response.json().get("response", "").strip()
        
        # Si la IA responde algo muy corto o vacío, usamos el formato profesional de respaldo
        if len(result) < 50:
            result = f"""# 📑 RFC: Reporte de Cambio de Infraestructura
## 📋 Resumen Ejecutivo
Validación de estado y aplicación de cambios mediante GitOps.

## 🛠 Tabla Detallada de Cambios
| Capa | Componente | Acción | Descripción |
| :--- | :--- | :--- | :--- |
| **Infraestructura** | Terraform | Sync | {tf_summary} |
| **Configuración** | Ansible | Deploy | {ansible_summary} |

## 🛡 Análisis de Riesgo
- **Impacto:** Controlado.
- **Rollback:** Revertir commit en rama principal."""

        # Escribimos el Markdown final
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
        print("✅ RFC Generado profesionalmente.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_rfc()