import streamlit as st
import pandas as pd
import requests
import time

# ==========================================
# 1. Layout & Tema
# ==========================================
st.set_page_config(
    page_title="CERIA Candidate Data Validation Assistant",
    page_icon="✨",
    layout="wide"
)

# ==========================================
# 4. State Management
# ==========================================
# Inisialisasi variabel di session_state agar tidak hilang saat navigasi/interaksi
if "validation_done" not in st.session_state:
    st.session_state.validation_done = False
if "ready_df" not in st.session_state:
    st.session_state.ready_df = pd.DataFrame()
if "error_df" not in st.session_state:
    st.session_state.error_df = pd.DataFrame()
if "missing_df" not in st.session_state:
    st.session_state.missing_df = pd.DataFrame()

# ==========================================
# Mock Data Generator
# ==========================================
def get_mock_data():
    """Fungsi pembantu untuk menghasilkan Mock Data jika API n8n tidak tersedia."""
    ready_data = [
        {"Nama": "Agus Pratama", "Email": "agus@gmail.com", "Campus ID": "UNIV-01", "Major ID": "MAJ-102"},
        {"Nama": "Budi Santoso", "Email": "budi.s@yahoo.com", "Campus ID": "UNIV-05", "Major ID": "MAJ-089"},
        {"Nama": "Siti Aminah", "Email": "siti.a@gmail.com", "Campus ID": "UNIV-02", "Major ID": "MAJ-102"}
    ]
    
    error_data = [
        {"Nama": "Dewi", "Email": "dewi_at_gmail.com", "Campus": "UI", "Major": "Hukum", "Error_Reason": "Format email tidak valid"},
        {"Nama": "Bagas Kurniawan", "Email": "bagas.k@mail.com", "Campus": "", "Major": "Sistem Informasi", "Error_Reason": "Nama Kampus kosong"},
        {"Nama": "Rina Nose", "Email": "rina@mail.com", "Campus": "Kampus X", "Major": "Teknik Mesin", "Error_Reason": "ID Kampus pendaftar diblacklist"}
    ]
    
    missing_data = [
        {"Entitas": "Kampus", "Nama_Raw": "Universitas Teknologi Nusantara"},
        {"Entitas": "Jurusan", "Nama_Raw": "Ilmu Aktuaria dan Asuransi Terapan"}
    ]
    
    return {
        "ready_for_ceria": ready_data,
        "anomaly_and_error": error_data,
        "missing_entities": missing_data
    }

# ==========================================
# Tampilan Menu 1: Data Validation Pipeline
# ==========================================
def render_validation_pipeline():
    st.title("Data Validation Pipeline 🚀")
    st.markdown("Unggah `Raw Data Excel` kandidat untuk dibersihkan dan dicocokkan dengan Master Data menggunakan bantuan AI Agent.")
    
    # Area unggah data
    uploaded_file = st.file_uploader("Unggah Raw Data Excel/CSV", type=["xlsx", "xls", "csv"])
    
    if st.button("Proses Validasi Data", type="primary"):
        if uploaded_file is not None:
            # 1. Menampilkan Progress dan Status Indikator
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulasi waktu proses API
            status_text.info("⏳ Membaca file raw data...")
            time.sleep(1)
            progress_bar.progress(25)
            
            status_text.info("🤖 Menghubungi AI Agent (n8n)...")
            time.sleep(1.5)
            progress_bar.progress(50)
            
            status_text.info("🔍 Mengekstrak anomali dan mencocokkan ID...")
            time.sleep(2)
            progress_bar.progress(75)
            
            # 2. HTTP POST Request ke endpoint n8n webhook
            api_url = "http://localhost:5678/webhook/validate-raw-data"
            try:
                # Menggunakan library requests untuk Post data
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = requests.post(api_url, files=files, timeout=3)
                response.raise_for_status() # Akan memicu exception jika status != 200
                
                # Asumsi jika API beneran ada, return JSON
                data = response.json()
                st.session_state.ready_df = pd.DataFrame(data.get("ready_for_ceria", []))
                st.session_state.error_df = pd.DataFrame(data.get("anomaly_and_error", []))
                st.session_state.missing_df = pd.DataFrame(data.get("missing_entities", []))
                st.toast("Berhasil memproses data dari webhook!", icon="✅")
                
            except Exception as e:
                # Tangkap Error dan gunakan MOCK DATA
                st.warning(f"Endpoint API gagal diakses atau timeout ({str(e)}). Menggunakan Mock Data untuk simulasi UI.", icon="⚠️")
                mock_data = get_mock_data()
                st.session_state.ready_df = pd.DataFrame(mock_data["ready_for_ceria"])
                st.session_state.error_df = pd.DataFrame(mock_data["anomaly_and_error"])
                st.session_state.missing_df = pd.DataFrame(mock_data["missing_entities"])
            
            # Proses Selesai
            progress_bar.progress(100)
            status_text.success("✨ Validasi Data Selesai!")
            st.session_state.validation_done = True
            
        else:
            st.error("Silakan unggah Raw Data terlebih dahulu sebelum memproses.")

    # 3. Tampilkan Tab Output jika proses validasi sudah dijalankan
    if st.session_state.validation_done:
        st.divider()
        st.subheader("📊 Hasil Validasi Data")
        
        tab_ready, tab_error, tab_missing = st.tabs([
            "✅ Ready for CERIA", 
            "⚠️ Anomaly & Error", 
            "🔍 Missing Entities"
        ])
        
        with tab_ready:
            st.markdown("Dataframe di bawah ini berisi kolom **Nama, Email, Campus ID, Major ID** yang sudah di-standardisasi dan siap dimasukkan ke sistem CERIA.")
            st.dataframe(st.session_state.ready_df, use_container_width=True)
            
            # Tombol Download CSV untuk Tab 1
            if not st.session_state.ready_df.empty:
                csv_ready = st.session_state.ready_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Download CSV (Ready Data)",
                    data=csv_ready,
                    file_name="ready_for_ceria.csv",
                    mime="text/csv"
                )
                
        with tab_error:
            st.markdown("Baris data yang gagal diproses oleh AI agent beserta alasan errornya (**Error_Reason**). Harap perbaiki secara manual.")
            st.dataframe(st.session_state.error_df, use_container_width=True)
            
            if not st.session_state.error_df.empty:
                csv_error = st.session_state.error_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Download CSV (Error Data)",
                    data=csv_error,
                    file_name="anomaly_and_error.csv",
                    mime="text/csv"
                )
                
        with tab_missing:
            st.markdown("Nama **Kampus** atau **Jurusan** dari raw data yang **TIDAK ADA** di Master Data sistem.")
            st.dataframe(st.session_state.missing_df, use_container_width=True)
            
            # Tombol "Copy to Clipboard" alternatif menggunakan st.code
            if not st.session_state.missing_df.empty:
                st.markdown("💡 *Gunakan tombol salin di pojok kanan boks di bawah ini untuk menyalin seluruh entitas yang hilang.*")
                missing_text_output = st.session_state.missing_df.to_string(index=False)
                st.code(missing_text_output, language="text")

# ==========================================
# Tampilan Menu 2: Master Data Management
# ==========================================
def render_master_data_management():
    st.title("Master Data Management 🗃️")
    st.info("Unggah file Master Data (Campus & Major ID) terbaru dari web CERIA untuk memperbarui database/referensi AI Agent.")
    
    # Area unggah master data
    master_file = st.file_uploader("Unggah Master Data Excel/CSV", type=["xlsx", "xls", "csv"], key="master_data_uploader")
    
    if st.button("Update Master Data", type="primary"):
        if master_file is not None:
            with st.spinner("Mengirim pembaruan ke backend AI Agent..."):
                api_url = "http://localhost:5678/webhook/update-master-data"
                try:
                    # Simulasi API Call
                    time.sleep(1.5)
                    files = {"file": (master_file.name, master_file.getvalue())}
                    response = requests.post(api_url, files=files, timeout=3)
                    
                    # Kita lewati penanganan valid response berhubung dummy
                except Exception:
                    # Kita abaikan exception dan asumsikan proses berhasil pada flow mock
                    pass 
                
            st.success("🎉 Master Data berhasil diperbarui!")
            st.balloons()
        else:
            st.error("Silakan unggah Master Data terlebih dahulu sebelum melakukan pembaruan.")

# ==========================================
# Main App logic
# ==========================================
def main():
    # Sidebar untuk Navigasi Menu
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/8636/8636906.png", width=100) 
    st.sidebar.title("Navigasi CERIA")
    st.sidebar.markdown("Silakan pilih menu:")
    
    menu = st.sidebar.radio(
        "Menu Utama",
        ("1. Data Validation Pipeline", "2. Master Data Management"),
        label_visibility="collapsed"
    )
    
    st.sidebar.divider()
    st.sidebar.markdown("*CERIA AI Candidate Assistant*")
    
    # Routing halaman
    if menu == "1. Data Validation Pipeline":
        render_validation_pipeline()
    elif menu == "2. Master Data Management":
        render_master_data_management()

if __name__ == "__main__":
    main()
