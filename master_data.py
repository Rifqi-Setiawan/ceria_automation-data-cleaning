import streamlit as st
import requests
import time
from db import fetch_master_data

def render_master_data_view():
    st.subheader("Master Data Kampus & Jurusan 🏛️")
    df_master = fetch_master_data()
    
    if not df_master.empty:
        search_query = st.text_input("🔍 Cari berdasarkan nama kampus atau jurusan...", "")
        
        if search_query:
            mask = (
                df_master['campus_name'].astype(str).str.contains(search_query, case=False, na=False) |
                df_master['major_name'].astype(str).str.contains(search_query, case=False, na=False)
            )
            df_display = df_master[mask]
        else:
            df_display = df_master
            
        if 'supabase_major_id' in df_display.columns:
            df_display = df_display.drop(columns=['supabase_major_id'])
            
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("Tidak ada data master yang ditemukan.")

def render_master_data_management():
    st.title("Master Data Management 🗃️")
    
    render_master_data_view()

    st.divider()
    st.info("Unggah file Master Data (Campus & Major ID) terbaru dari web CERIA untuk memperbarui database/referensi AI Agent.")
    
    master_file = st.file_uploader("Unggah Master Data Excel", type=["xlsx"], key="master_data_uploader")
    
    if st.button("Update Master Data", type="primary"):
        if master_file is not None:
            with st.spinner("Sedang memproses dan mengirim data ke AI Agent..."):
                WEBHOOK_MASTER_URL = "https://n8n.user.aispace.id/webhook/upload-master-data"
                files = {'data_referensi': (master_file.name, master_file.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                
                try:
                    response = requests.post(WEBHOOK_MASTER_URL, files=files, timeout=300)
                    
                    if response.status_code == 200:
                        try:
                            resp_data = response.json()
                            status = resp_data.get("status", "")
                            message = resp_data.get("message", "Master data berhasil diproses oleh sistem.")
                            
                            if status == "success":
                                st.toast("Data master berhasil disinkronisasi!", icon="✅")
                                st.success(f"✨ **Pembaruan Berhasil:** {message}")
                                
                                st.cache_data.clear()
                                if st.button("🔄 Refresh Halaman", key="btn_refresh_success"):
                                    st.rerun()
                            else:
                                st.warning(f"⚠️ **Perhatian:** {message}")
                        except ValueError:
                            st.toast("Data master berhasil disinkronisasi!", icon="✅")
                            st.success("✨ **Pembaruan Berhasil!** Master Data telah dikirim ke backend.")
                            
                            # CLEAR CACHE: Membuang memori data lama
                            st.cache_data.clear()
                            
                            # REFRESH UI: Tombol untuk force rerun
                            if st.button("🔄 Refresh Halaman"):
                                st.rerun()
                    else:
                        st.error(f"🚨 **Gagal Memproses Data:** Terjadi kesalahan pada server (HTTP Status: {response.status_code})")
                        st.info("💡 Pastikan webhook n8n di backend sedang aktif dan berjalan dengan baik.")
                        
                except requests.exceptions.Timeout:
                    st.error("Proses timeout, AI masih bekerja di latar belakang.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat menghubungi backend: {str(e)}")
        else:
            st.error("Silakan unggah Master Data terlebih dahulu sebelum melakukan pembaruan.")
