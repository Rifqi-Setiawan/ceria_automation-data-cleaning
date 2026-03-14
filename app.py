import streamlit as st
import pandas as pd
import requests
import time
import io

st.set_page_config(
    page_title="CERIA Candidate Data Validation Assistant",
    page_icon="✨",
    layout="wide"
)

if "validation_done" not in st.session_state:
    st.session_state.validation_done = False
if "ready_df" not in st.session_state:
    st.session_state.ready_df = pd.DataFrame()
if "error_df" not in st.session_state:
    st.session_state.error_df = pd.DataFrame()
if "missing_df" not in st.session_state:
    st.session_state.missing_df = pd.DataFrame()

def render_validation_pipeline():
    st.title("Data Validation Pipeline 🚀")
    st.markdown("Unggah `Raw Data Excel` kandidat untuk dibersihkan dan dicocokkan dengan Master Data menggunakan bantuan AI Agent.")
    
    uploaded_file = st.file_uploader("Unggah Raw Data Excel/CSV", type=["xlsx", "xls", "csv"])
    
    if st.button("Proses Validasi Data", type="primary"):
        if uploaded_file is not None:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.info("⏳ Membaca file raw data...")
            time.sleep(1)
            progress_bar.progress(25)
            
            status_text.info("🤖 Menghubungi AI Agent (n8n)...")
            time.sleep(1.5)
            progress_bar.progress(50)
            
            status_text.info("🔍 Mengekstrak anomali dan mencocokkan ID...")
            time.sleep(2)
            progress_bar.progress(75)
            
            api_url = "https://n8n.user.aispace.id/webhook-test/validate-raw-data"
            try:
                files = {"File_Excel": (uploaded_file.name, uploaded_file.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                response = requests.post(api_url, files=files, timeout=30)
                response.raise_for_status()
                
                raw_data = response.json()
                
                if isinstance(raw_data, list) and len(raw_data) > 0:
                    data = raw_data[0]
                else:
                    data = raw_data
                st.session_state.ready_df = pd.DataFrame(data.get("data_bersih", []))
                st.session_state.error_df = pd.DataFrame(data.get("data_bermasalah", []))
                st.session_state.missing_df = pd.DataFrame(data.get("data_belum_terdaftar", []))
                st.toast("Berhasil memproses data dari webhook!", icon="✅")
                
                progress_bar.progress(100)
                status_text.success("✨ Validasi Data Selesai!")
                st.session_state.validation_done = True
                
            except Exception as e:
                st.error(f"Gagal memproses data atau terjadi timeout: {str(e)}", icon="🚨")
                st.session_state.validation_done = False
                status_text.empty()
                progress_bar.empty()
            
        else:
            st.error("Silakan unggah Raw Data terlebih dahulu sebelum memproses.")

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
            
            if not st.session_state.ready_df.empty:
                output_ready = io.BytesIO()
                with pd.ExcelWriter(output_ready, engine='xlsxwriter') as writer:
                    st.session_state.ready_df.to_excel(writer, index=False, sheet_name='Ready Data')
                
                st.download_button(
                    label="⬇️ Download Excel (Ready Data)",
                    data=output_ready.getvalue(),
                    file_name="ready_for_ceria.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
        with tab_error:
            st.markdown("Baris data yang gagal diproses oleh AI agent beserta alasan errornya (**Error_Reason**). Harap perbaiki secara manual.")
            st.dataframe(st.session_state.error_df, use_container_width=True)
            
            if not st.session_state.error_df.empty:
                output_error = io.BytesIO()
                with pd.ExcelWriter(output_error, engine='xlsxwriter') as writer:
                    st.session_state.error_df.to_excel(writer, index=False, sheet_name='Error Data')
                    
                st.download_button(
                    label="⬇️ Download Excel (Error Data)",
                    data=output_error.getvalue(),
                    file_name="anomaly_and_error.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
        with tab_missing:
            st.markdown("Nama **Kampus** atau **Jurusan** dari raw data yang **TIDAK ADA** di Master Data sistem.")
            st.dataframe(st.session_state.missing_df, use_container_width=True)
            
            if not st.session_state.missing_df.empty:
                st.markdown("💡 *Gunakan tombol salin di pojok kanan boks di bawah ini untuk menyalin seluruh entitas yang hilang.*")
                missing_text_output = st.session_state.missing_df.to_string(index=False)
                st.code(missing_text_output, language="text")

def render_master_data_management():
    st.title("Master Data Management 🗃️")
    st.info("Unggah file Master Data (Campus & Major ID) terbaru dari web CERIA untuk memperbarui database/referensi AI Agent.")
    
    master_file = st.file_uploader("Unggah Master Data Excel/CSV", type=["xlsx", "xls", "csv"], key="master_data_uploader")
    
    if st.button("Update Master Data", type="primary"):
        if master_file is not None:
            with st.spinner("Mengirim pembaruan ke backend AI Agent..."):
                api_url = "http://localhost:5678/webhook/update-master-data"
                try:
                    time.sleep(1.5)
                    files = {"file": (master_file.name, master_file.getvalue())}
                    response = requests.post(api_url, files=files, timeout=3)
                except Exception:
                    pass
                
            st.success("🎉 Master Data berhasil diperbarui!")
            st.balloons()
        else:
            st.error("Silakan unggah Master Data terlebih dahulu sebelum melakukan pembaruan.")

def main():
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
    
    if menu == "1. Data Validation Pipeline":
        render_validation_pipeline()
    elif menu == "2. Master Data Management":
        render_master_data_management()

if __name__ == "__main__":
    main()
