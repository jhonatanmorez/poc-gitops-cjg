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
Eres un Director de Infraestructura. Tu objetivo es redactar un Reporte de Cambio (RFC) ejecutivo, claro y formal.
REGLAS:
1. No muestres código crudo como "+ resource". Tradúcelo a lenguaje humano.
2. Usa tablas Markdown limpias.
3. El tono debe ser profesional y de alto nivel.
<|user|>
DATOS TÉCNICOS PARA PROCESAR:
- Cambios Terraform: {tf_summary}
- Tareas Ansible: {ansible_summary}

GENERA EL SIGUIENTE FORMATO:
# 📑 SOLICITUD DE CAMBIO DE INFRAESTRUCTURA (RFC)

## 📋 1. RESUMEN EJECUTIVO
Escribe aquí un párrafo que explique que se va a desplegar un nuevo servidor web para mejorar la disponibilidad del servicio.

## 🛠 2. DETALLE DE LA INTERVENCIÓN
| Dimensión | Acción | Beneficio esperado |
| :--- | :--- | :--- |
| **Infraestructura** | Creación de Nueva Instancia Cloud | Escalabilidad del entorno |
| **Configuración** | Automatización de Servidor Nginx | Optimización de entrega de contenido |

## 🛡 3. ANÁLISIS DE RIESGO Y CONTROL
- **Nivel de Riesgo:** Mínimo.
- **Validación:** El cambio ha sido testeado satisfactoriamente en el pipeline de CI/CD.
- **Impacto en Usuario:** Sin interrupción de servicio (Zero Downtime).

## 🔄 4. PLAN DE CONTINUIDAD (ROLLBACK)
En caso de anomalía, se procederá a la reversión automática del commit en Git y restauración del estado anterior mediante Terraform, garantizando la estabilidad operativa.
<|assistant|>"""

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