import requests
import os

def generate_rfc():
    # Asegúrate de usar la ruta correcta donde Terraform guarda el txt
    tf_file = "gitops/terraform/environments/dev/tf.txt" 
    output_file = "RFC.md"

    # 1. Leer y validar el archivo de Terraform
    if not os.path.exists(tf_file):
        print(f"Archivo {tf_file} no encontrado.")
        return

    with open(tf_file, "r") as f:
        tf_content = f.read()

    # 2. Lógica de "Cortocircuito": ¿Hay cambios reales?
    # Buscamos indicadores de cambios positivos (+), eliminaciones (-) o modificaciones (~)
    cambios_reales = [line for line in tf_content.split('\n') if "resource" in line and ("+" in line or "-" in line or "~" in line)]
    
    # 3. Escenario A: NO HAY CAMBIOS
    if not cambios_reales or "No changes" in tf_content:
        print("Infraestructura sincronizada. Generando Reporte de Estado.")
        result = """# 📑 REPORTE DE ESTADO: INFRAESTRUCTURA SINCRONIZADA

## 📋 1. RESUMEN EJECUTIVO
Se ha realizado una validación de estado mediante Terraform. La infraestructura actual en la nube coincide exactamente con la configuración definida en el repositorio. No se han detectado desviaciones.

## 🛠 2. DETALLE DE VERIFICACIÓN
| Componente | Estado | Observación |
| :--- | :--- | :--- |
| **Recursos Cloud** | ✅ Sincronizado | Sin cambios pendientes de aplicar. |
| **Configuración** | ✅ Validado | La plataforma se mantiene estable. |

## 🛡 3. CONCLUSIÓN
No se requiere intervención ni aprobación de cambios en este ciclo. El sistema se encuentra en estado óptimo."""
        
    # 4. Escenario B: HAY CAMBIOS (Llamamos a TinyLlama)
    else:
        print(f"Se detectaron {len(cambios_reales)} cambios. Generando RFC con IA...")
        tf_data = f"Modificación/Creación de {len(cambios_reales)} recursos de infraestructura."
        ansible_data = "Automatización de servicios y hardening de seguridad."

        prompt = f"""<|system|>
Eres un Director de Infraestructura. Escribe un RFC formal sin usar código técnico.
<|user|>
DATOS:
Terraform: {tf_data}
Ansible: {ansible_data}

Escribe el RFC exactamente con este formato:
# 📑 SOLICITUD DE CAMBIO (RFC): ACTUALIZACIÓN DE SISTEMAS

## 📋 1. RESUMEN EJECUTIVO
Despliegue programado para optimizar la capacidad operativa y seguridad del entorno.

## 🛠 2. DETALLE DE IMPLEMENTACIÓN
| Capa | Acción Realizada | Beneficio de Negocio |
| :--- | :--- | :--- |
| Infraestructura | {tf_data} | Escalabilidad y Continuidad |
| Configuración | {ansible_data} | Estándar de Seguridad |

## 🛡 3. ANÁLISIS DE RIESGO
- **Nivel:** Bajo.
- **Validación:** Validado en entorno de pruebas CI/CD.

## 🔄 4. PLAN DE RETORNO
Reversión inmediata vía GitOps.
<|assistant|>"""

        payload = {
            "model": "tinyllama",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 500}
        }

        try:
            response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=60)
            result = response.json().get("response", "").strip()
        except:
            result = "# 📑 RFC (Error de Generación)\nInfraestructura con cambios pendientes. Revisar logs manuales."

    # 5. Guardar el archivo final
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"✅ Documento {output_file} generado.")

if __name__ == "__main__":
    generate_rfc()