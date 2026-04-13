import requests
import os
import yaml

def generate_rfc():
    tf_file = "tf.txt"
    ansible_file = "gitops/ansible/playbook.yml"
    output_file = "RFC.md"

    # --- 1. CAPTURA DINÁMICA DE TERRAFORM ---
    # En lugar de buscar un nombre, capturamos la acción (+, -, ~) y el tipo de recurso
    tf_summary = ""
    if os.path.exists(tf_file):
        with open(tf_file, "r") as f:
            lines = f.readlines()
            # Capturamos bloques que indiquen cambios estructurales
            relevant_changes = [l.strip() for l in lines if any(x in l for x in ["+", "~", "-"]) and "resource" in l]
            
            if not relevant_changes:
                tf_summary = "ESTADO: Sin cambios en la infraestructura actual (Sincronizada)."
            else:
                tf_summary = "\n".join(relevant_changes)

    # --- 2. CAPTURA DINÁMICA DE ANSIBLE ---
    # Extraemos metadatos del playbook sin asumir qué software se instala
    ansible_summary = ""
    if os.path.exists(ansible_file):
        try:
            with open(ansible_file, "r") as f:
                playbook = yaml.safe_load(f)
                summary_tasks = []
                for play in playbook:
                    play_name = play.get('name', 'Configuración de Host')
                    tasks = [t.get('name', 'Tarea sin nombre') for t in play.get('tasks', [])]
                    summary_tasks.append(f"Play: {play_name} -> Tareas: {', '.join(tasks)}")
                ansible_summary = "\n".join(summary_tasks)
        except Exception as e:
            ansible_summary = f"Error leyendo configuración de Ansible: {str(e)}"

    # --- 3. PROMPT DE INGENIERÍA DE CONTEXTO ---
    # Le pedimos a la IA que sea ella quien nombre los componentes basándose en el código
    prompt = f"""<|system|>
Eres un Arquitecto de Soluciones Senior especializado en Auditoría de Cambios. 
Tu tarea es redactar un "Request for Change" (RFC) basado en el código técnico proporcionado.
REGLAS:
- Identifica DINÁMICAMENTE los nombres de servidores, redes y servicios.
- Si no hay cambios en la infraestructura, resalta que el cambio es de CONFIGURACIÓN de software.
- Usa un lenguaje corporativo de alto nivel.
<|user|>
CONSTRÚYEME UN RFC PROFESIONAL BASADO EN ESTO:

[DATOS DE INFRAESTRUCTURA - TERRAFORM]
{tf_summary}

[DATOS DE CONFIGURACIÓN - ANSIBLE]
{ansible_summary}

ESTRUCTURA REQUERIDA:
1. # 📑 RFC: [Deduce un título basado en los cambios detectados]
2. ## 📋 Resumen Ejecutivo
3. ## 🛠 Tabla Detallada de Cambios (Capa, Componente, Acción, Propósito)
4. ## 🛡 Evaluación de Impacto y Riesgo
5. ## 🔄 Procedimiento de Reversión (Rollback)
<|assistant|>"""

    payload = {
        "model": "tinyllama", # O el modelo que prefieras (mistral, llama3, etc)
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2, # Un poco de creatividad pero controlada
            "num_predict": 900
        }
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=180)
        result = response.json().get("response", "Error: No se pudo generar el contenido dinámico.")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.strip())
        print(f"✅ RFC Dinámico generado en {output_file}")
    except Exception as e:
        with open(output_file, "w") as f:
            f.write(f"# Error Crítico en Generador de RFC\n{str(e)}")

if __name__ == "__main__":
    generate_rfc()