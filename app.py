import streamlit as st
from fpdf import FPDF
import datetime

st.set_page_config(page_title="Mesin Brosur Tatsuo & Aimix", layout="wide")

class BrochurePDF(FPDF):
    def header(self):
        self.set_fill_color(255, 215, 0)
        self.rect(0, 0, 210, 30, 'F')
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, 'TATSUO & AIMIX OFFICIAL BROCHURE', ln=True, align='C')

    def footer(self):
        self.set_y(-20)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Marketing: Adjie Agung | Generated: {datetime.date.today()}', align='C')

st.title("🏗️ Mesin Brosur Alat Berat")
st.write("Representasi Resmi: **Adjie Agung**")

col1, col2 = st.columns(2)

with col1:
    brand = st.selectbox("Pilih Merek", ["TATSUO", "AIMIX"])
    model = st.text_input("Tipe Unit", "Contoh: TS-200")
    headline = st.text_input("Headline Promo", "Tenaga Tangguh, Harga Bersaing!")
    specs = st.text_area("Detail Spesifikasi", "Kapasitas: 3 Ton\nEngine: Cummins\nGaransi: 1 Tahun")

with col2:
    foto = st.file_uploader("Upload Foto Unit", type=['png', 'jpg', 'jpeg'])
    
    if st.button("🚀 Buat Brosur Sekarang"):
        pdf = BrochurePDF()
        pdf.add_page()
        
        pdf.ln(30)
        pdf.set_font('Helvetica', 'B', 22)
        pdf.cell(0, 15, f"{brand} {model}", ln=True)
        
        pdf.set_font('Helvetica', 'I', 12)
        pdf.cell(0, 10, f"'{headline}'", ln=True)
        pdf.ln(5)
        
        if foto:
            with open("temp_unit.png", "wb") as f:
                f.write(foto.getbuffer())
            pdf.image("temp_unit.png", x=10, y=70, w=190)
        
        pdf.set_y(180)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, "Spesifikasi Teknis:", ln=True)
        pdf.set_font('Helvetica', '', 11)
        pdf.multi_cell(0, 8, specs)
        
        pdf_output = pdf.output(dest='S')
        st.success("Brosur Berhasil Dibuat!")
        st.download_button(label="⬇️ Download PDF", data=bytes(pdf_output), file_name=f"Brosur_{model}.pdf")
