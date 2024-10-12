import streamlit as st
import fitz  # PyMuPDF pour l'extraction de texte PDF
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr
from pydub import AudioSegment
import imageio_ffmpeg as ffmpeg

# Configuration pour FFmpeg avec pydub
AudioSegment.converter = ffmpeg.get_ffmpeg_exe()

# Fonction pour extraire du texte depuis un PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Fonction pour convertir du texte en audio avec gTTS
def text_to_audio(text, lang='fr'):
    tts = gTTS(text=text, lang=lang)
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)  # Remettre le pointeur au début du fichier pour la lecture
    return audio_file

# Fonction pour convertir un fichier audio téléchargé (MP3) en format WAV
def convert_audio_to_wav(mp3_file):
    audio = AudioSegment.from_file(mp3_file, format="mp3")
    wav_io = BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)  # Remettre le pointeur au début du fichier pour la lecture
    return wav_io

# Fonction pour convertir un fichier audio téléchargé en texte
def audio_to_text(wav_audio):
    r = sr.Recognizer()
    with sr.AudioFile(wav_audio) as source:
        audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data, language="fr-FR")
            return text
        except sr.UnknownValueError:
            return "Je n'ai pas compris l'audio."
        except sr.RequestError:
            return "Erreur de service avec la reconnaissance vocale."

# Ajout d'un panneau latéral pour la navigation
st.sidebar.title("Navigation")
option = st.sidebar.selectbox(
    "Choisissez une fonctionnalité",
    ("Accueil", "Lecture (PDF vers Audio)", "Écriture (Audio vers Texte)")
)

# Contenu de la page principale
if option == "Accueil":
    st.title("Application pour les élèves ayant des difficultés de lecture et d'écriture")
    st.write("""
    Cette application est conçue pour aider les élèves qui ont des difficultés en lecture et en écriture.
    Elle propose deux fonctionnalités principales :
    
    1. **Lecture** : Convertir un fichier PDF en audio afin que l'élève puisse écouter le contenu.
    2. **Écriture** : Enregistrer la voix de l'élève et transformer ses paroles en texte.
    
    Utilisez le panneau latéral pour naviguer entre les différentes fonctionnalités.
    """)

elif option == "Lecture (PDF vers Audio)":
    st.header("Convertir un PDF en Audio")

    # Téléchargement du fichier PDF
    uploaded_pdf = st.file_uploader("Télécharger un fichier PDF", type="pdf")

    if uploaded_pdf is not None:
        # Extraction du texte du PDF
        text = extract_text_from_pdf(uploaded_pdf)

        if text:
            st.text_area("Contenu extrait du PDF :", value=text, height=200)

            # Choix de la langue
            language = st.selectbox("Choisissez la langue de l'audio", ['fr', 'en', 'es', 'de'])

            # Bouton pour générer l'audio
            if st.button("Convertir en audio"):
                audio_file = text_to_audio(text, lang=language)

                # Lecture de l'audio et téléchargement
                st.audio(audio_file, format='audio/mp3')
                st.download_button("Télécharger l'audio", data=audio_file, file_name="output.mp3", mime="audio/mp3")
        else:
            st.error("Aucun texte n'a pu être extrait de ce fichier PDF.")
    else:
        st.info("Veuillez télécharger un fichier PDF pour commencer.")


elif option == "Écriture (Audio vers Texte)":
    st.header("Convertir un Enregistrement Audio en Texte")
    # Téléchargement du fichier audio (format MP3)
    uploaded_audio = st.file_uploader("Télécharger un fichier audio", type=["mp3"])

    if uploaded_audio is not None:
        st.audio(uploaded_audio, format="audio/mp3")

        if st.button("Convertir en texte"):
            with st.spinner("Conversion de l'audio en WAV..."):
                wav_audio = convert_audio_to_wav(uploaded_audio)

            with st.spinner("Transcription en cours..."):
                result_text = audio_to_text(wav_audio)

            if result_text:
                st.write("Texte extrait de l'audio :")
                st.text_area("Résultat", value=result_text, height=200)
    else:
        st.info("Veuillez télécharger un fichier audio pour commencer.")