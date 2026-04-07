import streamlit as st
from fpdf import FPDF
import datetime
import os
import uuid
import qrcode
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

st.set_page_config(page_title="AI Pro Brochure Engine", layout="wide")

class ProBrochure(FPDF):
    def __init__(self, brand_color, brand_name, website_link):
        super().__init__()
        self.brand_color = brand_color
        self.brand_name = brand_name
        self.website_link = website_link

    def header(self):
        self.set_fill_color(*self.brand_color)
        self.rect(0, 0, 210, 4, 'F')
        self.ln(5)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(*self.brand_color)
        self.cell(0, 10, self.brand_name, ln=True, align='R')

    def footer(self):
        self.set_y(-25)
        self.set_draw_color(*self.brand_color)
        self.line(10, 272, 200, 272)
        self.set_text_color(50, 50, 50)
        self.set_font('Helvetica', 'B', 9)
        self.cell(0, 8, f'{self.brand_name} - SMART EQUIPMENT FOR SMART BUILDERS', align='C', ln=True)
        self.set_font('Helvetica', 'I', 8)
        clean_link = self.website_link.replace("https://", "").replace("http://", "").rstrip("/")
        self.cell(0, 4, f'Authorized Representative: Adjie Agung | {clean_link}', align='C')

# --- UI DASHBOARD ---
st.title("🤖 AI-Powered Pro Brochure Engine")
st.write("Otomatis ubah halaman website menjadi bahasa jualan yang powerful.")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. Identitas & Visual")
    brand = st.selectbox("Pilih Merek", ["AIMIX", "TATSUO"])
    
    if brand == "AIMIX":
        default_link = "https://aimix-self-loading-mixer.netlify.app/"
        default_model = "SELF LOADING MIXER"
    else:
        default_link = "https://tatsuosales-id.netlify.app/#/"
        default_model = "EXCAVATOR / WHEEL LOADER"

    model = st.text_input("Tipe Unit", default_model)
    headline = st.text_input("Headline Utama", "LEBIH CERDAS, LEBIH AKURAT, LEBIH ANDAL")
    ref_link = st.text_input("Link Website (Untuk Dibaca AI & QR Code)", default_link)
    foto = st.file_uploader("Upload Foto Unit Utama", type=['png', 'jpg', 'jpeg'])

with col2:
    st.subheader("2. AI Copywriting Generator")
    
    if st.button("✨ Tarik Data & Buat Copywriting Otomatis"):
        if not ref_link:
            st.error("Link website tidak boleh kosong.")
        else:
            with st.spinner("AI sedang membaca website dan meracik bahasa jualan..."):
                try:
                    # Mengambil API Key yang disembunyikan di Streamlit Secrets
                    api_key = st.secrets["GEMINI_API_KEY"]
                    
                    # 1. Scrape Website
                    res = requests.get(ref_link)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    scraped_text = soup.get_text(separator=' ', strip=True)[:4000]
                    
                    # 2. Proses dengan AI
                    genai.configure(api_key=api_key)
                    ai_model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""
                    Anda adalah Copywriter Alat Berat profesional.
                    Baca spesifikasi ini dan ekstrak menjadi 3-4 poin keunggulan utama.
                    Gunakan bahasa Indonesia yang powerful, maskulin, dan menunjukkan efisiensi/keuntungan pembeli.
                    
                    ATURAN FORMAT WAJIB (Gunakan pemisah tanda | antara judul dan deskripsi):
                    JUDUL FITUR 1 | Deskripsi penjelasan yang menjual maksimal 2 kalimat.
                    JUDUL FITUR 2 | Deskripsi penjelasan yang menjual maksimal 2 kalimat.
                    
                    Data spesifikasi:
                    {scraped_text}
                    """
                    response = ai_model.generate_content(prompt)
                    st.session_state['ai_result'] = response.text
                    st.success("Berhasil! Cek dan edit hasilnya di bawah jika perlu.")
                except KeyError:
                    st.error("Konfigurasi Error: API Key belum dimasukkan ke dalam Streamlit Secrets.")
                except Exception as e:
                    st.error(f"Gagal memproses data: {e}")

    ai_raw_text = st.session_state.get('ai_result', "BELUM ADA DATA.\nSilakan klik tombol di atas atau ketik manual dengan format:\nJUDUL | Deskripsi...")
    final_copy = st.text_area("Hasil Copywriting (Format: JUDUL | Deskripsi)", ai_raw_text, height=150)

st.markdown("---")

if st.button("🌟 Generate Professional Brochure"):
    if not foto:
        st.warning("Mohon upload 1 foto utama unit.")
    else:
        with st.spinner("Merancang layout PDF..."):
            b_color = (0, 82, 155) if brand == "AIMIX" else (204, 0, 0)
            pdf = ProBrochure(brand_color=b_color, brand_name=brand, website_link=ref_link)
            pdf.add_page()
            
            img_path = f"temp_hero_{uuid.uuid4()}.png"
            with open(img_path, "wb") as f:
                f.write(foto.getbuffer())
            pdf.image(img_path, x=20, y=25, w=170)
            if os.path.exists(img_path): os.remove(img_path)
            
            pdf.set_y(120)
            pdf.set_font('Helvetica', 'B', 20)
            pdf.set_text_color(20, 20, 20)
            pdf.multi_cell(0, 10, f"{brand} {model} - {headline}", align='C')
            pdf.ln(10)
            
            lines = final_copy.strip().split('\n')
            for line in lines:
                if '|' in line:
                    judul, deskripsi = line.split('|', 1)
                    
                    pdf.set_fill_color(*b_color)
                    pdf.ellipse(10, pdf.get_y() + 2, 3, 3, 'F')
                    
                    pdf.set_xy(16, pdf.get_y())
                    pdf.set_font('Helvetica', 'B', 12)
                    pdf.set_text_color(*b_color)
                    pdf.cell(0, 6, judul.strip().upper(), ln=True)
                    
                    pdf.set_xy(16, pdf.get_y())
                    pdf.set_font('Helvetica', '', 10)
                    pdf.set_text_color(50, 50, 50)
                    pdf.multi_cell(0, 5, deskripsi.strip())
                    pdf.ln(4)
                
            if ref_link:
                qr = qrcode.make(ref_link)
                qr_path = f"qr_{uuid.uuid4()}.png"
                qr.save(qr_path)
                pdf.image(qr_path, x=175, y=245, w=25, h=25)
                pdf.set_xy(170, 270)
                pdf.set_font('Helvetica', 'B', 6)
                pdf.set_text_color(*b_color)
                pdf.cell(35, 3, "SCAN FOR DETAILS", align='C')
                if os.path.exists(qr_path): os.remove(qr_path)

            out = pdf.output(dest='S')
            st.success("Brosur Profesional Berhasil Dibuat!")
            st.download_button("⬇️ Download High-Res PDF", data=bytes(out), file_name=f"{brand}_Smart_Brochure.pdf")
