# main.py
import json, re
import os
from PIL import Image
import pytesseract
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
from io import BytesIO
from groq_client import get_groq_client

client = get_groq_client()

# === DOSSIER POUR LES PDF (crée si n'existe pas) ===
PDF_DIR = "factures_generees"
os.makedirs(PDF_DIR, exist_ok=True)

# === NOM UNIQUE PAR FACTURE ===
def get_unique_pdf_path():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(PDF_DIR, f"facture_{timestamp}.pdf")

# === SUPPRIME TOUS LES ANCIENS PDF (optionnel : garde les 5 derniers) ===
def nettoyer_anciens_pdf(keep_last=5):
    if not os.path.exists(PDF_DIR):
        return
    pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]
    pdf_files.sort(key=lambda x: os.path.getmtime(os.path.join(PDF_DIR, x)), reverse=True)
    for old_file in pdf_files[keep_last:]:
        try:
            os.remove(os.path.join(PDF_DIR, old_file))
        except:
            pass  # Ignore les erreurs de suppression

def generer_facture(data, output_path=None):
    if output_path is None:
        output_path = get_unique_pdf_path()

    # Nettoie les anciens PDF (garde les 5 derniers)
    nettoyer_anciens_pdf(keep_last=5)

    c = canvas.Canvas(output_path, pagesize=A4)
    largeur, hauteur = A4
    c.setFont("Helvetica-Bold", 18)
    c.drawString(30, hauteur - 50, "FACTURE")
    c.setFont("Helvetica", 10)
    c.drawString(30, hauteur - 70, f"Date : {datetime.today().strftime('%d/%m/%Y')}")

    y = hauteur - 110
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y, "Informations du client :")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Nom : {data.get('nom_client', 'Non précisé')}")
    y -= 15
    c.drawString(40, y, f"Téléphone : {data.get('telephone', 'Non précisé')}")
    y -= 15
    c.drawString(40, y, f"Adresse : {data.get('adresse', 'Non précisée')}")

    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y, "Produits :")
    y -= 20
    total = 0
    for p in data.get("produits", []):
        ligne = f"{p.get('quantite', 1)}x {p.get('produit', '')} ({p.get('couleur', '')}) - {p.get('prix', 0)} €"
        c.drawString(40, y, ligne)
        total += (p.get('prix', 0) or 0) * (p.get('quantite', 1) or 1)
        y -= 15
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y, f"Total : {total} €")

    y -= 30
    c.setFont("Helvetica", 10)
    c.drawString(30, y, f"Délai livraison : {data.get('delai_livraison', 'Non précisé')}")

    c.save()
    return output_path


def extraire_infos_depuis_image(image_bytes):
    img = Image.open(BytesIO(image_bytes))
    texte = pytesseract.image_to_string(img, lang='fra')

    prompt = f"""
Tu es un assistant expert en extraction de commandes iPhone.
Analyse ce texte et renvoie UNIQUEMENT le JSON suivant :
{{
  "nom_client": str,
  "telephone": str,
  "produits": [
    {{
      "produit": str,
      "couleur": str,
      "quantite": int,
      "prix": float
    }}
  ],
  "delai_livraison": str,
  "adresse": str
}}
Texte :
{texte}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Tu es un assistant expert en extraction de commandes iPhone."},
                {"role": "user", "content": prompt}
            ]
        )

        raw = response.choices[0].message.content.strip()
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not json_match:
            return {"error": "Pas de JSON trouvé dans la réponse", "raw": raw}

        data = json.loads(json_match.group(0))
        pdf_path = generer_facture(data)  # Nouveau PDF à chaque fois
        return {"data": data, "pdf": pdf_path}

    except Exception as e:
        return {"error": f"Erreur Groq/JSON : {str(e)}", "raw": raw if 'raw' in locals() else ""}