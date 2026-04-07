import streamlit as st
from fpdf import FPDF
import datetime
import os
import uuid

# Konfigurasi Halaman
st.set_page_config(page_title="Tatsuo & Aimix Brochure Engine v2.0", layout="wide")

class BrochurePDF(FPDF):
    def header(self):
        self.set_fill_color(255, 215, 0) # Kuning Alat Berat
        self.rect(0, 0, 210, 30, 'F')
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, 'TATSUO & AIMIX OFFICIAL BROCHURE', ln=True, align='C')
        self.set_font('Helvetica', '', 10)
        self.cell(0, 5, 'High Performance Heavy Equipment Solutions', ln=True, align='C')

    def footer(self):
        self.set_y(-20)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Marketing Representative: Adjie Agung | Generated: {datetime.date.today()}', align='C')

# Interface Dashboard
st.title("🏗️ Mesin Brosur Multi-Gambar")
st.write("Representasi Resmi: **Adjie Agung**")
st.markdown("---")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("1. Detail Unit")
    brand = st.selectbox("Pilih Merek", ["TATSUO", "AIMIX"])
    model = st.text_input("Tipe Unit", placeholder="Contoh: JP80-9 / Self Loading Mixer")
    headline = st.text_input("Headline Promo", placeholder="Tangguh di segala medan!")
    specs = st.text_area("Detail Spesifikasi", placeholder="Kapasitas: 8 Ton\nEngine: Yanmar\nGaransi: 1 Tahun", height=200)

with col2:
    st.subheader("2. Visual Unit (Maks 5 Gambar)")
    # Perubahan di sini: accept_multiple_files=True
    fotos = st.file_uploader("Upload Foto-foto Unit (Maks 5)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    
    if fotos and len(fotos) > 5:
        st.error("Waduh Pak Adjie, maksimal 5 gambar saja ya agar layout PDF-nya tetap rapi.")
        generate_ready = False
    elif not fotos:
        st.warning("Silakan upload minimal 1 foto utama.")
        generate_ready = False
    else:
        st.success(f"{len(fotos)} gambar siap diproses.")
        generate_ready = True

st.markdown("---")
if st.button("🚀 Buat Brosur PDF Sekarang", disabled=not generate_ready):
    with st.spinner("Sedang menyusun layout PDF dan mengolah gambar..."):
        pdf = BrochurePDF()
        pdf.add_page()
        
        # --- Judul & Headline ---
        pdf.ln(35)
        pdf.set_font('Helvetica', 'B', 28)
        pdf.set_text_color(200, 0, 0) # Merah Merek
        pdf.cell(0, 15, f"{brand} {model}", ln=True)
        
        pdf.set_font('Helvetica', 'I', 14)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 10, f"'{headline}'", ln=True)
        pdf.ln(5)
        
        # --- Pengolahan Gambar Dinamis (Max 5) ---
        if fotos:
            saved_images = []
            
            # 1. Simpan gambar sementara dengan nama unik (UUID)
            for i, foto_file in enumerate(fotos):
                if i >= 5: break # Safeguard maks 5
                
                # Buat nama file unik agar tidak bentrok
                unique_filename = f"temp_{uuid.uuid4()}_{i}.png"
                with open(unique_filename, "wb") as f:
                    f.write(foto_file.getbuffer())
                saved_images.append(unique_filename)

            # 2. Atur Layout Berdasarkan Jumlah Gambar
            num_images = len(saved_images)
            specs_start_y = 180 # Default posisi teks spesifikasi
            
            if num_images > 0:
                # Gambar 1 (Utama - Besar)
                try:
                    pdf.image(saved_images[0], x=10, y=70, w=190, h=80)
                    specs_start_y = 155 # Jika hanya 1 gambar, teks naik sedikit
                except:
                    pdf.set_xy(10, 70)
                    pdf.cell(190, 80, "[Gagal memuat gambar utama]", border=1, align='C')

                # Gambar 2-5 (Kecil - Susunan Grid di bawah gambar utama)
                if num_images > 1:
                    specs_start_y = 210 # Turunkan teks spesifikasi untuk grid
                    
                    gap = 5 # Jarak antar gambar
                    thumb_w = (190 - (gap * 3)) / 4 # Hitung lebar tiap thumbnail agar pas di lebar kertas
                    thumb_h = 40
                    y_grid = 155 # Posisi Y mulainya grid
                    
                    for i, img_path in enumerate(saved_images[1:]):
                        # Hitung posisi X dinamis
                        x_grid = 10 + (i * (thumb_w + gap))
                        try:
                            pdf.image(img_path, x=x_grid, y=y_grid, w=thumb_w, h=thumb_h)
                        except:
                            pdf.set_xy(x_grid, y=y_grid)
                            pdf.set_font('Helvetica', '', 8)
                            pdf.cell(thumb_w, thumb_h, "[Error]", border=1, align='C')

            # 3. Hapus Gambar Sementara setelah dimasukkan ke PDF
            for img_path in saved_images:
                if os.path.exists(img_path):
                    os.remove(img_path)

        # --- Spesifikasi Teknis (Posisinya dinamis mengikuti gambar) ---
        pdf.set_y(specs_start_y)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(240, 240, 240) # Abu-abu muda untuk header spek
        pdf.cell(0, 10, "  Spesifikasi Teknis:", ln=True, fill=True)
        
        pdf.ln(3)
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(30, 30, 30)
        # multi_cell untuk teks panjang
        pdf.multi_cell(0, 8, specs)
        
        # --- Generate Output ---
        # Gunakan nama model untuk nama file download
        safe_model_name = model.replace("/", "-").replace(" ", "_")
        pdf_output = pdf.output(dest='S')
        st.success("Brosur Multi-Gambar Berhasil Dibuat!")
        st.download_button(label="⬇️ Download Brosur PDF", data=bytes(pdf_output), file_name=f"Brosur_{brand}_{safe_model_name}.pdf")
