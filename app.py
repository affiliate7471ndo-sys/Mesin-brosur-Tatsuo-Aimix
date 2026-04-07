import streamlit as st
from fpdf import FPDF
import datetime
import os
import uuid
import qrcode

st.set_page_config(page_title="Tatsuo & Aimix Pro Brochure", layout="wide")

class ProBrochure(FPDF):
    def __init__(self, brand_color, brand_name):
        super().__init__()
        self.brand_color = brand_color
        self.brand_name = brand_name

    def header(self):
        # Garis tipis elegan di atas
        self.set_fill_color(*self.brand_color)
        self.rect(0, 0, 210, 4, 'F')
        
        # Nama Brand (Sebagai pengganti logo)
        self.ln(5)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(*self.brand_color)
        self.cell(0, 10, self.brand_name, ln=True, align='R')

    def footer(self):
        self.set_y(-25)
        self.set_draw_color(*self.brand_color)
        self.line(10, 272, 200, 272) # Garis pemisah
        
        self.set_text_color(50, 50, 50)
        self.set_font('Helvetica', 'B', 9)
        self.cell(0, 8, f'{self.brand_name} - SMART EQUIPMENT FOR SMART BUILDERS', align='C', ln=True)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 4, f'Authorized Representative: Adjie Agung | tatsuosales-id.netlify.app', align='C')

# --- UI DASHBOARD ---
st.title("✨ Pro Brochure Engine - Corporate Style")
st.write("Layout bersih, modern, dan profesional. Fokus pada visual dan keunggulan utama.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Identitas & Visual")
    brand = st.selectbox("Pilih Merek", ["AIMIX", "TATSUO"])
    model = st.text_input("Tipe Unit", "SELF LOADING MIXER")
    headline = st.text_input("Headline Utama (Huruf Besar)", "LEBIH CERDAS, LEBIH AKURAT, LEBIH ANDAL")
    ref_link = st.text_input("Link Produk (Untuk QR Code)", "https://tatsuosales-id.netlify.app/#/")
    foto = st.file_uploader("Upload Foto Unit (Gunakan foto tanpa background putih agar menyatu)", type=['png', 'jpg', 'jpeg'])

with col2:
    st.subheader("2. Poin Keunggulan (Seperti contoh gambar)")
    st.info("Isi poin-poin fitur andalan. Kosongkan jika tidak dipakai.")
    
    fitur = []
    for i in range(1, 6):
        with st.expander(f"Fitur Utama {i}", expanded=(i<=2)):
            judul = st.text_input(f"Judul Fitur {i}", key=f"j_{i}")
            deskripsi = st.text_area(f"Deskripsi Fitur {i}", key=f"d_{i}")
            if judul and deskripsi:
                fitur.append({"judul": judul, "desc": deskripsi})

if st.button("🌟 Generate Professional Brochure"):
    if not foto:
        st.warning("Mohon upload 1 foto utama unit.")
    else:
        with st.spinner("Merancang layout profesional..."):
            # Set warna berdasarkan brand (Aimix = Biru, Tatsuo = Merah/Kuning Gelap)
            b_color = (0, 82, 155) if brand == "AIMIX" else (204, 0, 0)
            
            pdf = ProBrochure(brand_color=b_color, brand_name=brand)
            pdf.add_page()
            
            # --- 1. HERO IMAGE (Besar di tengah) ---
            img_path = f"temp_hero_{uuid.uuid4()}.png"
            with open(img_path, "wb") as f:
                f.write(foto.getbuffer())
            
            # Posisikan gambar di tengah atas (Y=25)
            pdf.image(img_path, x=20, y=25, w=170)
            if os.path.exists(img_path): os.remove(img_path)
            
            # --- 2. HEADLINE BESAR ---
            pdf.set_y(120) # Mulai teks di bawah gambar
            pdf.set_font('Helvetica', 'B', 20)
            pdf.set_text_color(20, 20, 20)
            
            # Gabungkan brand, model, dan headline
            full_headline = f"{brand} {model} - {headline}"
            pdf.multi_cell(0, 10, full_headline, align='C')
            pdf.ln(10)
            
            # --- 3. POIN-POIN KEUNGGULAN (Bermodel Bullet Point Modern) ---
            for item in fitur:
                # Bullet (Titik Biru/Merah)
                pdf.set_fill_color(*b_color)
                pdf.ellipse(10, pdf.get_y() + 2, 3, 3, 'F')
                
                # Judul Fitur (Berwarna)
                pdf.set_xy(16, pdf.get_y())
                pdf.set_font('Helvetica', 'B', 12)
                pdf.set_text_color(*b_color)
                pdf.cell(0, 6, item['judul'].upper(), ln=True)
                
                # Deskripsi Fitur (Hitam)
                pdf.set_xy(16, pdf.get_y())
                pdf.set_font('Helvetica', '', 10)
                pdf.set_text_color(50, 50, 50)
                pdf.multi_cell(0, 5, item['desc'])
                pdf.ln(4) # Jarak antar fitur
                
            # --- 4. QR CODE (Pojok Kanan Bawah) ---
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

            # --- OUTPUT ---
            out = pdf.output(dest='S')
            st.success("Brosur Profesional Berhasil Dibuat!")
            st.download_button("⬇️ Download High-Res PDF", data=bytes(out), file_name=f"{brand}_{model}_Pro.pdf")
