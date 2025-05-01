import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# 🎨 Estilo tipo TERMINATOR
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
        color: #FF0000;
        font-family: 'Courier New', monospace;
    }
    h1, h2, h3, .css-10trblm {
        color: #FF2222;
        text-shadow: 0 0 5px #FF0000;
    }
    .stButton>button {
        background-color: #111;
        color: #FF3333;
        border: 2px solid #FF0000;
        padding: 0.5em 1em;
        font-size: 16px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #330000;
        border-color: #FF4444;
    }
    .stSelectbox label, .stTextInput label, .stTextArea label {
        color: #FF4444;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 T-800 | MODULO DE TRADUCCIÓN VOCAL")
st.subheader("SISTEMA ACTIVADO - INICIANDO ESCUCHA...")

# Imagen tipo visión cyborg (puedes cambiar 'OIG7.jpg' por una más robótica o roja)
image = Image.open("dron.jpg")
st.image(image, width=300)

with st.sidebar:
    st.subheader("🔊 MÓDULO DE TRADUCCIÓN CYBORG")
    st.write("Presiona el botón. Cuando escuches la señal, transmite tu mensaje. Luego selecciona idioma objetivo.")

st.write("📡 Pulsa el botón para activar el micrófono.")

stt_button = Button(label=" 🎤 ACTIVAR ESCUCHA", width=300, height=50)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result and "GET_TEXT" in result:
    st.markdown("### 🔍 TRADUCCIÓN ADQUIRIDA:")
    st.write(result.get("GET_TEXT"))

    try:
        os.mkdir("temp")
    except:
        pass

    translator = Translator()
    text = str(result.get("GET_TEXT"))

    in_lang = st.selectbox("📥 LENGUAJE DE ENTRADA", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))
    input_language = {
        "Inglés": "en", "Español": "es", "Bengali": "bn",
        "Coreano": "ko", "Mandarín": "zh-cn", "Japonés": "ja"
    }[in_lang]

    out_lang = st.selectbox("📤 LENGUAJE DE SALIDA", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))
    output_language = {
        "Inglés": "en", "Español": "es", "Bengali": "bn",
        "Coreano": "ko", "Mandarín": "zh-cn", "Japonés": "ja"
    }[out_lang]

    tld = st.selectbox("🌐 ACCENTO", {
        "Defecto": "com", "Español": "com.mx", "Reino Unido": "co.uk",
        "Estados Unidos": "com", "Canada": "ca", "Australia": "com.au",
        "Irlanda": "ie", "Sudáfrica": "co.za"
    }.keys())

    tld_value = {
        "Defecto": "com", "Español": "com.mx", "Reino Unido": "co.uk",
        "Estados Unidos": "com", "Canada": "ca", "Australia": "com.au",
        "Irlanda": "ie", "Sudáfrica": "co.za"
    }[tld]

    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        file_name = text[0:20].replace(" ", "_") or "audio"
        path = f"temp/{file_name}.mp3"
        tts.save(path)
        return path, trans_text

    if st.button("🎧 EJECUTAR CONVERSIÓN"):
        audio_path, translated_text = text_to_speech(input_language, output_language, text, tld_value)
        st.markdown("## 📡 AUDIO LISTO:")
        st.audio(audio_path, format="audio/mp3", start_time=0)

        if st.checkbox("📝 Mostrar texto traducido"):
            st.markdown(f"### 📃 RESULTADO:")
            st.write(translated_text)

    def remove_files(n):
        now = time.time()
        for f in glob.glob("temp/*.mp3"):
            if os.stat(f).st_mtime < now - n * 86400:
                os.remove(f)

    remove_files(7)
