import streamlit as st
import pandas as pd
import os
from fpdf import FPDF

CSV_PATH = 'produkMart.csv'
GAMBAR_FOLDER = 'images'

def load_data():
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH, delimiter='\t')
        df.columns = df.columns.str.strip()
        if 'Harga (Rp)' in df.columns:
            df.rename(columns={'Harga (Rp)': 'Harga'}, inplace=True)
        return df
    else:
        return pd.DataFrame(columns=['Nama_Product', 'Kuantitas', 'Harga'])

def save_data(df):
    df.to_csv(CSV_PATH, sep='\t', index=False)

def main():
    st.set_page_config(layout="wide")
    st.title("🛒 PTOIR MART")

    menu = st.sidebar.selectbox("Menu", [
        "Lihat Produk", "Tambah Stok", "Update Harga", "Kasir", "Lihat Struk"])

    if "cart" not in st.session_state:
        st.session_state.cart = {}

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

        st.markdown("### 📋 Tabel Produk")
        with st.container():
            st.markdown("""
                <div style="border:2px solid #ccc; padding:15px; border-radius:10px;">
                    <table style="width:100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background-color:#f2f2f2;">
                                <th style="text-align:left; padding:8px;">No</th>
                                <th style="text-align:left; padding:8px;">Nama Produk</th>
                                <th style="text-align:left; padding:8px;">Lihat Produk</th>
                                <th style="text-align:left; padding:8px;">Stok</th>
                                <th style="text-align:left; padding:8px;">Harga</th>
                            </tr>
                        </thead>
                        <tbody>
            """, unsafe_allow_html=True)

            for idx, row in df.iterrows():
                nama_produk = row['Nama_Product']
                harga = f"Rp{int(row['Harga']):,}"
                jumlah = row['Kuantitas']
                lihat_key = f"lihat_btn_{idx}"

                st.markdown(f"""
                    <tr>
                        <td style="padding:8px;">{idx+1}</td>
                        <td style="padding:8px;">{nama_produk}</td>
                        <td style="padding:8px;">[Lihat](#{lihat_key})</td>
                        <td style="padding:8px;">{jumlah}</td>
                        <td style="padding:8px;">{harga}</td>
                    </tr>
                """, unsafe_allow_html=True)

            st.markdown("""
                        </tbody>
                    </table>
                </div>
            """, unsafe_allow_html=True)

        # Tombol Lihat Produk (asli)
        for idx, row in df.iterrows():
            nama_produk = row['Nama_Product']
            lihat_key = f"lihat_{idx}"
            if st.button(f"Lihat {nama_produk}", key=lihat_key):
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

        if st.session_state.selected_image:
            with st.expander(f"📸 {st.session_state.selected_caption}", expanded=True):
                st.image(st.session_state.selected_image, caption=st.session_state.selected_caption, use_column_width=True)
        elif st.session_state.selected_caption == "Gambar tidak ditemukan":
            st.error("Gambar tidak ditemukan.")
        
    elif menu == "Tambah Stok":
        st.header("📥 Tambah Stok Produk")
        df = load_data()
        if df.empty:
            st.warning("Belum ada produk.")
        else:
            produk = st.selectbox("Pilih produk", df['Nama_Product'])
            stok_sekarang = df[df['Nama_Product'] == produk]['Kuantitas'].values[0]
            st.info(f"Stok saat ini: {stok_sekarang}")
            jumlah = st.number_input("Jumlah stok yang ingin ditambahkan", min_value=1, step=1)
            if st.button("Tambah Stok"):
                idx = df[df['Nama_Product'] == produk].index[0]
                df.at[idx, 'Kuantitas'] = int(df.at[idx, 'Kuantitas']) + jumlah
                save_data(df)
                st.success(f"Stok produk '{produk}' berhasil ditambah sebanyak {jumlah}.")
                st.rerun()

    elif menu == "Update Harga":
        st.header("💸 Update Harga Produk")
        df = load_data()
        if df.empty:
            st.warning("Belum ada produk.")
        else:
            produk = st.selectbox("Pilih produk", df['Nama_Product'])
            harga_sekarang = df[df['Nama_Product'] == produk]['Harga'].values[0]
            st.info(f"Harga saat ini: Rp{harga_sekarang:,}")
            harga_baru = st.number_input("Harga baru (Rp)", min_value=0, step=1000)
            if st.button("Update Harga"):
                idx = df[df['Nama_Product'] == produk].index[0]
                df.at[idx, 'Harga'] = harga_baru
                save_data(df)
                st.success(f"Harga produk '{produk}' berhasil diupdate ke Rp{harga_baru:,}.")
                st.rerun()

    elif menu == "Kasir":
        st.header("🧾 Kasir")
        df = load_data()
        if df.empty:
            st.warning("Belum ada produk.")
        else:
            produk = st.selectbox("Pilih produk", df['Nama_Product'])
            idx = df[df['Nama_Product'] == produk].index[0]
            stok = int(df.at[idx, 'Kuantitas'])
            harga = int(df.at[idx, 'Harga'])

            # Tampilkan info stok dan harga
            st.write(f"📦 **Stok tersedia:** {stok}")
            st.write(f"💰 **Harga per item:** Rp{harga:,}")

            # Cegah error saat stok habis
            if stok == 0:
                st.warning("Stok produk ini habis, tidak bisa dibeli.")
            else:
                jumlah_beli = st.number_input("Jumlah beli", min_value=1, max_value=stok, step=1)

                if st.button("Tambah ke Keranjang"):
                    if jumlah_beli <= stok:
                        st.session_state.cart[produk] = st.session_state.cart.get(produk, 0) + jumlah_beli
                        df.at[idx, 'Kuantitas'] = stok - jumlah_beli
                        save_data(df)
                        st.success(f"'{produk}' sebanyak {jumlah_beli} ditambahkan ke keranjang.")
                        st.rerun()
                    else:
                        st.error("Jumlah beli melebihi stok.")

            if st.session_state.cart:
                st.subheader("🛍️ Keranjang Belanja")
                total_bayar = 0
                for produk_keranjang, jumlah in st.session_state.cart.items():
                    harga_item = df.loc[df['Nama_Product'] == produk_keranjang, 'Harga'].values[0]
                    subtotal = harga_item * jumlah
                    st.write(f"{produk_keranjang} x{jumlah} @ Rp{harga_item:,} = Rp{subtotal:,}")
                    total_bayar += subtotal
                st.write(f"**Total bayar: Rp{total_bayar:,}**")

            if st.button("Reset Keranjang"):
                df = load_data()
                for produk_keranjang, jumlah in st.session_state.cart.items():
                    idx = df[df['Nama_Product'] == produk_keranjang].index[0]
                    df.at[idx, 'Kuantitas'] += jumlah  # Kembalikan stok
                save_data(df)
                st.session_state.cart = {}
                st.success("Keranjang berhasil dibersihkan dan stok dikembalikan.")
                st.rerun()



    elif menu == "Lihat Struk":
        df = load_data()
        if not st.session_state.cart:
            st.info("Keranjang kosong.")
        else:
            st.header("🧾 Struk Pembelian (Edit & Checkout)")
            total_bayar = 0

            for produk_keranjang, jumlah in st.session_state.cart.items():
                harga = df.loc[df['Nama_Product'] == produk_keranjang, 'Harga'].values[0]
                subtotal = harga * jumlah

                st.write(f"**{produk_keranjang}**")
                col1, col2 = st.columns([2, 1])
                with col1:
                    new_jumlah = st.number_input(
                        f"Jumlah", min_value=1,
                        max_value=int(df[df['Nama_Product'] == produk_keranjang]['Kuantitas'].values[0]) + jumlah,
                        value=jumlah,
                        key=f"edit_{produk_keranjang}"
                    )
                with col2:
                    if st.button("Update", key=f"update_{produk_keranjang}"):
                        stok_awal = int(df.loc[df['Nama_Product'] == produk_keranjang, 'Kuantitas'].values[0])
                        perubahan = new_jumlah - jumlah
                        df.loc[df['Nama_Product'] == produk_keranjang, 'Kuantitas'] = stok_awal - perubahan
                        save_data(df)
                        st.session_state.cart[produk_keranjang] = new_jumlah
                        st.success(f"Jumlah '{produk_keranjang}' diperbarui menjadi {new_jumlah}.")
                        st.rerun()

                st.write(f"{jumlah} x Rp{harga:,} = Rp{subtotal:,}")
                total_bayar += subtotal

            st.write(f"**Total Bayar: Rp{total_bayar:,}**")

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Struk Pembelian Ptoirmart", ln=True, align='C')
            pdf.ln(10)

            for produk_keranjang, jumlah in st.session_state.cart.items():
                harga = df.loc[df['Nama_Product'] == produk_keranjang, 'Harga'].values[0]
                subtotal = harga * jumlah
                line = f"{produk_keranjang} x{jumlah} @ Rp{harga:,} = Rp{subtotal:,}"
                pdf.cell(200, 10, txt=line, ln=True)

            pdf.ln(10)
            pdf.set_font("Arial", "B", size=12)
            pdf.cell(200, 10, txt=f"Total Bayar: Rp{total_bayar:,}", ln=True)

            pdf_path = "struk_belanja.pdf"
            pdf.output(pdf_path)

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Checkout",
                    data=f,
                    file_name="struk_belanja.pdf",
                    mime="application/pdf"
                )

if __name__ == "__main__":
    main()
