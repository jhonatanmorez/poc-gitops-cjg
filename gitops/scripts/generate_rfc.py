import requests
import os
import yaml

def generate_rfc():
    tf_file = "tf.txt"
    ansible_file = "gitops/ansible/playbook.yml"
    output_file = "RFC.md"

    # --- 1. CAPTURA DE DATOS ---
    tf_summary = "Sin cambios detectados."
    if os.path.exists(tf_file):
        with open(tf_file, "r") as f:
            lines = f.readlines()
            changes = [l.strip() for l in lines if any(x in l for x in ["+", "~", "-"]) and "resource" in l]
            if changes:
                tf_summary = "\n".join(changes)

    ansible_summary = "No se detectaron tareas de configuración."
    if os.path.exists(ansible_file):
        try:
            with open(ansible_file, "r") as f:
                playbook = yaml.safe_load(f)
                summary_tasks = []
                for play in playbook:
                    t_names = [t.get('name', 'Tarea técnica') for t in play.get('tasks', [])]
                    summary_tasks.append(f"Servicio: {play.get('name')} | Tareas: {', '.join(t_names)}")
                ansible_summary = "\n".join(summary_tasks)
        except:
            ansible_summary = "Configuración estándar de servidor."

    # --- 2. PROMPT OPTIMIZADO PARA MODELOS PEQUEÑOS ---
    # Eliminamos ambigüedades para que la IA no repita el prompt
    prompt = f"""<|system|>
Eres un Ingeniero Cloud que redacta Reportes de Cambio (RFC). 
TU TAREA: Generar un reporte técnico basado en los datos proporcionados.
REGLA: No repitas las instrucciones. Solo entrega el reporte final en Markdown.
<|user|>
DATOS TÉCNICOS:
Terraform: {tf_summary}
Ansible: {ansible_summary}

GENERA EL SIGUIENTE FORMATO:
1. Título (Deduce un nombre profesional)
2. Resumen Ejecutivo
3. Tabla de Cambios (Capa | Componente | Acción | Propósito)
4. Análisis de Riesgo
5. Plan de Rollback
<|assistant|>"""

    payload = {
        "model": "tinyllama",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1, # Menor temperatura = menos errores/alucinaciones
            "num_predict": 800,
            "stop": ["<|user|>", "<|system|>", "DATOS TÉCNICOS:"] # Evita que la IA siga escribiendo
        }
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=180)
        result = response.json().get("response", "").strip()
        
        # Validación: Si la IA devuelve basura, usamos un fallback profesional
        if len(result) < 50 or "ESTRUCTURO REQUERIADO" in result:
             result = generate_fallback_rfc(tf_summary, ansible_summary)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"✅ RFC generado exitosamente.")
    except Exception as e:
        print(f"❌ Error: {e}")

def generate_fallback_rfc(tf, ans):
    """Función de respaldo por si la IA falla (Seguridad Enterprise)"""
    return f"""# 📑 RFC: Actualización de Infraestructura y Servicios
## 📋 Resumen Ejecutivo
Se informa la validación de infraestructura y la aplicación de configuraciones de software automatizadas.

## 🛠 Tabla Detallada de Cambios
| Capa | Componente | Acción | Propósito |
| :--- | :--- | :--- | :--- |
| Infraestructura | Cloud Resources | Validar | {tf} |
| Configuración | Ansible Playbook | Ejecutar | {ans} |

## 🛡 Evaluación de Impacto y Riesgo
- **Impacto:** Bajo. Se aplican configuraciones sobre instancias existentes.
- **Riesgo:** Mínimo. Proceso idempotente.

## 🔄 Procedimiento de Reversión
1. Ejecutar Terraform Destroy si es necesario.
2. Restaurar Snapshot de la instancia previa al Playbook."""

if __name__ == "__main__":
    generate_rfc()