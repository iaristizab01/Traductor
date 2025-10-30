import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from deep_translator import GoogleTranslator


# 🌍 Interfaz principal
st.title("🌎 Traductor de Destinos")
st.subheader("Habla, y te traducirá al idioma del lugar al que estás destinado a ir.")

# Imagen principal
image = Image.open("OIG7.jpg")
st.image(image, width=300)

with st.sidebar:
    st.subheader("🧭 Modo viajero")
    st.write(
        "Presiona el botón y di algo. "
        "El traductor convertirá tus palabras al idioma del país que elijas, "
        "para que llegues preparado donde sea que te lleve el destino."
    )
    st.caption("✨ Consejo: imagina que estás a punto de aterrizar en tu próxima aventura.")

st.write("Presiona el botón y di algo para traducirlo al idioma de tu próximo destino 🌐")

# 🎙️ Botón de reconocimiento de voz
stt_button = Button(label="🎤 Hablar", width=300, height=50)

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

# ✈️ Traducción de voz
if result and "GET_TEXT" in result:
    original_text = result.get("GET_TEXT")
    st.success(f"🗣️ Tu frase: *{original_text}*")

    try:
        os.mkdir("temp")
    except:
        pass

    # Selección de idioma de entrada
    in_lang = st.selectbox(
        "🌍 Idioma actual (lo que estás hablando)",
        ("Español", "Inglés", "Francés", "Italiano")
    )

    # Idioma de destino (donde el usuario “viaja”)
    out_lang = st.selectbox(
        "🧳 Idioma del destino (donde estás por ir)",
        ("Inglés", "Francés", "Italiano", "Japonés", "Alemán", "Portugués")
    )

    # Diccionario de códigos ISO
    lang_codes = {
        "Español": "es",
        "Inglés": "en",
        "Francés": "fr",
        "Italiano": "it",
        "Japonés": "ja",
        "Alemán": "de",
        "Portugués": "pt"
    }

    input_language = lang_codes[in_lang]
    output_language = lang_codes[out_lang]

    def translate_and_speak(src_lang, dest_lang, text):
        translated = GoogleTranslator(source=src_lang, target=dest_lang).translate(text)
        tts = gTTS(translated, lang=dest_lang)
        filename = f"temp/{text[:15]}.mp3"
        tts.save(filename)
        return translated, filename

    if st.button("🌐 Traducir mi mensaje"):
        translated, filename = translate_and_speak(input_language, output_language, original_text)
        st.markdown(f"### ✈️ Traducción en {out_lang}:")
        st.markdown(f"**{translated}**")
        st.audio(filename)

    # Limpieza automática
    def remove_old_audio(days):
        mp3_files = glob.glob("temp/*.mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = days * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)

    remove_old_audio(3)
