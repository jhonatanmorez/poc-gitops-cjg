import requests
import os
import yaml

def generate_rfc():
    tf_file = "tf.txt"
    ansible_file = "gitops/ansible/playbook.yml"
    output_file = "RFC.md"

    # --- 1. PROCESAR TERRAFORM ---
    tf_summary = "Infraestructura sin cambios (Estado Sincronizado)."
    if os.path.exists(tf_file):
        with open(tf_file, "r") as f:
            lines = f.readlines()
            changes = [l.strip() for l in lines if ("+" in l or "~" in l or "-" in l) and "resource" in l]
            if changes:
                tf_summary = " | ".join(changes[:5])

    # --- 2. PROCESAR ANSIBLE ---
    ansible_summary = "Validación de configuración estándar."
    if os.path.exists(ansible_file):
        try:
            with open(ansible_file, "r") as f:
                playbook = yaml.safe_load(f)
                tasks = [t.get('name', 'Configuración') for play in playbook for t in play.get('tasks', [])]
                ansible_summary = " -> ".join(tasks[:5])
        except:
            ansible_summary = "Instalación de servicios y hardening."

    # --- 3. PROMPT OPTIMIZADO PARA TINYLLAMA ---
    # Usamos una estructura rígida para evitar que la IA alucine
    prompt = f"""<|system|>
Eres un Arquitecto de Soluciones Senior. Escribe un RFC técnico profesional.
<|user|>
DATOS TÉCNICOS:
Terraform: {tf_summary}
Ansible: {ansible_summary}

TAREA: Escribe el RFC siguiendo este modelo:
# 📑 RFC: Actualización de Plataforma Cloud
## 📋 Resumen Ejecutivo
Cambios programados para mejorar la infraestructura y servicios.
## 🛠 Tabla de Cambios
| Capa | Acción | Detalle Técnico |
| :--- | :--- | :--- |
| Infraestructura | Aplicar | {tf_summary} |
| Configuración | Software | {ansible_summary} |
## 🛡 Riesgo
Bajo. Validado en pipeline de CI/CD.
## 🔄 Rollback
Reversión de commit y ejecución de terraform destroy/apply.
<|assistant|>
# 📑 RFC: Despliegue Automatizado"""

    payload = {
        "model": "tinyllama",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 600, "stop": ["<|user|>"]}
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        result = response.json().get("response", "").strip()
        
        # Fallback profesional si la IA no responde correctamente
        if len(result) < 50:
            result = f"# 📑 RFC: Reporte de Cambio\n\n## 📋 Resumen\nCambio automático.\n\n## 🛠 Detalles\n- **Terraform:** {tf_summary}\n- **Ansible:** {ansible_summary}"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_rfc()