import streamlit as st
import pandas as pd
import os
from fpdf import FPDF

DATA_FILE = 'produkMart.csv'
GAMBAR_FOLDER = 'gambar_produk'

# Helper functions
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["Nama_Product", "Kuantitas", "Harga"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def buat_struk(keranjang):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="PTOIR MART", ln=True, align='C')
    pdf.cell(200, 10, txt="Struk Pembelian", ln=True, align='C')
    pdf.ln(10)

    total = 0
    for item in keranjang:
        nama = item['nama']
        jumlah = item['jumlah']
        harga = item['harga']
        subtotal = jumlah * harga
        total += subtotal
        pdf.cell(200, 10, txt=f"{nama} x{jumlah} @ Rp{harga:,} = Rp{subtotal:,}", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Total Bayar: Rp{total:,}", ln=True)

    filename = "struk_belanja.pdf"
    pdf.output(filename)
    return filename

# Sidebar Menu
menu = st.sidebar.selectbox("Pilih Menu", ["Lihat Produk", "Tambah Stok", "Update Harga", "Kasir", "Lihat Struk"])

if 'keranjang' not in st.session_state:
    st.session_state.keranjang = []

if 'jumlah_edit' not in st.session_state:
    st.session_state.jumlah_edit = {}

if menu == "Lihat Produk":
    st.header("📦 Daftar Produk")
    df = load_data()
    if df.empty:
        st.warning("Belum ada produk.")
    else:
        st.write("Klik 'Lihat' untuk melihat gambar produk.")
        st.divider()

        if 'selected_image' not in st.session_state:
            st.session_state.selected_image = None
            st.session_state.selected_caption = None

        with st.container():
            st.markdown("""
                <style>
                .product-box {
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 10px;
                    margin-bottom: 10px;
                    background-color: #f9f9f9;
                }
                </style>
            """, unsafe_allow_html=True)

            for i, row in df.iterrows():
                with st.container():
                    st.markdown(f"<div class='product-box'>", unsafe_allow_html=True)
                    col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
                    col1.markdown(f"**{i+1}.**")
                    col2.markdown(f"**{row['Nama_Product']}**")
                    with col3:
                        if st.button("Lihat", key=f"lihat_{i}"):
                            nama_produk = row['Nama_Product']
                            nama_file_fix = nama_produk.replace("/", "-").replace("\\", "-").strip()
                            jpg_path = os.path.join(GAMBAR_FOLDER, f"{nama_file_fix}.jpg")
                            png_path = os.path.join(GAMBAR_FOLDER, f"{nama_file_fix}.png")

                            if os.path.exists(jpg_path):
                                st.session_state.selected_image = jpg_path
                                st.session_state.selected_caption = nama_produk
                            elif os.path.exists(png_path):
                                st.session_state.selected_image = png_path
                                st.session_state.selected_caption = nama_produk
                            else:
                                st.session_state.selected_image = None
                                st.session_state.selected_caption = "Gambar tidak ditemukan"
                    col4.write(row['Kuantitas'])
                    col5.write(f"Rp{int(row['Harga']):,}")
                    st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.selected_image:
            with st.expander(f"📸 {st.session_state.selected_caption}", expanded=True):
                st.image(st.session_state.selected_image, caption=st.session_state.selected_caption, use_column_width=True)
        elif st.session_state.selected_caption == "Gambar tidak ditemukan":
            st.error("Gambar tidak ditemukan.")

elif menu == "Tambah Stok":
    st.header("➕ Tambah Stok Produk")
    nama = st.text_input("Nama Produk")
    stok = st.number_input("Jumlah Stok", min_value=1, step=1)
    harga = st.number_input("Harga per item", min_value=100, step=100)
    if st.button("Tambah"):
        df = load_data()
        if nama in df['Nama_Product'].values:
            df.loc[df['Nama_Product'] == nama, 'Kuantitas'] += stok
        else:
            df = pd.concat([df, pd.DataFrame([[nama, stok, harga]], columns=["Nama_Product", "Kuantitas", "Harga"])] , ignore_index=True)
        save_data(df)
        st.success("Stok berhasil ditambahkan!")

elif menu == "Update Harga":
    st.header("💰 Update Harga Produk")
    df = load_data()
    if df.empty:
        st.warning("Belum ada produk untuk diupdate.")
    else:
        produk = st.selectbox("Pilih Produk", df['Nama_Product'])
        harga_baru = st.number_input("Harga Baru", min_value=100, step=100)
        if st.button("Update"):
            df.loc[df['Nama_Product'] == produk, 'Harga'] = harga_baru
            save_data(df)
            st.success("Harga berhasil diupdate.")

elif menu == "Kasir":
    st.header("🧾 Kasir")
    df = load_data()
    if df.empty:
        st.warning("Belum ada produk untuk dibeli.")
    else:
        produk = st.selectbox("Pilih produk", df['Nama_Product'])
        info = df[df['Nama_Product'] == produk].iloc[0]
        stok = info['Kuantitas']
        harga = info['Harga']

        st.write(f"📦 Stok tersedia: {stok}")
        st.write(f"💰 Harga per item: Rp{int(harga):,}")

        if stok == 0:
            st.error("Stok produk ini habis, tidak bisa dibeli.")
        else:
            jumlah_beli = st.number_input("Jumlah beli", min_value=1, max_value=int(stok), step=1)
            if st.button("Tambah ke Keranjang"):
                for item in st.session_state.keranjang:
                    if item['nama'] == produk:
                        item['jumlah'] += jumlah_beli
                        break
                else:
                    st.session_state.keranjang.append({'nama': produk, 'jumlah': jumlah_beli, 'harga': harga})
                df.loc[df['Nama_Product'] == produk, 'Kuantitas'] -= jumlah_beli
                save_data(df)
                st.success("Produk ditambahkan ke keranjang!")

elif menu == "Lihat Struk":
    st.header("🧾 Struk Pembelian (Edit & Checkout)")
    keranjang = st.session_state.keranjang
    df = load_data()
    if not keranjang:
        st.info("Keranjang masih kosong.")
    else:
        total = 0
        for i, item in enumerate(keranjang):
            st.write(f"**{item['nama']}**")
            col1, col2 = st.columns([3, 1])
            jumlah_edit = col1.number_input("Jumlah", min_value=1, step=1, value=item['jumlah'], key=f"edit_{i}")
            if col2.button("Update", key=f"update_{i}"):
                perubahan = jumlah_edit - item['jumlah']
                stok_sekarang = df.loc[df['Nama_Product'] == item['nama'], 'Kuantitas'].values[0]
                if stok_sekarang - perubahan < 0:
                    st.error("Stok tidak cukup untuk update ini.")
                else:
                    df.loc[df['Nama_Product'] == item['nama'], 'Kuantitas'] -= perubahan
                    item['jumlah'] = jumlah_edit
                    save_data(df)
                    st.success("Jumlah berhasil diupdate.")

            subtotal = item['jumlah'] * item['harga']
            total += subtotal
            st.write(f"{item['nama']} x{item['jumlah']} @ Rp{item['harga']:,} = Rp{subtotal:,}")

        st.write(f"**Total Bayar: Rp{total:,}**")

        if st.button("Checkout"):
            filename = buat_struk(keranjang)
            st.session_state.keranjang = []
            st.download_button(
                label="📥 Unduh Struk (PDF)",
                data=open(filename, "rb"),
                file_name=filename,
                mime="application/pdf"
            )
