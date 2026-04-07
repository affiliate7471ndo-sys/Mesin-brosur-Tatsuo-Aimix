import streamlit as st
from fpdf import FPDF
import datetime
import os
import uuid
import qrcode
import requests
import json
from bs4 import BeautifulSoup

st.set_page_config(page_title="Ultimate Pro Brochure Engine", layout="wide")

class ProBrochure(FPDF):
    def __init__(self, brand_color, brand_name, website_link, logo_path, wa_number):
        super().__init__()
        self.brand_color = brand_color
        self.brand_name = brand_name
        self.website_link = website_link
        self.logo_path = logo_path
        self.wa_number = wa_number

    def header(self):
        # Garis warna di atas
        self.set_fill_color(*self.brand_color)
        self.rect(0, 0, 210, 4, 'F')
        
        # LOGO ATAU TEKS BRAND
        if self.logo_path and os.path.exists(self.logo_path):
            # Posisi logo di kanan atas. w=40 (lebar disesuaikan)
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
        
        # Teks Footer
        self.set_text_color(50, 50, 50)
        self.set_font('Helvetica', 'B', 9)
        self.cell(0, 6, f'{self.brand_name} - SMART EQUIPMENT FOR SMART BUILDERS', align='C', ln=True)
        
        # Link Website
        self.set_font('Helvetica', 'I', 8)
        clean_link = self.website_link.replace("https://", "").replace("http://", "").rstrip("/")
        self.cell(0, 4, f'Authorized Representative: Adjie Agung | {clean_link}', align='C', ln=True)

# --- UI DASHBOARD ---
st.title("🚀 Ultimate Brochure Engine - Tatsuo & Aimix")
st.write("Generasi terbaru dengan fitur Logo Kustom, Quick Specs, dan Integrasi WhatsApp.")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. Visual & Identitas")
    brand = st.selectbox("Pilih Merek", ["AIMIX", "TATSUO"])
    
    if brand == "AIMIX":
        default_link = "https://aimix-self-loading-mixer.netlify.app/"
        default_model = "SELF LOADING MIXER"
    else:
        default_link = "https://tatsuosales-id.netlify.app/#/"
        default_model = "EXCAVATOR / WHEEL LOADER"

    # FITUR BARU: Logo Upload & WA
    logo_file = st.file_uploader("Upload Logo Brand (PNG Transparan disarankan)", type=['png', 'jpg', 'jpeg'])
    foto = st.file_uploader("Upload Foto Unit Utama", type=['png', 'jpg', 'jpeg'])
    
    st.markdown("---")
    model = st.text_input("Tipe Unit", default_model)
    headline = st.text_input("Headline Utama", "LEBIH CERDAS, LEBIH AKURAT, LEBIH ANDAL")
    
    # FITUR BARU: Quick Specs Box
    st.caption("Highlight Spesifikasi Cepat (Tampil di bawah Headline)")
    c_sp1, c_sp2, c_sp3 = st.columns(3)
    with c_sp1: spec_engine = st.text_input("Engine / Power", "Cummins 125kW")
    with c_sp2: spec_cap = st.text_input("Kapasitas", "3.5 Kubik")
    with c_sp3: spec_weight = st.text_input("Bobot Unit", "7.5 Ton")

with col2:
    st.subheader("2. AI Copywriter & Kontak")
    
    ref_link = st.text_input("Link Website (Untuk Dibaca AI & QR Code)", default_link)
    wa_num = st.text_input("Nomor WhatsApp (Contoh: 628123456789)", "628123456789")
    
    if st.button("✨ Tarik Data & Buat Copywriting Otomatis"):
        if not ref_link:
            st.error("Link website tidak boleh kosong.")
        else:
            with st.spinner("Mengeksekusi Direct API ke Gemini 2.5 Flash..."):
                try:
                    api_key = st.secrets["GOOGLE_API_KEY"]
                    res = requests.get(ref_link, timeout=10)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    scraped_text = soup.get_text(separator=' ', strip=True)[:4000]
                    
                    prompt = f"""
                    Anda adalah Copywriter Alat Berat profesional.
                    Baca spesifikasi ini dan ekstrak menjadi 3 poin keunggulan utama.
                    Gunakan bahasa Indonesia yang powerful, maskulin, dan menunjukkan efisiensi/keuntungan pembeli.
                    
                    ATURAN FORMAT WAJIB (Gunakan pemisah tanda | antara judul dan deskripsi. Jangan gunakan tanda bintang atau bold):
                    JUDUL FITUR 1 | Deskripsi penjelasan yang menjual maksimal 2 kalimat.
                    JUDUL FITUR 2 | Deskripsi penjelasan yang menjual maksimal 2 kalimat.
                    
                    Data spesifikasi:
                    {scraped_text}
                    """
                    
                    api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}"
                    headers = {'Content-Type': 'application/json'}
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    
                    response = requests.post(api_url, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        hasil_ai = data['candidates'][0]['content']['parts'][0]['text']
                        st.session_state['ai_result'] = hasil_ai
                        st.success("Teks jualan berhasil dibuat!")
                    else:
                        error_details = response.json()
                        st.error(f"Gagal memanggil API. Pesan: {json.dumps(error_details)}")
                        
                except Exception as e:
                    st.error(f"Terjadi kesalahan teknis: {e}")

    ai_raw_text = st.session_state.get('ai_result', "BELUM ADA DATA.\nSilakan klik tombol di atas atau ketik manual dengan format:\nJUDUL | Deskripsi...")
    final_copy = st.text_area("Hasil Copywriting (Format: JUDUL | Deskripsi)", ai_raw_text, height=150)

st.markdown("---")

if st.button("🌟 Generate Ultimate Brochure"):
    if not foto:
        st.warning("Mohon upload 1 foto utama unit.")
    else:
        with st.spinner("Merancang layout PDF tingkat tinggi..."):
            b_color = (0, 82, 155) if brand == "AIMIX" else (204, 0, 0)
            
            # Kelola File Logo
            logo_path = None
            if logo_file:
                logo_path = f"temp_logo_{uuid.uuid4()}.png"
                with open(logo_path, "wb") as f:
                    f.write(logo_file.getbuffer())
            
            pdf = ProBrochure(brand_color=b_color, brand_name=brand, website_link=ref_link, logo_path=logo_path, wa_number=wa_num)
            pdf.add_page()
            
            # --- 1. GAMBAR UTAMA ---
            img_path = f"temp_hero_{uuid.uuid4()}.png"
            with open(img_path, "wb") as f:
                f.write(foto.getbuffer())
            
            pdf.image(img_path, x=35, y=25, w=140)
            if os.path.exists(img_path): os.remove(img_path)
            
            # --- 2. HEADLINE BESAR ---
            pdf.set_y(135) 
            pdf.set_font('Helvetica', 'B', 18) 
            pdf.set_text_color(20, 20, 20)
            pdf.multi_cell(0, 10, f"{brand} {model} - {headline}", align='C')
            
            # --- 3. QUICK SPECS BOX (FITUR BARU) ---
            pdf.ln(2)
            pdf.set_fill_color(245, 245, 245) # Warna abu-abu muda
            pdf.rect(10, pdf.get_y(), 190, 12, 'F') # Kotak background
            
            pdf.set_y(pdf.get_y() + 3)
            pdf.set_font('Helvetica', 'B', 9)
            pdf.set_text_color(80, 80, 80)
            # Dibagi 3 kolom sama rata
            pdf.cell(63, 6, f"ENGINE: {spec_engine.upper()}", align='C')
            pdf.cell(63, 6, f"KAPASITAS: {spec_cap.upper()}", align='C')
            pdf.cell(63, 6, f"BOBOT: {spec_weight.upper()}", align='C', ln=True)
            pdf.ln(8) # Jarak sebelum copywriting
            
            # --- 4. COPYWRITING AI ---
            lines = final_copy.strip().split('\n')
            for line in lines:
                if '|' in line:
                    judul, deskripsi = line.split('|', 1)
                    judul_bersih = judul.replace("**", "").replace("*", "").strip().upper()
                    deskripsi_bersih = deskripsi.replace("**", "").replace("*", "").strip()
                    
                    pdf.set_fill_color(*b_color)
                    pdf.ellipse(10, pdf.get_y() + 2, 3, 3, 'F')
                    
                    pdf.set_xy(16, pdf.get_y())
                    pdf.set_font('Helvetica', 'B', 12)
                    pdf.set_text_color(*b_color)
                    pdf.cell(0, 6, judul_bersih, ln=True)
                    
                    pdf.set_xy(16, pdf.get_y())
                    pdf.set_font('Helvetica', '', 10)
                    pdf.set_text_color(50, 50, 50)
                    pdf.multi_cell(0, 5, deskripsi_bersih)
                    pdf.ln(4)
                
            # --- 5. QR CODE & WHATSAPP CTA ---
            if ref_link:
                qr = qrcode.make(ref_link)
                qr_path = f"qr_{uuid.uuid4()}.png"
                qr.save(qr_path)
                
                # Render QR
                pdf.image(qr_path, x=175, y=235, w=25, h=25)
                pdf.set_xy(170, 262)
                pdf.set_font('Helvetica', 'B', 6)
                pdf.set_text_color(*b_color)
                pdf.cell(35, 3, "SCAN FOR DETAILS", align='C')
                if os.path.exists(qr_path): os.remove(qr_path)
            
            # Render WA CTA (Sebelah kiri QR)
            pdf.set_xy(10, 250)
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_text_color(20, 20, 20)
            pdf.cell(50, 6, "HUBUNGI SALES EXECUTIVE:", ln=True)
            
            pdf.set_font('Helvetica', 'B', 16)
            pdf.set_text_color(*b_color) # Warna sesuai brand
            wa_link = f"https://wa.me/{wa_num}"
            pdf.cell(50, 8, f"WhatsApp: +{wa_num}", link=wa_link, ln=True)

            # Cleanup logo temp
            if logo_path and os.path.exists(logo_path):
                os.remove(logo_path)

            out = pdf.output(dest='S')
            st.success("Brosur Ultimate Berhasil Dibuat!")
            st.download_button("⬇️ Download High-Res PDF", data=bytes(out), file_name=f"{brand}_Ultimate_Brochure.pdf")
