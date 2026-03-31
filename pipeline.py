import streamlit as st
import pandas as pd
import requests
import time
import io
from datetime import datetime

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
            
            api_url = "https://n8n.user.aispace.id/webhook/validate-raw-data"
            try:
                files = {"File_Excel": (uploaded_file.name, uploaded_file.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                response = requests.post(api_url, files=files, timeout=3000)
                response.raise_for_status()
                
                raw_data = response.json()
                
                data_bersih = []
                data_bermasalah = []
                data_belum_terdaftar = []

                if isinstance(raw_data, list):
                    for item in raw_data:
                        if isinstance(item, dict):
                            db = item.get("data_bersih")
                            dbm = item.get("data_bermasalah")
                            dbt = item.get("data_belum_terdaftar")
                            if db: data_bersih.extend(db if isinstance(db, list) else [db])
                            if dbm: data_bermasalah.extend(dbm if isinstance(dbm, list) else [dbm])
                            if dbt: data_belum_terdaftar.extend(dbt if isinstance(dbt, list) else [dbt])
                elif isinstance(raw_data, dict):
                    db = raw_data.get("data_bersih")
                    dbm = raw_data.get("data_bermasalah")
                    dbt = raw_data.get("data_belum_terdaftar")
                    if db: data_bersih.extend(db if isinstance(db, list) else [db])
                    if dbm: data_bermasalah.extend(dbm if isinstance(dbm, list) else [dbm])
                    if dbt: data_belum_terdaftar.extend(dbt if isinstance(dbt, list) else [dbt])

                st.session_state.ready_df = pd.DataFrame(data_bersih)
                st.session_state.ready_df.index += 1
                st.session_state.error_df = pd.DataFrame(data_bermasalah)
                st.session_state.error_df.index += 1
                st.session_state.missing_df = pd.DataFrame(data_belum_terdaftar)
                st.session_state.missing_df.index += 1
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
            "✅ Data Bersih", 
            "⚠️ Data Bermasalah", 
            "🔍 Data Belum Terdaftar"
        ])
        
        with tab_ready:
            st.markdown("Dataframe di bawah ini berisi kolom **Nama, Email, Campus ID, Major ID** yang sudah di-standardisasi dan siap dimasukkan ke sistem CERIA.")
            st.dataframe(st.session_state.ready_df, width='stretch')
            
            if not st.session_state.ready_df.empty:
                output_ready = io.BytesIO()
                with pd.ExcelWriter(output_ready, engine='xlsxwriter') as writer:
                    st.session_state.ready_df.to_excel(writer, index=False, sheet_name='Ready Data')
                
                st.download_button(
                    label="⬇️ Download Excel (Ready Data)",
                    data=output_ready.getvalue(),
                    file_name=f"data_bersih_{datetime.now().strftime('%Y-%m-%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
        with tab_error:
            st.markdown("Baris data yang gagal diproses oleh AI agent beserta alasan errornya (**Error_Reason**). Harap perbaiki secara manual.")
            st.dataframe(st.session_state.error_df, width='stretch')
            
            if not st.session_state.error_df.empty:
                output_error = io.BytesIO()
                with pd.ExcelWriter(output_error, engine='xlsxwriter') as writer:
                    st.session_state.error_df.to_excel(writer, index=False, sheet_name='Error Data')
                    
                st.download_button(
                    label="⬇️ Download Excel (Error Data)",
                    data=output_error.getvalue(),
                    file_name=f"data_bermasalah_{datetime.now().strftime('%Y-%m-%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
        with tab_missing:
            st.markdown("Nama **Kampus** atau **Jurusan** dari raw data yang **TIDAK ADA** di Master Data sistem.")
            st.dataframe(st.session_state.missing_df, width='stretch')
            
            if not st.session_state.missing_df.empty:
                output_missing = io.BytesIO()
                with pd.ExcelWriter(output_missing, engine='xlsxwriter') as writer:
                    st.session_state.missing_df.to_excel(writer, index=False, sheet_name='Missing Data')
                
                st.download_button(
                    label="⬇️ Download Excel (Missing Entities)",
                    data=output_missing.getvalue(),
                    file_name=f"data_belum_terdaftar_{datetime.now().strftime('%Y-%m-%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                st.markdown("💡 *Gunakan tombol salin di pojok kanan boks di bawah ini untuk menyalin seluruh entitas yang hilang.*")
                missing_text_output = st.session_state.missing_df.to_string(index=False)
                st.code(missing_text_output, language="text")
