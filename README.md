# 🧾 Smart Facture

**Smart Facture** est une application IA qui analyse les images de factures (par exemple, des commandes iPhone) pour générer automatiquement un fichier PDF structuré.

## 🚀 Fonctionnalités
- 📸 Capture ou upload d’une photo de facture
- 🤖 Extraction automatique des informations (nom, téléphone, produits, prix…)
- 🧾 Génération automatique d’un PDF professionnel
- 💬 Interface chat intuitive

---

## 🧰 Technologies utilisées
- **Python 3.10+**
- **Streamlit** (interface)
- **Tesseract OCR** (extraction de texte)
- **Groq API** (LLM pour extraction structurée)
- **ReportLab** (génération PDF)

---

## Structure du projet
SmartFacture/
├─ chatbot.py # Interface Streamlit
├─ main.py # Extraction et génération PDF
├─ groq_client.py # Gestion API Groq
├─ requirements.txt # Dépendances Python
├─ packages.txt
└─ README.md

## 🛠️ Installation
git clone https://github.com/ZiedEll/SmartFacture.git
cd SmartFacture
pip install -r requirements.txt  

## 🌐 Déploiement
L'application est déployée et accessible ici : [Smart Facture - Streamlit Cloud](https://smartfacture.streamlit.app/)

Exécution
streamlit run chatbot.py

👨‍💻 Auteur
Zied Ellouze
Ingénieur IA 
ellouzezied3@gmail.com
