import streamlit as st
import fitz  # PyMuPDF pour l'extraction de texte PDF
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr
from deep_translator import GoogleTranslator
from fpdf import FPDF  # Pour générer un nouveau PDF




# Fonction pour extraire le texte d'un PDF
def extract_text_from_pdf(pdf_file):
    document = fitz.open(pdf_file)
    text = ""
    for page in document:
        text += page.get_text() + "\n"
    document.close()
    return text

# Fonction pour traduire le texte
def translate_text(text, target_language):
    try:
        translator = GoogleTranslator(source='auto', target=target_language)
        translation = translator.translate(text)
        return translation
    except Exception as e:
        st.error(f"Erreur de traduction: {e}")
        return None

# Fonction pour diviser le texte en morceaux de taille maximale
def split_text(text, max_length=4500):
    # Diviser le texte en morceaux ne dépassant pas max_length caractères
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

# Fonction pour créer un PDF avec le texte traduit
def create_pdf(text_list, output_file):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for text in text_list:
        pdf.add_page()
        # Ajout du texte au PDF
        for line in text.split('\n'):
            pdf.multi_cell(0, 10, line)

    pdf.output(output_file)

# Fonction pour convertir du texte en audio avec gTTS
def text_to_audio(text, lang='fr'):
    tts = gTTS(text=text, lang=lang)
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)  # Remettre le pointeur au début du fichier pour la lecture
    return audio_file



# Fonction pour convertir l'audio en texte
def audio_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        try:
            # Transcription de l'audio avec Google
            result = recognizer.recognize_google(audio, language="fr-FR")
            return result
        except sr.UnknownValueError:
            st.error("L'audio n'a pas pu être compris.")
            return None
        except sr.RequestError:
            st.error("Erreur de demande à l'API de reconnaissance vocale.")
            return None

# Fonction pour améliorer le texte (par exemple, en remplaçant les mots répétitifs)
def improve_text(text):
    # Dictionnaire de mots ou phrases à remplacer
    replacements = {
        "point": ".",
        "à la ligne":"\n"

    }

    # Remplacer chaque mot ou phrase selon le dictionnaire
    for old, new in replacements.items():
        text = text.replace(old, new)

    return text
# Ajout d'un panneau latéral pour la navigation
st.sidebar.title("Navigation")
option = st.sidebar.selectbox(
    "Choisissez une fonctionnalité",
    ("Accueil", "Lecture (PDF vers Audio)", "Traduction PDF", "Écriture (Audio vers Texte)")
)

# Couleur de fond en utilisant st.markdown pour une section
page_bg_img = '''
<style>
[data-testid="stMain"] {
background-color: #71b3f5; /* Couleur de fond */
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

st.image("https://images.pexels.com/photos/4181861/pexels-photo-4181861.jpeg", 
         use_column_width=True)

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

 # Choix entre télécharger un PDF ou saisir du texte
    input_method = st.radio("Choisissez la méthode d'entrée", ("Télécharger un PDF", "Saisir du texte"))

    if input_method == "Télécharger un PDF":
        # Téléchargement du fichier PDF
        uploaded_pdf = st.file_uploader("Télécharger un fichier PDF", type="pdf")

        if uploaded_pdf is not None:
            # Extraction du texte du PDF
            text = extract_text_from_pdf(uploaded_pdf)

            if text:
                modified_text = st.text_area("Contenu extrait du PDF :", value=text, height=200)
            else:
                st.error("Aucun texte n'a pu être extrait de ce fichier PDF.")

    elif input_method == "Saisir du texte":
        # Zone de texte pour saisir directement le texte
        modified_text = st.text_area("Saisir votre texte ici :", height=200)

    # Choix de la langue
    language = st.selectbox("Choisissez la langue de l'audio", ['fr', 'en', 'es', 'de'])

    # Bouton pour générer l'audio
    if st.button("Convertir en audio"):
        if modified_text:
            audio_file = text_to_audio(modified_text, lang=language)

            # Lecture de l'audio et téléchargement
            st.audio(audio_file, format='audio/mp3')
            st.download_button("Télécharger l'audio", data=audio_file, file_name="output.mp3", mime="audio/mp3")
        else:
            st.error("Veuillez entrer du texte avant de convertir.")
elif option == "Traduction PDF":
    st.header("Traduire un pdf")

    # Téléchargement du fichier PDF
    uploaded_pdf = st.file_uploader("Télécharger un fichier PDF", type=["pdf"])

    # Sélection de la langue de traduction
    language = st.selectbox("Choisissez la langue de destination", ['fr', 'en', 'es', 'de', 'ur'])  # Ajoutez 'ur' pour l'ourdou

    if uploaded_pdf is not None:
        if st.button("Traduire"):
            # Extraction du texte du PDF
            original_text = extract_text_from_pdf(uploaded_pdf)
            
            # Traduction du texte
            translated_text = translate_text(original_text, language)
            
            if translated_text:
                # Diviser le texte traduit en morceaux
                text_chunks = split_text(translated_text)
                
                # Création d'un nouveau PDF avec le texte traduit
                output_pdf = "translated_output.pdf"
                create_pdf(text_chunks, output_pdf)
                st.success("PDF traduit créé avec succès !")
                st.download_button("Télécharger le PDF traduit", data=output_pdf, file_name="translated_output.pdf")

elif option == "Écriture (Audio vers Texte)":
    st.header("Convertir un Enregistrement Audio en Texte")

    # Téléchargement du fichier audio (format WAV )
    uploaded_audio = st.file_uploader("Télécharger un fichier audio (WAV )", type=["wav"])

    if uploaded_audio is not None:
        st.audio(uploaded_audio)

        if st.button("Convertir en texte"):
            with st.spinner("Transcription en cours..."):
                result_text = audio_to_text(uploaded_audio)

            if result_text:
                # Améliorer le texte
                improved_text = improve_text(result_text)
                st.write("Texte extrait de l'audio :")
                st.text_area("Résultat", value=improved_text, height=200)
            else:
                st.error("La transcription n'a pas pu être effectuée.")
    else:
        st.info("Veuillez télécharger un fichier audio pour commencer.")