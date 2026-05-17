import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

st.set_page_config(page_title="Tanya-Pajak: Asisten AI Perpajakan", page_icon="💬", layout="centered")

@st.cache_resource
def get_genai_client():
    return genai.Client()

client = get_genai_client()

system_instruction = """
Anda adalah "Tanya-Pajak", sebuah chatbot berbasis AI (Large Language Model) yang bertindak sebagai asisten virtual ahli perpajakan Indonesia.
Tugas utama Anda adalah memberikan jawaban yang solutif, valid, dan mudah dipahami oleh wajib pajak.

Aturan Komunikasi:
1. Identifikasi diri Anda sebagai "Tanya-Pajak" jika pengguna menanyakan nama Anda.
2. Gunakan bahasa Indonesia yang formal, santun, terstruktur, dan mematuhi standar PUEBI/KBBI.
3. Fokus pada domain perpajakan (regulasi, tata cara, integrasi sistem seperti Coretaxpedia/pajak.go.id).
4. Jika ada pertanyaan di luar domain perpajakan atau keuangan negara, tolak secara halus dan arahkan kembali ke topik pajak.
5. Setel respon agar informatif namun tetap menyertakan saran untuk validasi ke Kring Pajak 1500200 untuk urusan hukum yang mengikat.
"""

config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    temperature=0.2,  
    max_output_tokens=1024,
    safety_settings=[
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
    ]
)

if "chat_session" not in st.session_state:
    st.session_state.chat_session = client.chats.create(
   "models/gemini-2.5-flash-lite",
    generation_config={
        "max_output_tokens": 100,
        "temperature": 0.2
    }
)


st.title("💬 Tanya-Pajak")
st.markdown("Selamat datang di **Tanya-Pajak**! Layanan chatbot bertenaga AI untuk menjawab segala pertanyaan seputar regulasi dan administrasi perpajakan Indonesia secara instan.")
st.divider()

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
