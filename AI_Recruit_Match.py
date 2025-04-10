# ============================
# APP EN STREAMLIT
# ============================
import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import json
import io
import requests

# API KEY y URL (se puede ocultar mejor con secrets en producción)
api_key = st.secrets["API_KEY"]
api_url = "https://openrouter.ai/api/v1/chat/completions"
st.set_page_config(page_title="Análisis de Candidato IA", layout="wide")

# ============================
# 🧠 TÍTULO Y DESCRIPCIÓN
# ============================
st.title("🤖 AI_Recruit_Match.py")
st.markdown("""
Esta aplicación permite analizar un CV comparándolo con los requerimientos de un puesto IT.
Subí el PDF del candidato, ingresá los requerimientos del rol y obtené:
- 📊 Una tabla comparativa con cumplimiento por requerimiento
- 🧠 Un análisis técnico y recomendación final
- 💾 Una descarga en Excel con el resumen completo
""")

st.markdown("---")

# ============================
# 📥 INPUT DEL USUARIO
# ============================
nombre_candidato = st.text_input("🧑 Nombre del Candidato")
rol_postulado = st.text_input("🎯 Rol al que Aplica")
rol_experiencia = st.text_input("💼 Rol con experiencia previa")
job_requirements = st.text_area("📌 Ingresá los requerimientos del puesto")
cv_file = st.file_uploader("📄 Subí el CV del candidato en PDF", type=["pdf"])

if st.button("🔍 Analizar Candidato") and cv_file and job_requirements:
    with st.spinner("Analizando CV..."):
        # ============================
        # 🔎 Lectura del CV
        # ============================
        doc = fitz.open(stream=cv_file.read(), filetype="pdf")
        cv_text = "".join(page.get_text() for page in doc)

        with st.expander("📄 Texto extraído del CV (debug)"):
            st.text(cv_text[:2000])  # Primeros caracteres del CV

        # ============================
        # 🤖 Prompt Comparación
        # ============================
        prompt_comparacion = f"""
Sos una reclutadora IT con experiencia. Analizá si el candidato encaja en el puesto a partir de los requerimientos y el CV.

✅ Devolvé SOLO una lista en formato JSON válido, sin explicaciones ni texto adicional. Formato exacto:
[
  {{
    "Requerimiento": "...",
    "Experiencia del Candidato": "...",
    "Años de Experiencia": "...",
    "Cumplimiento": "✔ Cumple" o "❌ No cumple",
    "Observaciones": "..."
  }}
]

📌 Requerimientos del Rol:
{job_requirements}

📌 CV:
{cv_text}
"""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # 🚨 CORRECTO PARA OPENROUTER
        data = {
            "model": "mistralai/mixtral-8x7b",
            "messages": [{"role": "user", "content": prompt_comparacion}]
        }

        response = requests.post(api_url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']

            with st.expander("🧾 Respuesta completa de la IA (debug)"):
                st.text(content)

            try:
                comparacion = json.loads(content)
                df = pd.DataFrame(comparacion)
                st.subheader("📊 Comparativa de Requerimientos vs Experiencia del Candidato")
                st.dataframe(df, use_container_width=True)

                # ============================
                # 🧠 Análisis técnico
                # ============================
                tabla_texto = df.to_string(index=False)
                prompt_analisis = f"""
Sos una reclutadora especializada en IT. A continuación recibirás una tabla comparativa entre los requisitos del puesto y la experiencia del candidato.

📊 Tabla:
{tabla_texto}

🧠 Redactá un análisis técnico claro sobre si el perfil cumple el total de los requerimientos.
🧭 Brindá una recomendación como reclutadora: ¿Es ideal? ¿Necesita formación? ¿No encaja?
👉 Finalizá con una sugerencia concreta al cliente para decidir.
"""
                data2 = {
                    "model": "mistralai/mixtral-8x7b",
                    "messages": [{"role": "user", "content": prompt_analisis}]
                }

                response2 = requests.post(api_url, headers=headers, data=json.dumps(data2))

                if response2.status_code == 200:
                    analisis_final = response2.json()['choices'][0]['message']['content']
                    st.subheader("🧠 Análisis Técnico y Recomendación Final")
                    st.markdown(analisis_final)
                else:
                    st.error(f"Error al generar el análisis. Código: {response2.status_code}")
                    st.text(response2.text)

                # ============================
                # 💾 DESCARGA EN EXCEL
                # ============================
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    workbook = writer.book
                    worksheet = workbook.add_worksheet("Resumen y Comparativa")
                    writer.sheets["Resumen y Comparativa"] = worksheet
                    bold = workbook.add_format({'bold': True})

                    worksheet.write("A1", "Información del Candidato", bold)
                    worksheet.write("A3", "Nombre:", bold)
                    worksheet.write("B3", nombre_candidato)
                    worksheet.write("A4", "Rol con experiencia:", bold)
                    worksheet.write("B4", rol_experiencia)
                    worksheet.write("A5", "Rol al que aplica:", bold)
                    worksheet.write("B5", rol_postulado)

                    df.to_excel(writer, sheet_name="Resumen y Comparativa", startrow=7, index=False)

                output.seek(0)
                st.download_button(
                    label="💾 Descargar Excel con resumen",
                    data=output,
                    file_name=f"Resumen_{nombre_candidato.replace(' ', '_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error("⚠️ Error al interpretar la respuesta de la IA. Puede que el contenido no sea un JSON válido.")
                st.text(f"Detalle del error: {e}")
                st.text_area("Respuesta recibida (debug)", content, height=300)
        else:
            st.error(f"Error al analizar el CV. Código: {response.status_code}")
            st.text_area("Detalle del error (debug)", response.text, height=200)

# ============================
# ℹ️ Cómo funciona
# ============================
with st.expander("ℹ️ Cómo funciona esta app"):
    st.markdown("""
    1. Ingresá los datos del candidato y el rol.
    2. Subí el CV en formato PDF.
    3. Al hacer clic en el botón de analizar:
        - Se extrae el texto del CV.
        - Se consulta a una IA con un prompt estructurado.
        - Se recibe una tabla comparativa y una recomendación técnica.
        - Se genera un archivo Excel descargable.
    """)
