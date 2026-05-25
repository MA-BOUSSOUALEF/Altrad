"""
Agent GPT-4o — Comprend les demandes client et modifie les paramètres
uniquement les VALEURS dans params_session.json
"""

import json
import math
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

SYSTEM_PROMPT = """Tu es un agent expert en échafaudage Altrad Plettac Metrix.
Tu aides les clients à configurer leur échafaudage en français.

Tu as accès aux paramètres actuels de l'échafaudage (JSON).
Quand le client demande une modification, tu DOIS retourner un JSON avec UNIQUEMENT les valeurs modifiées.

RÈGLES STRICTES :
- Tu modifies UNIQUEMENT les valeurs numériques ou textuelles des paramètres
- Tu ne modifies JAMAIS la structure du script ou des prompts
- Tu réponds toujours en français de manière professionnelle et concise

PARAMÈTRES DISPONIBLES ET LEURS VALEURS POSSIBLES :
- classe : 2, 3, 4 ou 5
- materiel : 70 ou 100
- garde_corps : "permanent" ou "standard"
- longueur : nombre en mètres (1.2 à 100)
- hauteur : nombre en mètres (3.4 à 26.25)
- maille : 2.0, 2.5 ou 3.0
- mailles_list : liste de mailles ex: [2.0, 3.0, 3.0, 2.0]
- espacement_niveaux : 2.0, 2.5 ou 3.0
- verins : "ASV5" ou "ASV8"
- calage : "AMX1" ou "personnalise"
- console_facade : 0, 40 ou 70
- console_rue : 0, 40 ou 70
- console_gauche : 0, 40 ou 70
- console_droit : 0, 40 ou 70
- nom_projet : texte
- adresse : texte
- entreprise : texte
- montage : texte

CORRESPONDANCES MODIFICATIONS :
- "supprimer un étage" / "enlever un niveau" → hauteur -= espacement_niveaux
- "ajouter un étage" / "ajouter un niveau" → hauteur += espacement_niveaux
- "ajouter une travée" → ajouter 3.0 à la fin de mailles_list
- "ajouter une travée de Xm" → ajouter X à la fin de mailles_list
- "supprimer une travée" / "enlever une travée" → retirer le dernier élément de mailles_list
- "console Xcm facade" → console_facade = X
- "sans console" → console_facade = 0
- "classe X" → classe = X
- "passer en classe X" → classe = X
- "garde-corps standard" → garde_corps = "standard"
- "garde-corps permanent" → garde_corps = "permanent"
- "longueur Xm" → longueur = X (recalculer mailles_list)
- "hauteur Xm" → hauteur = X
- "maille de Xm" → maille = X (recalculer mailles_list)
- "Metrix 100" → materiel = 100
- "Metrix 70" → materiel = 70

FORMAT DE RÉPONSE OBLIGATOIRE (JSON) :
{
  "message": "Votre message en français pour le client",
  "modifications": {
    "parametre1": valeur1,
    "parametre2": valeur2
  },
  "demande_generation": true/false,
  "demande_pdf": false
}

- "message" : explication claire de ce que tu fais
- "modifications" : UNIQUEMENT les paramètres qui changent (vide {} si pas de modification)
- "demande_generation" : true si le client veut voir les images (après modification ou explicitement)
- "demande_pdf" : true UNIQUEMENT si le client dit "génère le PDF" / "télécharger" / "pdf"

EXEMPLES :

Client : "supprimer un étage"
Params actuels : hauteur=12.0, espacement_niveaux=2.0
Réponse :
{
  "message": "J'ai supprimé un niveau. La hauteur passe de 12m à 10m (5 niveaux x 2m). Je régénère les vues ?",
  "modifications": {"hauteur": 10.0},
  "demande_generation": false,
  "demande_pdf": false
}

Client : "oui" (après une proposition de régénération)
Réponse :
{
  "message": "Je génère les nouvelles vues...",
  "modifications": {},
  "demande_generation": true,
  "demande_pdf": false
}

Client : "génère le PDF"
Réponse :
{
  "message": "Je génère votre rapport PDF...",
  "modifications": {},
  "demande_generation": false,
  "demande_pdf": true
}

Client : "quelle est la différence entre classe 4 et 5 ?"
Réponse :
{
  "message": "Classe 4 : 300 daN/m² pour travaux de maçonnerie. Classe 5 : 450 daN/m² pour gros stockage de matériaux. Votre configuration actuelle est en Classe 5.",
  "modifications": {},
  "demande_generation": false,
  "demande_pdf": false
}

IMPORTANT : Retourne UNIQUEMENT le JSON, pas de texte avant ou après."""


def get_default_params():
    """Paramètres par défaut au démarrage."""
    return {
        "project": {
            "nom_projet": "Mon Projet",
            "adresse": "",
            "entreprise": "",
            "montage": ""
        },
        "scaffolding": {
            "classe": 5,
            "materiel": 70,
            "garde_corps": "permanent",
            "longueur": 15.0,
            "hauteur": 8.0,
            "maille": 3.0,
            "mailles_list": [3.0, 3.0, 3.0, 3.0, 3.0],
            "espacement_niveaux": 2.0,
            "verins": "ASV5",
            "calage": "AMX1",
            "console_facade": 0,
            "console_rue": 0,
            "console_gauche": 0,
            "console_droit": 0
        }
    }


def params_to_summary(params):
    """Résumé lisible des params pour le contexte GPT-4o."""
    s = params["scaffolding"]
    p = params["project"]
    nb_t = len(s["mailles_list"])
    nb_n = math.ceil(s["hauteur"] / s["espacement_niveaux"])
    mailles_str = " ; ".join([f"{m}m" for m in s["mailles_list"]])
    return f"""PARAMÈTRES ACTUELS :
- Projet : {p['nom_projet']} | Entreprise : {p['entreprise']}
- Matériel : Metrix {s['materiel']} | Classe : {s['classe']}
- Garde-corps : {s['garde_corps']}
- Longueur : {s['longueur']}m | {nb_t} travées : {mailles_str}
- Hauteur : {s['hauteur']}m | {nb_n} niveaux x {s['espacement_niveaux']}m
- Vérins : {s['verins']} | Calage : {s['calage']}
- Console facade : {s['console_facade']}cm | Console gauche : {s['console_gauche']}cm
- Console rue : {s['console_rue']}cm | Console droit : {s['console_droit']}cm"""


def apply_modifications(params, modifications):
    """
    Applique les modifications au params.
    Ne touche qu'aux valeurs — jamais à la structure.
    """
    s = params["scaffolding"]
    p = params["project"]

    for key, value in modifications.items():
        # Paramètres projet
        if key in ["nom_projet", "adresse", "entreprise", "montage"]:
            p[key] = value

        # Paramètres échafaudage
        elif key == "longueur":
            s["longueur"] = float(value)
            # Recalculer mailles_list si longueur change
            maille = s["maille"]
            nb_t = math.ceil(s["longueur"] / maille)
            s["mailles_list"] = [maille] * nb_t

        elif key == "hauteur":
            s["hauteur"] = float(value)

        elif key == "maille":
            s["maille"] = float(value)
            # Recalculer mailles_list
            nb_t = math.ceil(s["longueur"] / float(value))
            s["mailles_list"] = [float(value)] * nb_t

        elif key == "mailles_list":
            s["mailles_list"] = [float(m) for m in value]
            s["longueur"] = round(sum(s["mailles_list"]), 2)

        elif key == "classe":
            s["classe"] = int(value)

        elif key == "materiel":
            s["materiel"] = int(value)

        elif key == "garde_corps":
            s["garde_corps"] = str(value)

        elif key == "espacement_niveaux":
            s["espacement_niveaux"] = float(value)

        elif key == "verins":
            s["verins"] = str(value)

        elif key == "calage":
            s["calage"] = str(value)

        elif key in ["console_facade", "console_rue", "console_gauche", "console_droit"]:
            s[key] = int(value)

    return params


def chat_with_agent(user_message, params, conversation_history):
    """
    Envoie le message au GPT-4o agent.
    Retourne (response_dict, updated_params, updated_history)
    """
    if not OPENAI_API_KEY:
        return {
            "message": "Clé OpenAI non configurée.",
            "modifications": {},
            "demande_generation": False,
            "demande_pdf": False
        }, params, conversation_history

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Construire le contexte avec les params actuels
    context = params_to_summary(params)

    # Ajouter le message utilisateur avec contexte
    conversation_history.append({
        "role": "user",
        "content": f"{context}\n\nClient : {user_message}"
    })

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + conversation_history,
        max_tokens=1000,
        temperature=0.3
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "message": raw,
            "modifications": {},
            "demande_generation": False,
            "demande_pdf": False
        }

    # Appliquer les modifications
    if result.get("modifications"):
        params = apply_modifications(params, result["modifications"])

    # Ajouter la réponse à l'historique
    conversation_history.append({
        "role": "assistant",
        "content": result.get("message", "")
    })

    return result, params, conversation_history


def analyze_building_gpt4o(image_path):
    """Analyse le bâtiment avec GPT-4o Vision."""
    import base64
    if not OPENAI_API_KEY:
        return "a multi-story classical European building"

    client = OpenAI(api_key=OPENAI_API_KEY)
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            {"type": "text", "text": (
                "Describe this building in one precise sentence in English. "
                "Include: type, architectural style, floors, facade material/color. "
                "Reply with the description only."
            )}
        ]}],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()