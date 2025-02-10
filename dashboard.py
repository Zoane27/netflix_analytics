import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
import geopandas as gpd

# Membaca dataset
df = pd.read_csv('netflix_titles.csv')
df_filtered = df.copy()

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard Analisis Netflix", page_icon="📊", layout="wide")

# Set Style
sns.set(style="whitegrid")

#-------------------------------------------------------------------------------------#

# Konfigurasi Sidebar
st.sidebar.markdown('<style> .css-1aumxhk {background-color: #2c3e50;} </style>', unsafe_allow_html=True)
st.sidebar.title("🔧 Navigasi Dashboard")

sidebar_options = [
    "Beranda",
    "Pengenalan Dataset",
    "Statistik Dasar",
    "Distribusi Tahun Rilis",
    "Distribusi Rating",
    "Perbandingan Film vs TV Show",
    "10 Negara dengan Film/Show Terbanyak",
    "Jumlah Film/Show per Rating",
    "Analisis Durasi Film",
    "Distribusi Film per Negara (Geoanalisis)",
    "Analisis Klasterisasi (Data Mining)",
    "Detail Film"
]

sidebar_selection = st.sidebar.radio("Pilih Analisis", sidebar_options, help="Pilih jenis analisis yang ingin Anda lihat")

#-------------------------------------------------------------------------------------#

# Konfigurasi Filter
st.sidebar.markdown("---")
st.sidebar.subheader("🔎 Terapkan Filter pada Dataset")

filter_choice = st.sidebar.selectbox(
    "Pilih Kategori Filter", 
    ["Pilih Filter", "Tahun Rilis", "Rating", "Negara", "Durasi"],
    help="Pilih filter yang ingin diterapkan pada data"
)

# Parameter filter
filter_params = {}

if filter_choice != "Pilih Filter":
    selected_filter = filter_choice
else:
    selected_filter = None

if selected_filter == "Tahun Rilis":
    filter_params['year_filter'] = st.sidebar.slider(
        'Pilih Rentang Tahun Rilis', 
        min_value=int(df['release_year'].min()), 
        max_value=int(df['release_year'].max()), 
        value=(int(df['release_year'].min()), int(df['release_year'].max())), 
        step=1
    )
elif selected_filter == "Rating":
    filter_params['rating_filter'] = st.sidebar.multiselect(
        'Pilih Rating', 
        options=df['rating'].unique(), 
        default=df['rating'].unique()
    )
elif selected_filter == "Negara":
    filter_params['country_filter'] = st.sidebar.multiselect(
        'Pilih Negara', 
        options=df['country'].dropna().unique()
    )
elif selected_filter == "Durasi":
    filter_params['duration_filter'] = st.sidebar.slider(
        'Filter Durasi (Film) (menit)', 
        min_value=0, 
        max_value=300, 
        value=(0, 300), 
        step=1
    )

apply_filter = st.sidebar.button('Terapkan Filter')

st.sidebar.markdown(
    """
    <i><small><b>📌 Keterangan:</b> 
    Pilih filter yang diinginkan untuk menerapkan pembatasan pada data. Jangan lupa untuk klik <b>'Terapkan Filter'</b> setelah mengganti pilihan analisis untuk memperbarui hasil dengan filter yang baru.</small></i>
    """, unsafe_allow_html=True
)

if apply_filter:
    df_filtered = df.copy()
    
    if 'year_filter' in filter_params:
        df_filtered = df_filtered[df_filtered['release_year'].between(filter_params['year_filter'][0], filter_params['year_filter'][1])]
    if 'rating_filter' in filter_params:
        df_filtered = df_filtered[df_filtered['rating'].isin(filter_params['rating_filter'])]
    if 'country_filter' in filter_params:
        df_filtered = df_filtered[df_filtered['country'].isin(filter_params['country_filter'])]
    if 'duration_filter' in filter_params:
        movies_df = df_filtered[df_filtered['type'] == 'Movie']
        movies_df['duration'] = movies_df['duration'].str.replace(' min', '').astype(float)
        movies_df['duration'] = movies_df['duration'].fillna(0).astype(int)
        df_filtered = movies_df[movies_df['duration'].between(filter_params['duration_filter'][0], filter_params['duration_filter'][1])]
    
    #st.write("Data Setelah Difilter")
    #st.write(df_filtered)

#-------------------------------------------------------------------------------------#

# Layout Setup: Header
st.title('📊 Dashboard Analisis Netflix')


# 0. Beranda
if sidebar_selection == "Beranda":

    # Define the columns for the grid layout
    col1, col2, col3 = st.columns(3)

    # Define consistent figure size
    fig_size = (10, 6)

    # --- Column 1: Distribusi Tahun Rilis ---#
    with col1:
        release_year_counts = df_filtered["release_year"].value_counts().sort_index()
        
        fig, ax = plt.subplots(figsize=fig_size)  # Consistent figure size
        sns.lineplot(x=release_year_counts.index, y=release_year_counts.values, color="teal", ax=ax)
        ax.set_title("Distribusi Tahun Rilis", fontsize=18, fontweight='bold', color='teal')
        ax.set_xlabel("Tahun Rilis", fontsize=14)
        ax.set_ylabel("Jumlah Film/Show", fontsize=14)
        ax.grid(True, linestyle="--", alpha=0.7)
        st.pyplot(fig)

    # --- Column 2: Distribusi Rating ---#
    with col2:
        rating_counts = df_filtered["rating"].value_counts()
        rating_percent = (rating_counts / rating_counts.sum()) * 100

        fig, ax = plt.subplots(figsize=fig_size)  # Consistent figure size
        sns.barplot(x=rating_counts.index, y=rating_counts.values, palette="viridis", ax=ax)
        ax.set_title("Distribusi Rating", fontsize=18, fontweight='bold', color='royalblue')
        ax.set_xlabel("Rating", fontsize=14)
        ax.set_ylabel("Jumlah", fontsize=14)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=12)
        st.pyplot(fig)

    # --- Column 3: Perbandingan Film vs TV Show ---#
    with col3:
        type_counts = df_filtered["type"].value_counts()
        type_percent = (type_counts / type_counts.sum()) * 100

        fig, ax = plt.subplots(figsize=fig_size)  # Consistent figure size
        sns.barplot(x=type_counts.index, y=type_counts.values, palette="coolwarm", ax=ax)
        ax.set_title("Perbandingan Film vs TV Show", fontsize=18, fontweight='bold', color='darkorange')
        ax.set_xlabel("Jenis Konten", fontsize=14)
        ax.set_ylabel("Jumlah", fontsize=14)
        st.pyplot(fig)   

    # --- Column 1 (2): 10 Negara Teratas ---# 
    with col1:
        country_counts = df_filtered["country"].value_counts().head(10)

        fig, ax = plt.subplots(figsize=fig_size)  # Consistent figure size
        sns.barplot(x=country_counts.index, y=country_counts.values, palette="Blues_r", ax=ax)
        ax.set_title("10 Negara dengan Film/Show Terbanyak", fontsize=18, fontweight='bold', color='darkgreen')
        ax.set_xlabel("Negara", fontsize=14)
        ax.set_ylabel("Jumlah", fontsize=14)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=12)
        st.pyplot(fig)

    # --- Column 2 (2): Jumlah Film per Rating ---#
    with col2:
        rating_type_counts = df_filtered.groupby(["rating", "type"]).size().unstack()

        fig, ax = plt.subplots(figsize=(14, 7))  # Adjusted for consistency
        rating_type_counts.plot(kind="bar", stacked=True, ax=ax, cmap="viridis")
        ax.set_title("Jumlah Film dan TV Shows per Rating", fontsize=18, fontweight='bold', color='indigo')
        ax.set_xlabel("Rating", fontsize=14)
        ax.set_ylabel("Jumlah", fontsize=14)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=12)
        ax.legend(title="Tipe", bbox_to_anchor=(1, 1), fontsize=12)
        st.pyplot(fig)

    # --- Column 3 (2): Distribusi Durasi Film ---#
    with col3:
        movies_df = df_filtered[df_filtered["type"] == "Movie"]

        # Konversi durasi ke numerik
        movies_df["duration"] = (
            movies_df["duration"].astype(str).str.replace(" min", "").astype(float)
        )

        fig, ax = plt.subplots(figsize=fig_size)  # Consistent figure size
        sns.histplot(movies_df["duration"], bins=30, kde=True, color="royalblue", ax=ax)
        ax.set_title("Distribusi Durasi Film", fontsize=18, fontweight='bold', color='mediumslateblue')
        ax.set_xlabel("Durasi (menit)", fontsize=14)
        ax.set_ylabel("Frekuensi", fontsize=14)
        ax.grid(True, linestyle="--", alpha=0.7)
        st.pyplot(fig)

# 1. Pengenalan Dataset
elif sidebar_selection == "Pengenalan Dataset":
    st.header("📊 Pengenalan Dataset")
    st.write("Berikut adalah gambaran umum tentang dataset yang digunakan.")

    # Informasi Dataset
    st.subheader("📌 Informasi Dataset")
    st.write(f"- **Jumlah total data:** {len(df_filtered):,} baris")
    st.write(f"- **Jumlah kolom:** {len(df_filtered.columns)}")
    st.write("Gunakan opsi di bawah untuk menampilkan data yang tersedia.")

    st.divider()  # Garis pemisah

    # Opsi untuk menampilkan data
    show_all = st.checkbox("🔍 Tampilkan Seluruh Data")
    if show_all:
        st.subheader("📋 Seluruh Data")
        st.dataframe(df_filtered)
    else:
        st.subheader("📋 Cuplikan Data")
        num_rows = st.slider(
            "📌 Pilih jumlah baris yang ingin ditampilkan:",
            min_value=5,
            max_value=len(df_filtered),
            value=10,
        )
        st.dataframe(df_filtered.head(num_rows))

    st.divider()

    # Keterangan
    st.subheader("📖 Keterangan")
    st.markdown(
        """
        - **Jumlah total data:** Total baris data yang tersedia.
        - **Jumlah kolom:** Total fitur atau atribut dalam dataset.
        - **Tampilkan Seluruh Data:** Centang untuk melihat semua data.
        - **Cuplikan Data:** Menampilkan contoh data untuk memahami struktur dataset.
        """
    )

# 2. Statistik Dasar
elif sidebar_selection == "Statistik Dasar":
    st.header("📊 Statistik Dasar")
    st.write("Berikut adalah statistik deskriptif untuk dataset yang difilter:")

    # Tampilkan statistik deskriptif
    st.dataframe(df_filtered.describe())

    st.divider()

    # Keterangan
    st.subheader("📖 Keterangan")
    st.markdown(
        """
        - **Statistik Deskriptif:** Menunjukkan ringkasan statistik seperti rata-rata, standar deviasi, nilai minimum, dan maksimum untuk setiap kolom numerik.
        - Berguna untuk memahami distribusi dan karakteristik data.
        """
    )

# 3. Distribusi Tahun Rilis
elif sidebar_selection == "Distribusi Tahun Rilis":
    st.header("📅 Distribusi Tahun Rilis")
    st.write("Berikut adalah distribusi tahun rilis film dan acara TV.")

    # Hitung jumlah rilis per tahun
    release_year_counts = df_filtered["release_year"].value_counts().sort_index()

    # Tampilkan data dalam tabel
    st.subheader("📋 Data Jumlah Rilis per Tahun")
    st.dataframe(
        release_year_counts.rename_axis("Tahun Rilis").reset_index(name="Jumlah")
    )

    # Visualisasi Grafik Garis
    st.subheader("📊 Grafik Distribusi Tahun Rilis")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(
        x=release_year_counts.index, y=release_year_counts.values, color="teal", ax=ax
    )
    ax.set_title("Distribusi Tahun Rilis", fontsize=16, weight="bold")
    ax.set_xlabel("Tahun Rilis", fontsize=12)
    ax.set_ylabel("Jumlah Film/Show", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.7)
    st.pyplot(fig)

    st.divider()

    # Keterangan
    st.subheader("📖 Keterangan")
    st.markdown(
        """
        - **Tahun dengan Rilis Terbanyak:** Tahun dengan jumlah film/show terbanyak.
        - **Tahun dengan Rilis Terendah:** Tahun dengan jumlah film/show terendah.
        - **Tren Rilis:** Grafik garis menunjukkan perubahan jumlah rilis dari tahun ke tahun.
        """
    )

# 4. Distribusi Rating
elif sidebar_selection == "Distribusi Rating":
    st.header("⭐ Distribusi Rating")
    st.write("Berikut adalah distribusi rating film dan acara TV.")

    # Hitung jumlah dan persentase rating
    rating_counts = df_filtered["rating"].value_counts()
    rating_percent = (rating_counts / rating_counts.sum()) * 100

    # Dictionary Penjelasan Rating
    rating_descriptions = {
        "TV-MA": "Khusus dewasa, bisa mengandung kekerasan, bahasa kasar, atau tema dewasa.",
        "TV-14": "Dapat mengandung konten yang lebih kuat, tidak cocok untuk anak di bawah 14 tahun.",
        "TV-PG": "Bimbingan orang tua disarankan, mungkin mengandung adegan ringan yang kurang cocok untuk anak kecil.",
        "TV-Y7": "Cocok untuk anak di atas 7 tahun, bisa mengandung sedikit kekerasan ringan.",
        "TV-Y": "Aman untuk semua usia, ditujukan untuk anak-anak.",
        "R": "Dewasa (17+), bisa mengandung kekerasan, bahasa kasar, atau konten seksual.",
        "PG-13": "Bimbingan orang tua disarankan, mungkin ada unsur kekerasan atau tema dewasa ringan.",
        "PG": "Bisa ditonton semua usia, tapi bimbingan orang tua disarankan.",
        "TV-G": "General Audience - Untuk semua umur.",
        "G": "Cocok untuk semua umur, tanpa unsur yang berbahaya.",
        "TV-Y7-FV":"Youth 7-Fantasy Violence - Konten anak 7+ dengan kekerasan fantasi",
        "NC-17": "Tidak untuk usia di bawah 17 tahun, sering mengandung konten eksplisit.",
        "NR": "Belum diberi rating resmi.",
        "UR": "Rating tidak tersedia atau tidak diketahui.",
        "74 min": "Film Berdurasi 74 menit.",
        "84 min": "Film Berdurasi 84 menit.",
        "66 min" : "Film Berdurasi 66 menit"

    }

    # Menambahkan kolom deskripsi ke dalam dataframe
    df_rating = pd.DataFrame({
        "Jumlah": rating_counts,
        "Persentase (%)": rating_percent.round(2),
        "Keterangan": rating_counts.index.map(rating_descriptions)  # Menyesuaikan deskripsi
    })

    # Tampilkan data dalam tabel
    st.subheader("📋 Data Distribusi Rating")
    st.dataframe(df_rating)

    # Visualisasi Grafik Batang
    st.subheader("📊 Grafik Distribusi Rating")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=rating_counts.index, y=rating_counts.values, palette="viridis", ax=ax)
    ax.set_title("Distribusi Rating", fontsize=16, weight="bold")
    ax.set_xlabel("Rating", fontsize=12)
    ax.set_ylabel("Jumlah", fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    st.pyplot(fig)

    st.divider()

    # Keterangan
    st.subheader("📖 Keterangan")
    st.markdown(
        """
        - *Rating Terbanyak:* Rating yang paling umum dalam dataset.
        - *Rating Terendah:* Rating yang paling jarang muncul.
        - *Persentase:* Menunjukkan proporsi setiap rating dalam dataset.
        - *Keterangan:* Setiap rating memiliki makna tertentu terkait batasan usia dan kontennya.
        """
)

# 5. Perbandingan Film vs TV Show
elif sidebar_selection == "Perbandingan Film vs TV Show":
    st.header("🎬 Perbandingan Film vs TV Show")
    st.write("Berikut adalah perbandingan jumlah film dan acara TV.")

    # Hitung jumlah film dan TV show
    type_counts = df_filtered["type"].value_counts()
    type_percent = (type_counts / type_counts.sum()) * 100

    # Tampilkan data dalam tabel
    st.subheader("📋 Data Perbandingan")
    st.dataframe(
        pd.DataFrame(
            {"Jumlah": type_counts, "Persentase (%)": type_percent.round(2)}
        )
    )

    # Visualisasi Grafik Batang
    st.subheader("📊 Grafik Perbandingan")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=type_counts.index, y=type_counts.values, palette="coolwarm", ax=ax)
    ax.set_title("Perbandingan Film vs TV Show", fontsize=16, weight="bold")
    ax.set_xlabel("Jenis Konten", fontsize=12)
    ax.set_ylabel("Jumlah", fontsize=12)
    st.pyplot(fig)

    st.divider()

    # Keterangan
    st.subheader("📖 Keterangan")
    st.markdown(
        """
        - **Film vs TV Show:** Menunjukkan apakah dataset lebih didominasi oleh film atau acara TV.
        - **Persentase:** Menunjukkan proporsi film dan acara TV dalam dataset.
        """
    )

# 6. 10 Negara dengan Film/Show Terbanyak
elif sidebar_selection == "10 Negara dengan Film/Show Terbanyak":
    st.header("🌍 10 Negara dengan Film/Show Terbanyak")
    st.write("Berikut adalah 10 negara dengan jumlah film dan acara TV terbanyak.")

    # Hitung jumlah film/show per negara
    country_counts = df_filtered["country"].value_counts().head(10)

    # Tampilkan data dalam tabel
    st.subheader("📋 Data 10 Negara Teratas")
    st.dataframe(country_counts.rename_axis("Negara").reset_index(name="Jumlah"))

    # Visualisasi Grafik Batang
    st.subheader("📊 Grafik 10 Negara Teratas")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=country_counts.index, y=country_counts.values, palette="Blues_r", ax=ax)
    ax.set_title("10 Negara dengan Film/Show Terbanyak", fontsize=16, weight="bold")
    ax.set_xlabel("Negara", fontsize=12)
    ax.set_ylabel("Jumlah", fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    st.pyplot(fig)

    st.divider()

    # Keterangan
    st.subheader("📖 Keterangan")
    st.markdown(
        """
        - **Negara Teratas:** Menunjukkan negara dengan produksi film/show terbanyak.
        - **Jumlah:** Menunjukkan berapa banyak film/show yang diproduksi oleh setiap negara.
        """
    )

# 7. Jumlah Film/Show per Rating
elif sidebar_selection == "Jumlah Film/Show per Rating":
    st.header("🔢 Jumlah Film/Show per Rating")
    st.write("Berikut adalah jumlah film dan acara TV berdasarkan rating.")

    # Hitung jumlah film dan TV show per rating
    rating_type_counts = df_filtered.groupby(["rating", "type"]).size().unstack()

    # Tampilkan data dalam tabel
    st.subheader("📋 Data Jumlah per Rating")
    st.dataframe(rating_type_counts)

    # Visualisasi Grafik Batang Bertumpuk
    st.subheader("📊 Grafik Jumlah per Rating")
    fig, ax = plt.subplots(figsize=(14, 7))
    rating_type_counts.plot(kind="bar", stacked=True, ax=ax, cmap="viridis")
    ax.set_title("Jumlah Film dan TV Shows per Rating", fontsize=16, weight="bold")
    ax.set_xlabel("Rating", fontsize=12)
    ax.set_ylabel("Jumlah", fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.legend(title="Tipe", bbox_to_anchor=(1, 1))
    st.pyplot(fig)

    st.divider()

    # Keterangan
    st.subheader("📖 Keterangan")
    st.markdown(
        """
        - **Rating Terbanyak:** Menunjukkan rating yang paling umum untuk film dan acara TV.
        - **Perbandingan Film vs TV Show:** Menunjukkan apakah rating tertentu lebih umum untuk film atau acara TV.
        """
    )

# 8. Analisis Durasi Film
elif sidebar_selection == "Analisis Durasi Film":
    st.header("⏳ Analisis Durasi Film")
    st.write("Berikut adalah analisis durasi film dalam dataset.")

    # Filter hanya untuk film
    movies_df = df_filtered[df_filtered["type"] == "Movie"]

    if not movies_df.empty:
        # Konversi durasi ke numerik
        movies_df["duration"] = (
            movies_df["duration"].astype(str).str.replace(" min", "").astype(float)
        )

        # Hitung statistik durasi
        avg_duration = movies_df["duration"].mean()
        min_duration = movies_df["duration"].min()
        max_duration = movies_df["duration"].max()

        # Tampilkan statistik
        st.subheader("📋 Statistik Durasi Film")
        st.write(f"- **Rata-rata Durasi:** {avg_duration:.2f} menit")
        st.write(f"- **Durasi Terpendek:** {min_duration} menit")
        st.write(f"- **Durasi Terpanjang:** {max_duration} menit")

        # Visualisasi Histogram
        st.subheader("📊 Grafik Distribusi Durasi Film")
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.histplot(movies_df["duration"], bins=30, kde=True, color="royalblue", ax=ax)
        ax.set_title("Distribusi Durasi Film", fontsize=16, weight="bold")
        ax.set_xlabel("Durasi (menit)", fontsize=12)
        ax.set_ylabel("Frekuensi", fontsize=12)
        ax.grid(True, linestyle="--", alpha=0.7)
        st.pyplot(fig)

        st.divider()

        # Keterangan
        st.subheader("📖 Keterangan")
        st.markdown(
            """
            - **Rata-rata Durasi:** Durasi rata-rata film dalam dataset.
            - **Durasi Terpendek dan Terpanjang:** Menunjukkan rentang durasi film.
            - **Distribusi Durasi:** Histogram menunjukkan sebaran durasi film.
            """
        )
    else:
        st.warning("⚠ Tidak ada data film yang tersedia.")

#-------------------------------------------------------------------------------------#

# 9. Fungsi untuk analisis geoanalisis
def analisis_geoanalisis(df):
    shapefile_path = r'ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp'
    world = gpd.read_file(shapefile_path)
    kolom_negara = 'NAME'

    jumlah_negara = df['country'].value_counts()
    df_geo_negara = pd.DataFrame(jumlah_negara).reset_index()
    df_geo_negara.columns = ['Negara', 'Jumlah']
    
    df_geo_negara['geometry'] = df_geo_negara['Negara'].apply(
        lambda x: world[world[kolom_negara] == x].geometry.values[0] if x in world[kolom_negara].values else None
    )
    
    gdf = gpd.GeoDataFrame(df_geo_negara, geometry='geometry')
    
    st.header('🔍 Distribusi Film per Negara (Geoanalisis) ')
    fig, ax = plt.subplots(figsize=(15, 10))
    world.plot(ax=ax, color='lightgrey')
    gdf.plot(ax=ax, marker='o', color='red', markersize=gdf['Jumlah']*10, alpha=0.7)
    ax.set_title('Distribusi Negara Berdasarkan Jumlah Film/TV Shows', fontsize=16)
    st.pyplot(fig)

    st.divider()

    # Keterangan
    st.subheader("📖 Keterangan")
    st.markdown(
        """
        - **Distribusi Negara:** Peta menunjukkan distribusi negara berdasarkan jumlah film/TV shows yang diproduksi.
        - **Ukuran Titik:** Ukuran titik pada peta menunjukkan jumlah film/TV shows yang diproduksi oleh negara tersebut. Semakin besar titik, semakin banyak jumlah produksinya.
        - **Warna Titik:** Titik berwarna merah menunjukkan lokasi negara yang memiliki produksi film/TV shows.
        """
    )
 
# 10. Fungsi untuk analisis klasterisasi
def analisis_klasterisasi(df):
    df_movies = df[df['type'] == 'Movie'].dropna(subset=['duration', 'rating'])

    # Memetakan rating ke nilai numerik
    rating_map = {'G': 1, 'PG': 2, 'PG-13': 3, 'R': 4, 'NC-17': 5}
    df_movies['rating_num'] = df_movies['rating'].map(rating_map)

    # Konversi durasi ke angka
    df_movies['duration'] = df_movies['duration'].str.replace(' min', '', regex=True).astype(float)

    # Isi NaN dengan median masing-masing kolom
    df_movies['rating_num'].fillna(df_movies['rating_num'].median(), inplace=True)
    df_movies['duration'].fillna(df_movies['duration'].median(), inplace=True)

    # Fitur untuk klasterisasi
    fitur = df_movies[['rating_num', 'duration']].dropna().values  # Hapus NaN sebelum klasterisasi

    # Pastikan tidak ada NaN di data
    if fitur.shape[0] == 0:
        st.warning("Data tidak cukup untuk klasterisasi. Periksa kembali dataset Anda.")
        return

    # KMeans Clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    df_movies = df_movies.loc[df_movies[['rating_num', 'duration']].dropna().index]  # Sinkronisasi indeks
    df_movies['Cluster'] = kmeans.fit_predict(fitur)

    # Header dan deskripsi
    st.header('🔍 Analisis Klasterisasi Film Berdasarkan Rating dan Durasi')
    st.markdown("""
    Dalam analisis ini, kami melakukan klasterisasi pada film berdasarkan dua fitur utama: **Rating** dan **Durasi**. 
    Klasterisasi ini bertujuan untuk mengelompokkan film berdasarkan kesamaan dalam kedua fitur tersebut, memberikan wawasan tentang pola distribusi film.
    """)

    # Menampilkan hasil klasterisasi
    st.write("### Hasil Klasterisasi:")
    st.dataframe(df_movies[['title', 'rating', 'duration', 'Cluster']].head(10).style
                 .background_gradient(cmap="Blues")
                 .set_properties(**{'text-align': 'center'}))
    
    # Plot hasil klasterisasi
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df_movies, x='rating_num', y='duration', hue='Cluster', palette="viridis", s=100, edgecolor="w", ax=ax)
    ax.set_title('Klasterisasi Film Berdasarkan Rating dan Durasi', fontsize=16, weight='bold', color="#2f4f4f")
    ax.set_xlabel('Rating', fontsize=12, color="#3e4a59")
    ax.set_ylabel('Durasi (Menit)', fontsize=12, color="#3e4a59")
    ax.legend(title="Cluster", title_fontsize='13', loc='upper right', fontsize='11', frameon=False)
    ax.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig)

    st.divider()

    # Keterangan
    st.subheader("📖 Keterangan")
    st.markdown(
        """
        - **Cluster 0:** Film dengan rating rendah dan durasi pendek.
        - **Cluster 1:** Film dengan rating menengah dan durasi sedang.
        - **Cluster 2:** Film dengan rating tinggi dan durasi panjang.
        """
    )

# Menambahkan logika untuk menampilkan analisis lanjutan berdasarkan pilihan
if sidebar_selection == "Distribusi Film per Negara (Geoanalisis)":
    analisis_geoanalisis(df_filtered)

elif sidebar_selection == "Analisis Klasterisasi (Data Mining)":
    analisis_klasterisasi(df_filtered)

#-------------------------------------------------------------------------------------#

# 11. Film Details
elif sidebar_selection == "Detail Film":
    st.header("🎬 Detail Film")
    st.write("Gunakan filter di bawah ini untuk menemukan film yang ingin Anda lihat detailnya.")
    
    # Filter untuk detail film
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.selectbox("📽️ Pilih Tipe", ["Semua"] + df['type'].dropna().unique().tolist(), key="type_filter")
    with col2:
        country_filter = st.selectbox("🌍 Pilih Negara", ["Semua"] + df['country'].dropna().unique().tolist(), key="country_filter")
    with col3:
        year_filter = st.selectbox("📅 Pilih Tahun Rilis", ["Semua"] + sorted(df['release_year'].dropna().unique().tolist(), reverse=True), key="year_filter")
    
    # Terapkan filter
    df_filtered = df.copy()
    if type_filter != "Semua":
        df_filtered = df_filtered[df_filtered['type'] == type_filter]
    if country_filter != "Semua":
        df_filtered = df_filtered[df_filtered['country'] == country_filter]
    if year_filter != "Semua":
        df_filtered = df_filtered[df_filtered['release_year'] == year_filter]
    
    # Cek apakah hasil filter kosong
    if df_filtered.empty:
        st.warning("⚠️ Tidak ada film yang sesuai dengan filter yang dipilih.")
    else:
        film_titles = df_filtered['title'].dropna().unique()
        if len(film_titles) == 0:
            st.warning("⚠️ Tidak ada film yang tersedia setelah filter diterapkan.")
        else:
            selected_film = st.selectbox("🎥 Pilih Film", film_titles, key="film_select")
            
            if selected_film:
                selected_film_data = df_filtered[df_filtered['title'] == selected_film].iloc[0]
                st.subheader("Informasi Film")
                st.markdown(f"**👑 Judul:** {selected_film_data['title']}")
                st.markdown(f"**📽️ Tipe:** {selected_film_data['type']}")
                st.markdown(f"**🎬 Sutradara:** {selected_film_data['director'] if pd.notna(selected_film_data['director']) else 'Tidak tersedia'}")
                st.markdown(f"**🎭 Pemeran:** {selected_film_data['cast'] if pd.notna(selected_film_data['cast']) else 'Tidak tersedia'}")
                st.markdown(f"**🌍 Negara:** {selected_film_data['country']}")
                st.markdown(f"**📅 Tanggal Ditambahkan:** {selected_film_data['date_added'] if pd.notna(selected_film_data['date_added']) else 'Tidak tersedia'}")
                st.markdown(f"**📅 Tahun Rilis:** {selected_film_data['release_year']}")
                st.markdown(f"**⭐ Rating:** {selected_film_data['rating'] if pd.notna(selected_film_data['rating']) else 'Tidak tersedia'}")
                st.markdown(f"**⏳ Durasi:** {selected_film_data['duration'] if pd.notna(selected_film_data['duration']) else 'Tidak tersedia'}")
                st.markdown(f"**🎬 Kategori:** {selected_film_data['listed_in'] if pd.notna(selected_film_data['listed_in']) else 'Tidak tersedia'}")
                st.markdown(f"**📝 Deskripsi:** {selected_film_data['description']}")
                st.divider()


    # Keterangan
    st.subheader("📖 Keterangan")
    st.markdown(
        """
        - **Judul:** Nama film yang dipilih.
        - **Tipe:** Jenis konten (Film atau TV Show).
        - **Sutradara:** Nama sutradara film (jika tersedia).
        - **Pemeran:** Daftar pemeran film (jika tersedia).
        - **Negara:** Negara asal produksi film.
        - **Tanggal Ditambahkan:** Tanggal film ditambahkan ke platform (jika tersedia).
        - **Tahun Rilis:** Tahun film dirilis.
        - **Rating:** Rating film (jika tersedia).
        - **Durasi:** Durasi film atau jumlah episode untuk TV Show (jika tersedia).
        - **Kategori:** Genre atau kategori film.
        - **Deskripsi:** Sinopsis atau deskripsi singkat film.
        """
    )
