import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

# Load produk
file_path = 'produkMart.csv'
df = pd.read_csv(file_path)

# Inisialisasi session_state untuk keranjang jika belum ada
if 'cart' not in st.session_state:
    st.session_state.cart = {}

def save_data(dataframe):
    dataframe.to_csv(file_path, index=False)

def main():
    st.title("🛒 PTOIR MART")

    menu = st.sidebar.selectbox("Menu", ["Lihat Produk", "Tambah Stok", "Update Harga", "Kasir", "Lihat Struk"])

    if menu == "Lihat Produk":
        st.subheader("📦 Daftar Produk")
        st.dataframe(df)

    elif menu == "Tambah Stok":
        st.subheader("➕ Tambah Stok Produk")
        produk = st.selectbox("Pilih Produk", df['Nama_Product'])
        jumlah = st.number_input("Jumlah Tambahan", min_value=1, step=1)
        if st.button("Tambah"):
            df.loc[df['Nama_Product'] == produk, 'Kuantitas'] += jumlah
            save_data(df)
            st.success(f"Stok untuk '{produk}' berhasil ditambahkan.")

    elif menu == "Update Harga":
        st.subheader("💰 Update Harga Produk")
        produk = st.selectbox("Pilih Produk", df['Nama_Product'])
        harga_baru = st.number_input("Harga Baru", min_value=100, step=100)
        if st.button("Update"):
            df.loc[df['Nama_Product'] == produk, 'Harga'] = harga_baru
            save_data(df)
            st.success(f"Harga untuk '{produk}' berhasil diperbarui.")

    elif menu == "Kasir":
        st.subheader("🛒 Kasir")
        for i, row in df.iterrows():
            st.write(f"**{row['Nama_Product']}** - Stok: {row['Kuantitas']} - Harga: Rp{row['Harga']:,}")
            col1, col2 = st.columns([2, 1])
            with col1:
                jumlah_beli = st.number_input(f"Jumlah beli {row['Nama_Product']}", min_value=0, max_value=row['Kuantitas'], step=1, key=row['Nama_Product'])
            with col2:
                if st.button("Tambah ke Keranjang", key=f"btn_{row['Nama_Product']}"):
                    if jumlah_beli > 0:
                        if row['Nama_Product'] in st.session_state.cart:
                            st.session_state.cart[row['Nama_Product']] += jumlah_beli
                        else:
                            st.session_state.cart[row['Nama_Product']] = jumlah_beli
                        df.loc[i, 'Kuantitas'] -= jumlah_beli
                        save_data(df)
                        st.success(f"{jumlah_beli} item '{row['Nama_Product']}' ditambahkan ke keranjang.")

    elif menu == "Lihat Struk":
        st.header("🧾 Struk Pembelian (Edit & Checkout)")

        if not st.session_state.cart:
            st.info("Keranjang kosong.")
        else:
            total_bayar = 0

            for produk_keranjang, jumlah in list(st.session_state.cart.items()):
                harga = df.loc[df['Nama_Product'] == produk_keranjang, 'Harga'].values[0]
                subtotal = harga * jumlah

                col1, col2, col3 = st.columns([4, 2, 2])
                col1.write(f"**{produk_keranjang}** @ Rp{harga:,}")
                with col2:
                    new_jumlah = st.number_input(
                        f"Jumlah '{produk_keranjang}'", min_value=1,
                        value=jumlah, key=f"struk_jumlah_{produk_keranjang}"
                    )
                with col3:
                    if st.button("Update", key=f"struk_update_{produk_keranjang}"):
                        stok_tersedia = int(df[df['Nama_Product'] == produk_keranjang]['Kuantitas'].values[0])
                        perubahan = new_jumlah - jumlah
                        if perubahan > stok_tersedia:
                            st.warning(f"Stok '{produk_keranjang}' tidak mencukupi untuk menambah {perubahan} item.")
                        else:
                            df.loc[df['Nama_Product'] == produk_keranjang, 'Kuantitas'] -= perubahan
                            st.session_state.cart[produk_keranjang] = new_jumlah
                            save_data(df)
                            st.success(f"Jumlah '{produk_keranjang}' diperbarui menjadi {new_jumlah}.")
                            st.rerun()

                st.write(f"{jumlah} x Rp{harga:,} = Rp{subtotal:,}")
                total_bayar += subtotal

            st.write(f"**Total Bayar: Rp{total_bayar:,}**")

            # Generate PDF
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

if __name__ == '__main__':
    main()
