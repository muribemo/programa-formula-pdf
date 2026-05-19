import streamlit as st
import tempfile
import os
from datetime import datetime

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

def _build_filename(patient: str) -> str:
    now = datetime.now()
    nombre = patient.strip().replace(" ", "") if patient.strip() else "Paciente"
    fecha = f"{now.day:02d}{MESES[now.month]}{now.year}_{now.strftime('%H%M')}"
    return f"receta_{nombre}_{fecha}.pdf"
from pdf_generator import generate_prescription_pdf

st.set_page_config(
    page_title="Recetas — mateouribe",
    page_icon="💊",
    layout="centered"
)

# Header
st.markdown("""
<style>
    .header {
        background-color: #1A1A6E;
        padding: 20px 30px;
        border-radius: 10px;
        margin-bottom: 24px;
    }
    .header h1 {
        color: white;
        margin: 0;
        font-size: 28px;
    }
    .header p {
        color: #AABFFF;
        margin: 4px 0 0 0;
        font-size: 14px;
    }
    .med-box {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        background: #f9f9ff;
    }
</style>
<div class="header">
    <h1>mateouribe</h1>
    <p>Formulación de Recetas Médicas</p>
</div>
""", unsafe_allow_html=True)

# Session state para medicamentos
if "medications" not in st.session_state:
    st.session_state.medications = [{}]

# ── Datos del paciente ───────────────────────────────────────────────────────
with st.expander("Datos del paciente (opcional)", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        patient = st.text_input("Paciente", placeholder="Nombre completo")
    with col2:
        date = st.text_input("Fecha", value=datetime.today().strftime("%d/%m/%Y"))
    diagnosis = st.text_input("Diagnóstico", placeholder="Ej: Herpes Zoster")

st.divider()

# ── Medicamentos ─────────────────────────────────────────────────────────────
st.subheader("Medicamentos")

medications = []
to_remove = None

for i, _ in enumerate(st.session_state.medications):
    with st.container():
        st.markdown(f"**Medicamento {i + 1}**")

        col1, col2 = st.columns(2)
        with col1:
            generic = st.text_input(
                "Nombre genérico *",
                key=f"generic_{i}",
                placeholder="Ej: Valacyclovir"
            )
        with col2:
            brand = st.text_input(
                "Nombre comercial",
                key=f"brand_{i}",
                placeholder="Ej: Valtrex®"
            )

        col3, col4 = st.columns(2)
        with col3:
            form = st.text_input(
                "Presentación",
                key=f"form_{i}",
                placeholder="Ej: Tabletas 1 gr"
            )
        with col4:
            instructions = st.text_input(
                "Instrucciones *",
                key=f"instructions_{i}",
                placeholder="Ej: Tomar 1 tableta cada 8 horas"
            )

        if len(st.session_state.medications) > 1:
            if st.button(f"✕ Eliminar medicamento {i + 1}", key=f"remove_{i}"):
                to_remove = i

        medications.append({
            "generic": generic,
            "brand": brand,
            "form": form,
            "instructions": instructions,
        })

        st.divider()

if to_remove is not None:
    st.session_state.medications.pop(to_remove)
    st.rerun()

if st.button("＋ Agregar medicamento", use_container_width=False):
    st.session_state.medications.append({})
    st.rerun()

# ── Generar PDF ───────────────────────────────────────────────────────────────
st.markdown("")
if st.button("📄 Generar PDF", type="primary", use_container_width=True):
    # Validar
    errors = []
    for i, med in enumerate(medications):
        if not med["generic"].strip():
            errors.append(f"Medicamento {i + 1}: el nombre genérico es obligatorio.")
        if not med["instructions"].strip():
            errors.append(f"Medicamento {i + 1}: las instrucciones son obligatorias.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        data = {
            "patient": patient,
            "date": date,
            "diagnosis": diagnosis,
            "medications": medications,
        }

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp_path = tmp.name

        try:
            generate_prescription_pdf(tmp_path, data)

            with open(tmp_path, "rb") as f:
                pdf_bytes = f.read()

            filename = _build_filename(patient)
            st.success("¡PDF generado exitosamente!")
            st.download_button(
                label="⬇️ Descargar receta",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error al generar el PDF: {e}")
        finally:
            os.unlink(tmp_path)
