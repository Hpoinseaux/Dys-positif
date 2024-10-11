import streamlit as st
from gtts import gTTS
from io import BytesIO

# Fonction pour convertir du texte en audio avec gTTS
def text_to_audio(text, lang='fr'):
    tts = gTTS(text=text, lang=lang)
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)  # Remettre le pointeur au début du fichier pour la lecture
    return audio_file

# Interface Streamlit
st.title("Convertisseur de Texte en Audio")

# Choisir d'uploader un fichier texte ou d'écrire directement du texte
uploaded_file = st.file_uploader("Télécharger un fichier texte (.txt)", type="txt")

if uploaded_file is not None:
    # Lecture du contenu du fichier texte
    text = uploaded_file.read().decode("utf-8")
    st.text_area("Contenu du fichier texte :", value=text, height=200)

else:
    # Si aucun fichier n'est téléchargé, permettre à l'utilisateur de saisir du texte directement
    text = st.text_area("Ou écrivez directement le texte ici :", height=200)

# Option pour choisir la langue
language = st.selectbox("Choisissez la langue de l'audio", ['fr', 'en', 'es', 'de'])

# Bouton pour générer l'audio
if st.button("Convertir en audio"):
    if text:
        audio_file = text_to_audio(text, lang=language)
        
        # Télécharger le fichier audio en MP3
        st.audio(audio_file, format='audio/mp3')
        st.download_button("Télécharger l'audio", data=audio_file, file_name="output.mp3", mime="audio/mp3")
    else:
        st.warning("Veuillez entrer ou télécharger du texte pour générer l'audio.")