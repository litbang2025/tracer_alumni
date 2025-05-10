import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from io import BytesIO

# ----------------------------
# Fungsi validasi kolom
def validate_columns(df, required_cols):
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Kolom berikut tidak ditemukan: {', '.join(missing_cols)}")
        return False
    return True

# ----------------------------
# Main
st.set_page_config(page_title="Analisis Alumni & Stakeholder", layout="wide")

# Custom CSS
st.markdown("""
    <style>
        .main > div {
            padding-top: 0rem;
        }
        .css-1d391kg { padding-top: 1rem; }
        .sidebar .sidebar-content {
            background-color: #f0f2f6;
            padding: 1rem;
        }
        .stRadio > div {
            flex-direction: column;
        }
        .stRadio label {
            font-weight: 500;
            padding: 0.3rem 1rem;
            margin: 0.2rem 0;
            border: 1px solid #ccc;
            border-radius: 8px;
            background-color: white;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .stRadio label:hover {
            background-color: #e6f0ff;
            border-color: #1f77b4;
        }
        .stRadio input:checked + div > label {
            background-color: #1f77b4 !important;
            color: white;
        }
        .header-container {
            background-color: #1f77b4;
            color: white;
            padding: 1.5rem 2rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)
# HEADER UTAMA
st.markdown("""
    <div class='header-container'>
        <h1>📊 Dashboard Analisis Alumni & Stakeholder</h1>
        <p>Analisis interaktif data tracer alumni berdasarkan pekerjaan, gaji, kepuasan, dan lainnya.</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
st.sidebar.title("Menu")
menu = st.sidebar.radio("Pilih Menu", [
    "Upload Data",
    "Distribusi Pekerjaan",
    "Rata-rata Gaji",
    "Kepuasan Alumni",
    "Asal Unit",
    "Program Studi",
    "Distribusi Lembaga",
    "Relevansi Pendidikan",
    "Rekomendasi",
    "Tabel Data",
    "Unduh Laporan"
])

required_cols = [
    "id","nama","tahun_lulus","pekerjaan","industri","gaji","kepuasan",
    "asal_unit","relevansi_pendidikan","rekomendasi","jurusan",
    "nama_lembaga","jenjang"
]

if 'df' not in st.session_state:
    st.session_state.df = None

df = st.session_state.df

if menu == "Upload Data":
    st.header("Upload Data Tracer (.csv atau .xlsx)")
    uploaded_file = st.file_uploader("Unggah file data", type=["csv", "xlsx"])

    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            if validate_columns(df, required_cols):
                st.success("Data berhasil dimuat")
                st.session_state.df = df
                total = df.shape[0]
                st.write(f"Jumlah total data: {total}")
                st.subheader("Preview Data Sample")
                st.dataframe(df.head(20))
                st.subheader("Ringkasan Statistik Numerik")
                st.write(df.describe(include='all'))
            else:
                st.session_state.df = None
        except Exception as e:
            st.error(f"Gagal membaca file: {e}")
            st.session_state.df = None

if df is not None:
    tahun_lulus_unique = sorted(df['tahun_lulus'].dropna().unique())
    pekerjaan_unique = sorted(df['pekerjaan'].dropna().unique())
    jenjang_unique = sorted(df['jenjang'].dropna().unique())
    asal_unit_unique = sorted(df['asal_unit'].dropna().unique())

    selected_tahun = st.sidebar.selectbox("Pilih Tahun Lulus", ["All"] + tahun_lulus_unique)
    selected_pekerjaan = st.sidebar.multiselect("Pilih Pekerjaan", pekerjaan_unique, default=pekerjaan_unique)
    selected_jenjang = st.sidebar.selectbox("Pilih Jenjang", ["All"] + jenjang_unique)

    df_filtered = df.copy()
    if selected_tahun != "All":
        df_filtered = df_filtered[df_filtered["tahun_lulus"] == selected_tahun]
    if selected_pekerjaan:
        df_filtered = df_filtered[df_filtered["pekerjaan"].isin(selected_pekerjaan)]
    if selected_jenjang != "All":
        df_filtered = df_filtered[df_filtered["jenjang"] == selected_jenjang]

    if menu == "Distribusi Pekerjaan":
        st.header("Distribusi Pekerjaan")
        pekerjaan_count = df_filtered['pekerjaan'].value_counts().reset_index()
        pekerjaan_count.columns = ['Pekerjaan', 'Jumlah']
        fig = px.bar(pekerjaan_count, x='Pekerjaan', y='Jumlah', text='Jumlah',
                     title="Distribusi Pekerjaan", labels={'Jumlah': 'Jumlah Alumni', 'Pekerjaan': 'Pekerjaan'})
        fig.update_traces(textposition='outside')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "Rata-rata Gaji":
        st.header("Rata-rata Gaji Berdasarkan Pekerjaan")
        gaji_df = df_filtered[df_filtered['gaji'] > 0]
        fig = px.box(gaji_df, x='pekerjaan', y='gaji', points="all",
                     title="Distributsi Gaji per Pekerjaan", labels={'pekerjaan':'Pekerjaan', 'gaji':'Gaji (Rp)'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "Kepuasan Alumni":
        st.header("Kepuasan Alumni")
        kepuasan_count = df_filtered['kepuasan'].value_counts().sort_index().reset_index()
        kepuasan_count.columns = ['Skor Kepuasan', 'Jumlah']
        fig = px.bar(kepuasan_count, x='Skor Kepuasan', y='Jumlah',
                     title="Distribusi Skor Kepuasan Alumni")
        fig.update_traces(texttemplate='%{y}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "Asal Unit":
        st.header("Distribusi Asal Unit")
        unit_count = df_filtered['asal_unit'].value_counts().reset_index()
        unit_count.columns = ['Asal Unit', 'Jumlah']
        fig = px.bar(unit_count, x='Asal Unit', y='Jumlah',
                     title="Distribusi Asal Unit Alumni")
        fig.update_traces(texttemplate='%{y}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "Program Studi":
        st.header("Distribusi Program Studi")
        jurusan_count = df_filtered['jurusan'].value_counts().reset_index()
        jurusan_count.columns = ['Jurusan', 'Jumlah']
        st.table(jurusan_count)
        fig = px.bar(jurusan_count, x='Jurusan', y='Jumlah', text='Jumlah')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "Distribusi Lembaga":
        st.header("Distribusi Alumni per Lembaga per Tahun")
        df_lembaga = df_filtered.groupby(['jenjang', 'tahun_lulus']).size().reset_index(name='Jumlah')
        df_lembaga['Persen'] = (df_lembaga['Jumlah'] / df_lembaga.groupby('jenjang')['Jumlah'].transform('sum') * 100).round(1)
        fig = px.bar(df_lembaga, x='jenjang', y='Persen', color='tahun_lulus', barmode='group', text='Persen')
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_lembaga)

    elif menu == "Relevansi Pendidikan":
        st.header("Relevansi Pendidikan")
        relevansi_count = df_filtered['relevansi_pendidikan'].value_counts().reset_index()
        relevansi_count.columns = ['Relevansi', 'Jumlah']
        fig = px.bar(relevansi_count, x='Relevansi', y='Jumlah')
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "Rekomendasi":
        st.header("Rekomendasi Stakeholder")
        rekom_count = df_filtered['rekomendasi'].value_counts().reset_index()
        rekom_count.columns = ['Rekomendasi', 'Jumlah']
        fig = px.bar(rekom_count, x='Rekomendasi', y='Jumlah')
        st.plotly_chart(fig, use_container_width=True)

    elif menu == "Tabel Data":
        st.header("Data Alumni Lengkap")
        st.dataframe(df_filtered)
        st.subheader("Statistik Rangkuman per Pekerjaan")
        stat_df = df_filtered.groupby('pekerjaan').agg(
            Rata_Gaji=pd.NamedAgg(column='gaji', aggfunc='mean'),
            Median_Gaji=pd.NamedAgg(column='gaji', aggfunc='median'),
            Jumlah_Alumni=pd.NamedAgg(column='id', aggfunc='count')
        ).reset_index()
        st.dataframe(stat_df)

    elif menu == "Unduh Laporan":
        st.header("Unduh Data Alumni Filtered")
        towrite = BytesIO()
        df_filtered.to_csv(towrite, index=False)
        towrite.seek(0)
        st.download_button(label='Download CSV', data=towrite,
                           file_name='data_alumni_filtered.csv', mime='text/csv')
else:
    st.info("Silakan unggah data terlebih dahulu pada menu 'Upload Data'.")