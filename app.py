import streamlit as st
from fpdf import FPDF
import datetime
import os
import uuid
import qrcode
import requests
import json
from bs4 import BeautifulSoup
import PyPDF2
import fitz
from PIL import Image
import time  

st.set_page_config(page_title="Ultimate Pro Brochure Engine", layout="wide")

# --- INISIALISASI FOLDER MEMORI ---
CATALOG_DIR = "katalog_tersimpan"
if not os.path.exists(CATALOG_DIR):
    os.makedirs(CATALOG_DIR)

class ProBrochure(FPDF):
    def __init__(self, brand_color, brand_name, website_link, logo_path, wa_number):
        super().__init__()
        self.brand_color = brand_color
        self.brand_name = brand_name
        self.website_link = website_link
        self.logo_path = logo_path
        self.wa_number = wa_number

    def header(self):
        self.set_fill_color(*self.brand_color)
        self.rect(0, 0, 210, 4, 'F')
        
        if self.logo_path and os.path.exists(self.logo_path):
            self.image(self.logo_path, x=160, y=8, w=40)
        else:
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
        self.cell(0, 6, f'{self.brand_name} - SMART EQUIPMENT FOR SMART BUILDERS', align='C', ln=True)
        
        self.set_font('Helvetica', 'I', 8)
        clean_link = self.website_link.replace("https://", "").replace("http://", "").rstrip("/")
        self.cell(0, 4, f'Authorized Representative: Adjie Agung | {clean_link}', align='C', ln=True)

# --- UI DASHBOARD ---
st.title("🚀 Ultimate Brochure Engine + Final Fix")
st.write("Generasi terbaru dengan Perbaikan Jalur API 100% Valid.")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. Visual & Identitas")
    brand = st.selectbox("Pilih Merek", ["AIMIX", "TATSUO"])
    
    if brand == "AIMIX":
        default_link = "https://aimix-self-loading-mixer.netlify.app/"
        default_model = "SELF LOADING MIXER"
    else:
        default_link = "https://tatsuosales-id.netlify.app/#/"
        default_model = "WHEEL CRAWLER EXCAVATOR JP80-9"

    logo_file = st.file_uploader("Upload Logo Brand (PNG Transparan)", type=['png', 'jpg', 'jpeg'])
    foto = st.file_uploader("Upload Foto Unit Utama", type=['png', 'jpg', 'jpeg'])
    
    st.markdown("---")
    model = st.text_input("Tipe Unit", default_model)
    headline = st.text_input("Headline Utama", "TANGGUH DISEGALA MEDAN")
    
    st.caption("Highlight Spesifikasi Cepat")
    c_sp1, c_sp2, c_sp3 = st.columns(3)
    with c_sp1: spec_engine = st.text_input("Engine / Power", "Yanmar 4TNV98-ZCVLGC")
    with c_sp2: spec_cap = st.text_input("Hydraulic System", "Rexroth")
    with c_sp3: spec_weight = st.text_input("Bobot Unit", "9600kg")

    st.caption("Stempel Kepercayaan (Trust Badges)")
    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1: badge1 = st.text_input("Badge 1", "GARANSI 1 TAHUN")
    with b_col2: badge2 = st.text_input("Badge 2", "")
    with b_col3: badge3 = st.text_input("Badge 3", "READY STOCK")

with col2:
    st.subheader("2. AI Copywriter & Database Referensi")
    
    ref_link = st.text_input("Link Website Produk (Opsional)", default_link)
    
    st.markdown("**📂 Database Katalog (PDF)**")
    saved_files = [f for f in os.listdir(CATALOG_DIR) if f.endswith('.pdf')]
    pilihan_katalog = st.selectbox("Pilih File dari Memori / Upload Baru", ["-- Upload Katalog Baru --"] + saved_files)
    
    pdf_path_to_read = None
    
    if pilihan_katalog == "-- Upload Katalog Baru --":
        pdf_ref = st.file_uploader("Upload Katalog Spesifikasi (PDF)", type=['pdf'])
        if pdf_ref:
            save_path = os.path.join(CATALOG_DIR, pdf_ref.name)
            with open(save_path, "wb") as f:
                f.write(pdf_ref.getbuffer())
            st.success(f"✅ Katalog '{pdf_ref.name}' tersimpan ke memori!")
            pdf_path_to_read = save_path
    else:
        pdf_path_to_read = os.path.join(CATALOG_DIR, pilihan_katalog)
        st.info(f"⚡ Menggunakan katalog dari memori: **{pilihan_katalog}**")
        
    wa_num = st.text_input("Nomor WhatsApp (Contoh: +628123456789)", "+6281230857759")
    
    if st.button("✨ Tarik Data & Buat Copywriting Otomatis"):
        if not ref_link and not pdf_path_to_read:
            st.error("Silakan masukkan Link Website atau pilih/upload Katalog PDF.")
        else:
            with st.spinner("AI sedang meramu data..."):
                try:
                    api_key = st.secrets["GOOGLE_API_KEY"]
                    scraped_text = ""
                    
                    if ref_link:
                        try:
                            res = requests.get(ref_link, timeout=10)
                            soup = BeautifulSoup(res.text, 'html.parser')
                            scraped_text += soup.get_text(separator=' ', strip=True)[:3000]
                        except: pass

                    if pdf_path_to_read:
                        try:
                            with open(pdf_path_to_read, "rb") as file_pdf:
                                pdf_reader = PyPDF2.PdfReader(file_pdf)
                                num_pages = min(5, len(pdf_reader.pages))
                                for i in range(num_pages):
                                    scraped_text += pdf_reader.pages[i].extract_text() + "\n"
                        except: pass
                            
                    prompt = f"Tolong buatkan 4 poin keunggulan alat berat dari data ini: {scraped_text[:8000]}. Format wajib: JUDUL | Deskripsi singkat."
                    
                    # --- FIX FINAL: Nama model HARUS models/gemini-1.5-flash ---
                    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                    headers = {'Content-Type': 'application/json'}
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    
                    # Auto Retry
                    for attempt in range(3):
                        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
                        if response.status_code == 200:
                            data = response.json()
                            hasil_ai = data['candidates'][0]['content']['parts'][0]['text']
                            st.session_state['ai_result'] = hasil_ai
                            st.success("✅ Berhasil!")
                            break
                        else:
                            time.sleep(2)
                            if attempt == 2:
                                st.error(f"Error: {response.status_code} - {response.text}")

                except Exception as e:
                    st.error(f"Sistem Error: {e}")

    ai_raw_text = st.session_state.get('ai_result', "JUDUL | Deskripsi...")
    final_copy = st.text_area("Hasil Copywriting", ai_raw_text, height=150)

st.markdown("---")

if st.button("🌟 Generate Ultimate Brochure"):
    if not foto:
        st.warning("Mohon upload foto.")
    else:
        with st.spinner("Merancang PDF..."):
            b_color = (0, 82, 155) if brand == "AIMIX" else (204, 0, 0)
            
            logo_path = None
            if logo_file:
                logo_path = f"temp_logo_{uuid.uuid4()}.png"
                with open(logo_path, "wb") as f: f.write(logo_file.getbuffer())
            
            pdf = ProBrochure(b_color, brand, ref_link, logo_path, wa_num)
            pdf.add_page()
            
            # Watermark
            if logo_path:
                img = Image.open(logo_path).convert("RGBA")
                alpha = img.split()[3].point(lambda p: p * 0.1)
                img.putalpha(alpha)
                wm_p = f"wm_{uuid.uuid4()}.png"
                img.save(wm_p)
                pdf.image(wm_p, x=35, y=90, w=140)
            
            # QR Code
            if ref_link:
                qr_path = f"qr_{uuid.uuid4()}.png"
                qrcode.make(ref_link).save(qr_path)
                pdf.image(qr_path, x=12, y=8, w=22, h=22)
                pdf.set_xy(8, 31); pdf.set_font('Helvetica', 'B', 6); pdf.set_text_color(*b_color)
                pdf.cell(30, 3, "SCAN FOR DETAILS", align='C')

            # Main Image
            img_p = f"hero_{uuid.uuid4()}.png"
            with open(img_p, "wb") as f: f.write(foto.getbuffer())
            pdf.image(img_p, x=40, y=14, w=130)
            
            # Content
            pdf.set_y(115); pdf.set_font('Helvetica', 'B', 18); pdf.set_text_color(20, 20, 20)
            pdf.multi_cell(0, 10, f"{brand} {model} - {headline}", align='C')
            
            pdf.set_fill_color(245, 245, 245); pdf.rect(10, pdf.get_y(), 190, 12, 'F')
            pdf.set_y(pdf.get_y()+3); pdf.set_font('Helvetica', 'B', 9); pdf.set_text_color(80, 80, 80)
            pdf.cell(63, 6, f"ENGINE: {spec_engine}", align='C')
            pdf.cell(63, 6, f"HYDRAULIC: {spec_cap}", align='C')
            pdf.cell(63, 6, f"BOBOT: {spec_weight}", align='C', ln=True)
            
            pdf.ln(5); pdf.set_fill_color(*b_color); pdf.set_text_color(255, 255, 255); pdf.set_font('Helvetica', 'B', 10)
            pdf.cell(60, 8, badge1.upper(), fill=True, align='C')
            pdf.cell(5); pdf.cell(60, 8, badge2.upper() if badge2 else "-", fill=True, align='C')
            pdf.cell(5); pdf.cell(60, 8, badge3.upper(), fill=True, align='C', ln=True)
            
            pdf.ln(8); pdf.set_text_color(50, 50, 50)
            for line in final_copy.strip().split('\n'):
                if '|' in line:
                    j, d = line.split('|', 1)
                    pdf.set_font('Helvetica', 'B', 12); pdf.set_text_color(*b_color)
                    pdf.cell(0, 6, j.strip().upper(), ln=True)
                    pdf.set_font('Helvetica', '', 10); pdf.set_text_color(50, 50, 50)
                    pdf.multi_cell(0, 5, d.strip()); pdf.ln(2)

            # Footer WA
            pdf.set_xy(10, 250); pdf.set_font('Helvetica', 'B', 12); pdf.set_text_color(20, 20, 20)
            pdf.cell(0, 6, "HUBUNGI SALES KAMI:", ln=True)
            pdf.set_font('Helvetica', 'B', 16); pdf.set_text_color(*b_color)
            pdf.cell(0, 8, f"WhatsApp: {wa_num}", ln=True, link=f"https://wa.me/{wa_num.replace('+', '')}")

            # Export
            out = pdf.output(dest='S')
            pdf_b = bytes(out)
            doc = fitz.open("pdf", pdf_b)
            pix = doc.load_page(0).get_pixmap(dpi=300)
            st.success("✅ Selesai!")
            st.download_button("⬇️ PDF", data=pdf_b, file_name="Brosur.pdf")
            st.download_button("🖼️ PNG", data=pix.tobytes("png"), file_name="Brosur.png")
