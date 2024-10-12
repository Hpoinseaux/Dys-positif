import streamlit as st
import fitz  # PyMuPDF pour l'extraction de texte PDF
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr

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

# Fonction pour convertir l'audio en texte (utilise microphone par défaut)
def audio_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Enregistrement... Parlez maintenant")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio, language="fr-FR")
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

    # Bouton pour lancer l'enregistrement
    if st.button("Commencer l'enregistrement"):
        with st.spinner("Écoute..."):
            result_text = audio_to_text()

        if result_text:
            st.write("Texte extrait de l'audio :")
            st.text_area("Résultat", value=result_text, height=200)

            # Bouton pour copier le texte
            st.write("Vous pouvez copier ce texte pour l'utiliser ailleurs.")