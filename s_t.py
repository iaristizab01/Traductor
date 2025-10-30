import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from deep_translator import GoogleTranslator  # ✅ reemplazo estable


# 🌹 Interfaz
st.title("💌 El Traductor del Corazón")
st.subheader("Donde las palabras cruzan fronteras... y corazones.")

image = Image.open("OIG7.jpg")
st.image(image, width=300)

with st.sidebar:
    st.markdown("### 💞 Modo romántico activado")
    st.write("Habla desde el corazón. Este traductor convierte tus emociones "
             "en mensajes que puedan entenderse en cualquier idioma.")
    st.caption("✨ Consejo: mientras más sincero seas, más hermoso será el resultado.")

st.write("Presiona el botón y confiesa tu mensaje de amor 💬")

# 🎙️ Botón de voz
stt_button = Button(label="💖 Susurrar al micrófono", width=300, height=50)

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

# 🪶 Traducción romántica
if result and "GET_TEXT" in result:
    original_text = result.get("GET_TEXT")
    st.success(f"💬 Tu mensaje: *{original_text}*")

    try:
        os.mkdir("temp")
    except:
        pass

    in_lang = st.selectbox("🌍 Lenguaje de entrada", ("Español", "Inglés", "Francés", "Italiano"))
    out_lang = st.selectbox("💘 Lenguaje del corazón (salida)", ("Inglés", "Francés", "Italiano", "Japonés"))

    # Diccionarios de códigos
    lang_codes = {
        "Español": "es", "Inglés": "en", "Francés": "fr", "Italiano": "it", "Japonés": "ja"
    }

    input_language = lang_codes[in_lang]
    output_language = lang_codes[out_lang]

    def text_to_love(input_language, output_language, text):
        # ✅ deep-translator reemplaza a googletrans
        translated_text = GoogleTranslator(source=input_language, target=output_language).translate(text)

        # Pequeño toque poético 💫
        love_quotes = [
            "El amor no necesita traducción, solo intención.",
            "Cada palabra que cruzó el idioma fue un suspiro del alma.",
            "Tu voz viajó más lejos que cualquier carta de amor.",
            "A veces traducir es otra forma de decir 'te pienso'."
        ]
        import random
        poetic_line = random.choice(love_quotes)

        tts = gTTS(translated_text, lang=output_language)
        filename = f"temp/{text[:15]}.mp3"
        tts.save(filename)

        return filename, translated_text, poetic_line

    if st.button("✨ Traducir mi sentimiento"):
        filename, translated, poetic = text_to_love(input_language, output_language, original_text)
        st.audio(filename)
        st.markdown(f"### 💞 Traducción:")
        st.markdown(f"**{translated}**")
        st.caption(f"💬 {poetic}")

    # Limpieza de archivos antiguos
    def remove_files(n):
        mp3_files = glob.glob("temp/*.mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)

    remove_files(3)
