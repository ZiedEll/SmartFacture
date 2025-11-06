# interface_chatbot.py
import streamlit as st
from PIL import Image
from io import BytesIO
from main import extraire_infos_depuis_image

# === CONFIG ===
st.set_page_config(page_title="Smart Facture", page_icon="🧾", layout="centered")

# === CSS pour chat et interface ===
st.markdown("""
<style>
    .chat-bubble {padding: 1em; border-radius: 1em; margin: 0.5em 0; max-width: 80%; word-wrap: break-word;}
    .user-bubble {background-color: #d1e7dd; margin-left: auto;}
    .assistant-bubble {background-color: #f8d7da; margin-right: auto;}
    .chat-container {border: 1px solid #dee2e6; border-radius: 0.5em; padding: 1em; background: #fff; margin-bottom: 1em;}
    #MainMenu, header, footer {visibility: hidden;}
    body {background-color: #f4f6f9;}
</style>
""", unsafe_allow_html=True)

# === TITRE ===
st.title("🧾 Smart Facture - Assistant IA")

# === HISTORIQUE DU CHAT ===
if "messages" not in st.session_state:
    st.session_state.messages = []

# === AFFICHAGE DU CHAT ===
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    role_class = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
    label = "Vous" if msg["role"] == "user" else "Assistant"
    if msg.get("type") == "image":
        st.markdown(f'<div class="chat-bubble {role_class}"><strong>{label} :</strong><br>'
                    f'<img src="data:image/png;base64,{msg["content"]}" style="max-width:100%; border-radius:0.5em; margin-top:0.5em;"></div>',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble {role_class}"><strong>{label} :</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# === SAISIE UTILISATEUR ===
user_input = st.chat_input("Écrivez votre message...")

# === UPLOADER IMAGE ===
uploaded_file = st.file_uploader("📸 Upload une facture (jpg, png)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Ajouter image dans le chat
    img = Image.open(uploaded_file)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    import base64
    img_str = base64.b64encode(buffered.getvalue()).decode()
    st.session_state.messages.append({
        "role": "user",
        "type": "image",
        "content": img_str
    })

    # === ANALYSE IMAGE ET GÉNÉRATION PDF ===
    try:
        result = extraire_infos_depuis_image(uploaded_file.getvalue())
        if "error" not in result:
            pdf_bytes = open(result["pdf"], "rb").read()

            # BOUTON CLAIR DE TÉLÉCHARGEMENT
            st.download_button(
                label="📄 Télécharger votre facture PDF",
                data=pdf_bytes,
                file_name="facture_client.pdf",
                mime="application/pdf"
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": "Facture analysée avec succès ! Cliquez sur le bouton ci-dessus pour télécharger votre PDF."
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Erreur lors de l'analyse : {result.get('error', 'Inconnue')}"
            })
    except Exception as e:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Erreur : {str(e)}"
        })

# === TRAITEMENT TEXTE ===
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    response = "Prends une photo de ta facture pour que je l’analyse !" if "facture" in user_input.lower() else "Je suis prêt ! Téléverse une photo ou décris-moi ta facture."
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.experimental_rerun()
