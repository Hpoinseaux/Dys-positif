import streamlit as st
import fitz  # PyMuPDF pour l'extraction de texte PDF
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr
from deep_translator import GoogleTranslator
from fpdf import FPDF  # Pour générer un nouveau PDF





# Fonction pour extraire du texte depuis un PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Fonction pour traduire du texte dans une autre langue
def translate_text(text, target_language):
    translator = GoogleTranslator(source='auto', target=target_language)
    translation = translator.translate(text)
    return translation

# Fonction pour générer un PDF avec du texte
def generate_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    
    # Ajouter le texte traduit au PDF
    pdf.multi_cell(0, 10, text)
    
    # Sauvegarder le fichier PDF dans un buffer en mémoire
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)  # Remettre le pointeur au début pour la lecture
    return pdf_output

# Fonction pour convertir du texte en audio avec gTTS
def text_to_audio(text, lang='fr'):
    tts = gTTS(text=text, lang=lang)
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)  # Remettre le pointeur au début du fichier pour la lecture
    return audio_file



# Fonction pour convertir un fichier audio téléchargé (WAV) en texte
def audio_to_text(audio_file):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
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
    ("Accueil", "Lecture (PDF vers Audio)", "Traduction PDF", "Écriture (Audio vers Texte)")
)

# Contenu de la page principale
if option == "Accueil":
    st.title("Application pour les élèves ayant des difficultés de lecture et d'écriture")
    st.write("""
    Cette application est conçue pour aider les élèves qui ont des difficultés en lecture et en écriture.
    Elle propose trois fonctionnalités principales :
    
    1. **Lecture** : Convertir un fichier PDF en audio afin que l'élève puisse écouter le contenu.
    2. **Traduction** : Traduire le contenu d'un PDF dans une autre langue et générer un nouveau PDF traduit.
    3. **Écriture** : Enregistrer la voix de l'élève et transformer ses paroles en texte.
    
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

elif option == "Traduction PDF":
    st.header("Traduire un PDF et générer un nouveau PDF")

    # Téléchargement du fichier PDF
    uploaded_pdf = st.file_uploader("Télécharger un fichier PDF", type="pdf")

    if uploaded_pdf is not None:
        # Extraction du texte du PDF
        text = extract_text_from_pdf(uploaded_pdf)

        if text:
            # Afficher le texte extrait
            st.text_area("Contenu extrait du PDF :", value=text, height=200, disabled=True)

            # Choix de la langue de traduction
            target_language = st.selectbox("Choisissez la langue de traduction", ['en', 'es', 'de'])

            # Bouton pour traduire et générer un nouveau PDF
            if st.button("Traduire et générer PDF"):
                with st.spinner("Traduction en cours..."):
                    translated_text = translate_text(text, target_language)

                # Générer le PDF avec le texte traduit
                pdf_output = generate_pdf(translated_text)

                # Télécharger le PDF traduit
                st.download_button("Télécharger le PDF traduit", data=pdf_output, file_name="translated_output.pdf", mime="application/pdf")
        else:
            st.error("Aucun texte n'a pu être extrait de ce fichier PDF.")
    else:
        st.info("Veuillez télécharger un fichier PDF pour commencer.")

elif option == "Écriture (Audio vers Texte)":
    st.header("Convertir un Enregistrement Audio en Texte")

    # Téléchargement du fichier audio (format WAV )
    uploaded_audio = st.file_uploader("Télécharger un fichier audio (WAV )", type=["wav"])

    if uploaded_audio is not None:
        # Lecture de l'audio
        st.audio(uploaded_audio)
        if st.button("Convertir en texte"):
            wav_audio = uploaded_audio
            with st.spinner("Transcription en cours..."):
                result_text = audio_to_text(wav_audio)

            if result_text:
                st.write("Texte extrait de l'audio :")
                st.text_area("Résultat", value=result_text, height=200)
    else:
        st.info("Veuillez télécharger un fichier audio pour commencer.")