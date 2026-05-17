import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

load_dotenv()

st.set_page_config(page_title="Tanya-Pajak: Asisten AI Perpajakan", page_icon="💬", layout="centered")

default_key = os.environ.get("GEMINI_API_KEY", "")

@st.cache_resource(show_spinner=False)
def validate_and_get_client(api_key):
    if not api_key:
        return None, "empty"
    try:
        test_client = genai.Client(api_key=api_key)
        test_client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents='ping',
            config=types.GenerateContentConfig(max_output_tokens=1)
        )
        return test_client, "success"
    except APIError as e:
        return None, f"error: {e.message}"
    except Exception as e:
        return None, f"error: {str(e)}"

with st.sidebar:
    st.header("⚙️ Konfigurasi Sistem")
    st.markdown("Pengaturan parameter kreatif dan kredensial model AI.")
    st.divider()
    
    api_key_input = st.text_input(
        "Google Gemini API Key:",
        value=default_key,
        type="password",
        placeholder="AIzaSy...",
        help="Dapatkan API Key Anda melalui platform Google AI Studio (aistudio.google.com)"
    )
    
    client, status = validate_and_get_client(api_key_input)
    
    if status == "success":
        st.success("✅ **API Key Valid!** Koneksi ke Google AI berhasil.")
    elif status != "empty" and status.startswith("error"):
        st.error(f"❌ **API Key Gagal:** {status.replace('error: ', '')}")
    elif status == "empty":
        st.info("🔑 Silakan masukkan API Key untuk memulai.")
        
    st.divider()
    st.caption("ℹ️ **Tanya-Pajak v1.1**")
    st.caption("Ditenagai oleh **Gemini 2.5 Flash Lite** (Model Efisiensi Tinggi).")

st.title("💬 Tanya-Pajak")
st.markdown("Halo, Selamat datang di **Tanya-Pajak**! Layanan chatbot untuk menjawab segala pertanyaan seputar regulasi dan administrasi perpajakan di Indonesia.")
st.divider()

if client is None:
    st.warning("🔒 **Akses Terkunci:** Pastikan untuk input Google Gemini API Key yang **Valid** untuk mengaktifkan chatbot Tanya-Pajak.")
    st.stop()

system_instruction = """
Anda adalah "Tanya-Pajak", sebuah chatbot berbasis AI (Large Language Model) yang bertindak sebagai asisten virtual ahli perpajakan Indonesia.
Tugas utama Anda adalah memberikan jawaban yang solutif, valid, dan mudah dipahami oleh wajib pajak.

Aturan Komunikasi:
1. Gunakan bahasa Indonesia yang formal, santun, terstruktur, dan mematuhi standar PUEBI/KBBI.
2. Fokus pada domain perpajakan (regulasi, tata cara, integrasi sistem seperti Coretaxpedia/pajak.go.id).
3. Jika ada pertanyaan di luar domain perpajakan atau keuangan negara, tolak secara halus dan arahkan kembali ke topik pajak.
4. Setel respon agar informatif namun tetap menyertakan saran untuk validasi ke Kring Pajak 1500200 untuk urusan hukum yang mengikat.
"""

config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    temperature=0.2, 
    max_output_tokens=150,
)

if "chat_session" not in st.session_state:
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash-lite",
        config=config
    )

for message in st.session_state.chat_session.get_history():
    role = "human" if message.role == "user" else "ai"
    with st.chat_message(role):
        st.write(message.parts[0].text)

if user_input := st.chat_input("Tanyakan apa saja seputar pajak di sini..."):
    with st.chat_message("human"):
        st.write(user_input)
    
    with st.chat_message("ai"):
        with st.spinner("Tanya-Pajak sedang menyusun jawaban..."):
            response = st.session_state.chat_session.send_message(user_input)
            st.write(response.text)
