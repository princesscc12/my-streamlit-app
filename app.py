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

    df = load_data()

    if menu == "Kasir":
        st.header("🧾 Kasir")
        if df.empty:
            st.warning("Belum ada produk.")
        else:
            produk = st.selectbox("Pilih produk", df['Nama_Product'])
            idx = df[df['Nama_Product'] == produk].index[0]
            stok = int(df.at[idx, 'Kuantitas'])
            st.write(f"Stok tersedia: {stok}")

            if stok > 0:
                jumlah_beli = st.number_input("Jumlah beli", min_value=1, max_value=stok, step=1)
                if st.button("Tambah ke Keranjang"):
                    st.session_state.cart[produk] = st.session_state.cart.get(produk, 0) + jumlah_beli
                    df.at[idx, 'Kuantitas'] = stok - jumlah_beli
                    save_data(df)
                    st.success(f"'{produk}' sebanyak {jumlah_beli} ditambahkan ke keranjang.")
                    st.rerun()
            else:
                st.info("Stok habis, tidak bisa menambahkan ke keranjang.")

            if st.session_state.cart:
                st.subheader("🛍️ Keranjang Belanja")
                total_bayar = 0

                for produk_keranjang, jumlah in list(st.session_state.cart.items()):
                    harga = df.loc[df['Nama_Product'] == produk_keranjang, 'Harga'].values[0]
                    subtotal = harga * jumlah
                    col1, col2, col3 = st.columns([3, 2, 2])
                    col1.write(f"{produk_keranjang} @ Rp{harga:,}")
                    with col2:
                        new_jumlah = st.number_input(
                            f"Jumlah '{produk_keranjang}'", min_value=1,
                            value=jumlah, key=f"edit_{produk_keranjang}"
                        )
                    with col3:
                        if st.button("Update", key=f"update_{produk_keranjang}"):
                            stok_sisa = int(df[df['Nama_Product'] == produk_keranjang]['Kuantitas'].values[0])
                            total_kembali = jumlah  # jumlah sebelum diubah
                            perubahan = new_jumlah - jumlah
                            if perubahan > stok_sisa:
                                st.warning(f"Stok tidak mencukupi untuk menambah {perubahan} item.")
                            else:
                                df.loc[df['Nama_Product'] == produk_keranjang, 'Kuantitas'] -= perubahan
                                save_data(df)
                                st.session_state.cart[produk_keranjang] = new_jumlah
                                st.success(f"Jumlah '{produk_keranjang}' diperbarui menjadi {new_jumlah}.")
                                st.rerun()

                    st.write(f"{jumlah} x Rp{harga:,} = Rp{subtotal:,}")
                    total_bayar += subtotal

                st.write(f"**Total bayar: Rp{total_bayar:,}**")

                if st.button("Reset Keranjang"):
                    st.session_state.cart = {}
                    st.success("Keranjang berhasil dibersihkan.")
                    st.rerun()

    elif menu == "Lihat Struk":
        st.header("🧾 Struk Pembelian")
        if not st.session_state.cart:
            st.info("Keranjang kosong.")
        else:
            total_bayar = 0
            for produk_keranjang, jumlah in st.session_state.cart.items():
                harga = df.loc[df['Nama_Product'] == produk_keranjang, 'Harga'].values[0]
                subtotal = harga * jumlah
                st.write(f"{produk_keranjang} x{jumlah} @ Rp{harga:,} = Rp{subtotal:,}")
                total_bayar += subtotal
            st.write(f"**Total bayar: Rp{total_bayar:,}**")

            # Auto generate and download PDF on button click
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
