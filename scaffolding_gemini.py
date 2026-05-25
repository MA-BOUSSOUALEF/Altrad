"""
Générateur d'échafaudage — Pipeline Matplotlib → Gemini
1. Matplotlib génère l'échafaudage exact (dimensions 100% précises)
2. Gemini reçoit l'image Matplotlib et la rend réaliste en 3D
3. Gemini applique l'échafaudage réaliste sur la photo du bâtiment
4. Génération du PDF professionnel

Prérequis:
    pip install google-genai google-generativeai pillow python-dotenv reportlab matplotlib numpy

Variables d'environnement (.env) :
    GEMINI_API_KEY  → votre clé Google AI Studio
"""

import os, time, math, mimetypes, argparse, json
from datetime import datetime
from dotenv import load_dotenv

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import google.generativeai as genai
from google import genai as genai_client
from google.genai import types
from PIL import Image

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = "gemini-3-pro-image-preview"
GEMINI_TEXT    = "gemini-2.5-flash"

C_BG    = '#1A1A2E'
C_TUBE  = '#D8DCE0'
C_PLANK = '#DC3C14'
C_DIM   = '#4080DC'
C_LABEL = '#FF5050'
C_VERIN = '#909090'

CATALOGUE = {
    "AA11":  {"designation": "TUBE D'AMARRAGE STAND. DE 110",     "poids": 3.90,  "prix": 21.32},
    "ACHE":  {"designation": "CHEVILLE NYLON D.14 X 70 MM",       "poids": 0.00,  "prix": 0.30},
    "AMX1":  {"designation": "CALE MADRIER 8 X 23 LONG. 50",      "poids": 3.70,  "prix": 8.58},
    "APA2":  {"designation": "PITON D'AMARRAGE DE 12",            "poids": 0.20,  "prix": 2.30},
    "ASV5":  {"designation": "SOCLE A VERIN GALVA DE 59",         "poids": 3.20,  "prix": 23.79},
    "KDV4":  {"designation": "DIAGO. VERTI. METRIX 200 X 200",    "poids": 10.10, "prix": 54.48},
    "KDV6":  {"designation": "DIAGO. VERTI. METRIX 200 X 300",    "poids": 12.40, "prix": 62.14},
    "KEMB":  {"designation": "EMBASE DE DEPART METRIX",           "poids": 2.10,  "prix": 16.73},
    "KGH1":  {"designation": "GARDE-CORPS PERMANENT DE 0.70",     "poids": 7.20,  "prix": 76.99},
    "KGH4":  {"designation": "GARDE-CORPS PERMANENT DE 2 M",      "poids": 10.00, "prix": 124.77},
    "KGH6":  {"designation": "GARDE-CORPS PERMANENT DE 3 M",      "poids": 15.20, "prix": 141.83},
    "KKR1":  {"designation": "CONSOLE METRIX RENFORCE 2 PL.",     "poids": 4.86,  "prix": 66.30},
    "KKR8":  {"designation": "CONSOLE METRIX RENFORCEE 1 PL.",    "poids": 3.20,  "prix": 55.54},
    "KLC1":  {"designation": "LISSE METRIX STANDARD 70",          "poids": 3.16,  "prix": 25.27},
    "KLC4":  {"designation": "LISSE METRIX STANDARD 200",         "poids": 7.00,  "prix": 42.12},
    "KLC6":  {"designation": "LISSE METRIX STANDARD 300",         "poids": 10.10, "prix": 53.24},
    "KLC8":  {"designation": "LISSE METRIX STANDARD 40",          "poids": 2.10,  "prix": 30.69},
    "KMC1":  {"designation": "PLANCHER ACIER 15/10E 30 X 70",     "poids": 6.40,  "prix": 68.32},
    "KMC4":  {"designation": "PLANCHER ACIER 15/10E 30 X 200",    "poids": 14.50, "prix": 92.12},
    "KMC5":  {"designation": "PLANCHER ACIER 15/10E 30 X 300",    "poids": 20.80, "prix": 110.86},
    "KPE6":  {"designation": "PLANCHER TRAPPE + ECH. 60 X 300",   "poids": 24.10, "prix": 531.27},
    "KPI4":  {"designation": "PLINTHE BOIS DE 200",               "poids": 4.27,  "prix": 30.84},
    "KPI6":  {"designation": "PLINTHE BOIS DE 300",               "poids": 6.31,  "prix": 37.53},
    "KPT2":  {"designation": "POTEAU STANDARD METRIX DE 100",     "poids": 5.40,  "prix": 32.62},
    "KPT4":  {"designation": "POTEAU STANDARD METRIX DE 200",     "poids": 10.05, "prix": 54.11},
}


# ─────────────────────────────────────────────
# COLLECTE DES PARAMÈTRES
# ─────────────────────────────────────────────

def ask(question, choices=None, default=None):
    if choices:
        print(f"\n  {question}")
        for i, c in enumerate(choices, 1):
            print(f"    {i}. {c}")
        while True:
            rep = input(f"  Votre choix (1-{len(choices)}) : ").strip()
            if rep.isdigit() and 1 <= int(rep) <= len(choices):
                return choices[int(rep) - 1]
            print(f"  Entrez un nombre entre 1 et {len(choices)}")
    else:
        rep = input(f"\n  {question} : ").strip()
        return rep if rep else (default or "")


def ask_float(question, min_val, max_val, default):
    while True:
        rep = input(f"\n  {question} (entre {min_val} et {max_val}, defaut={default}) : ").strip()
        if not rep:
            return default
        try:
            val = float(rep.replace(",", "."))
            if min_val <= val <= max_val:
                return val
            print(f"  Valeur hors plage ({min_val} - {max_val})")
        except ValueError:
            print("  Entrez un nombre valide")


def ask_mailles(maille_principale, longueur_totale):
    nb_t_auto = math.ceil(longueur_totale / maille_principale)
    print(f"\n  Longueur totale : {longueur_totale}m -> {nb_t_auto} travees de {maille_principale}m")
    choix = input("\n  Personnaliser les mailles par travee ? (o/n) : ").strip().lower()
    if choix not in ("o", "oui", "y", "yes"):
        return [maille_principale] * nb_t_auto
    print(f"\n  Entrez chaque maille (ENTREE = defaut {maille_principale}m)")
    mailles = []
    cumul   = 0.0
    t       = 1
    while cumul < longueur_totale - 0.01:
        reste = round(longueur_totale - cumul, 2)
        while True:
            rep = input(f"  T{t} (reste {reste}m, defaut={min(maille_principale, reste)}) : ").strip()
            val = float(rep.replace(",", ".")) if rep else min(maille_principale, reste)
            if 0 < val <= reste + 0.01:
                break
            print("  Valeur invalide")
        mailles.append(round(val, 2))
        cumul = round(cumul + val, 2)
        t    += 1
    print(f"\n  Mailles : {' ; '.join([str(m)+'m' for m in mailles])}")
    return mailles


def collect_project_info():
    print("\n" + "="*60)
    print("  INFORMATIONS DU CHANTIER")
    print("="*60)
    return {
        "nom_projet": ask("Nom du projet",                default="Mon projet"),
        "adresse":    ask("Adresse du chantier",          default=""),
        "entreprise": ask("Entreprise utilisatrice",      default=""),
        "montage":    ask("Entreprise chargee du montage",default=""),
    }


def collect_user_parameters():
    print("\n" + "="*60)
    print("   CONFIGURATEUR D'ECHAFAUDAGE — Style Altrad Plettac")
    print("="*60)
    params = {}

    print("\n" + "-"*60)
    print("  ETAPE 1 : Classe")
    print("-"*60)
    params["classe"] = ask("Classe :", [
        "Classe 2 — 150 daN/m2", "Classe 3 — 200 daN/m2",
        "Classe 4 — 300 daN/m2", "Classe 5 — 450 daN/m2",
    ])

    print("\n" + "-"*60)
    print("  ETAPE 2 : Materiel et garde-corps")
    print("-"*60)
    params["materiel"]    = ask("Materiel :", [
        "Metrix 70 — Largeur 70 cm", "Metrix 100 — Largeur 100 cm"])
    params["garde_corps"] = ask("Garde-corps :", [
        "Garde-corps permanent de securite", "Garde-corps standard"])

    print("\n" + "-"*60)
    print("  ETAPE 3 : Dimensions")
    print("-"*60)
    params["longueur"] = ask_float("Longueur facade (m)", 1.2, 100.0, 15.0)
    params["hauteur"]  = ask_float("Hauteur facade (m)",  3.4, 26.25,  8.0)

    print("\n" + "-"*60)
    print("  ETAPE 4 : Maille principale")
    print("-"*60)
    maille_str       = ask("Maille principale :", ["2.0 m", "2.5 m", "3.0 m"])
    params["maille"] = maille_str
    maille_val       = float(maille_str.split()[0])

    print("\n" + "-"*60)
    print("  ETAPE 4b : Mailles par travee")
    print("-"*60)
    params["mailles_list"] = ask_mailles(maille_val, params["longueur"])

    print("\n" + "-"*60)
    print("  ETAPE 5 : Niveaux")
    print("-"*60)
    params["espacement_niveaux"] = ask("Espacement niveaux :", [
        "2.0 m (standard)", "2.5 m", "3.0 m"])
    params["verins"] = ask("Verins :", ["ASV5 — 4 cm", "ASV8 — 8 cm"])
    params["calage"] = ask("Calage :", [
        "AMX1 — 8 cm (standard)", "Calage personnalise — 4 cm min"])

    print("\n" + "-"*60)
    print("  ETAPE 6 : Consoles")
    print("-"*60)
    cc = ["Pas de console", "Console largeur 40 cm", "Console largeur 70 cm"]
    params["console_facade"] = ask("Console facade :", cc)
    params["console_rue"]    = ask("Console rue :",    cc)
    params["console_gauche"] = ask("Console gauche :", cc)
    params["console_droit"]  = ask("Console droit :",  cc)

    mailles = params["mailles_list"]
    nb_t    = len(mailles)
    esp     = float(params["espacement_niveaux"].split()[0])
    nb_n    = math.ceil(params["hauteur"] / esp)

    print("\n" + "="*60)
    print("  RESUME")
    print("="*60)
    print(f"  Longueur   : {params['longueur']}m | {nb_t} travees : {' ; '.join([str(m)+'m' for m in mailles])}")
    print(f"  Hauteur    : {params['hauteur']}m  | {nb_n} niveaux x {esp}m")
    print(f"  Consoles   : facade={params['console_facade']} | gauche={params['console_gauche']}")
    print("="*60)

    if input("\n  Confirmer ? (o/n) : ").strip().lower() not in ("o","oui","y","yes"):
        exit(0)
    return params


# ─────────────────────────────────────────────
# CALCUL MATÉRIAUX
# ─────────────────────────────────────────────

def calculate_materials(params):
    mailles = params["mailles_list"]
    nb_t    = len(mailles)
    esp     = float(params["espacement_niveaux"].split()[0])
    nb_n    = math.ceil(params["hauteur"] / esp)
    has_c   = params["console_facade"] != "Pas de console"
    raw = [
        ("AA11", nb_t*nb_n), ("ACHE", nb_t*nb_n), ("AMX1", nb_t+1),
        ("APA2", nb_t*nb_n), ("ASV5", nb_t+1),    ("KDV4", nb_t),
        ("KDV6", nb_t),      ("KEMB", nb_t+1),    ("KGH1", nb_n*2),
        ("KGH4", max(1, nb_t*nb_n//3)), ("KGH6", nb_t*nb_n),
        ("KKR1", nb_t*2 if has_c else 0), ("KKR8", nb_t if has_c else 0),
        ("KLC1", nb_t*nb_n), ("KLC4", max(1, nb_t*nb_n//2)),
        ("KLC6", nb_t*nb_n), ("KLC8", max(1, nb_t*nb_n//3)),
        ("KMC1", nb_t*2),    ("KMC4", max(1, nb_t*nb_n//2)),
        ("KMC5", nb_t*nb_n*2), ("KPE6", nb_t),
        ("KPI4", max(1, nb_t*nb_n//2)), ("KPI6", nb_t*nb_n),
        ("KPT2", nb_t*nb_n*2), ("KPT4", nb_t*2),
    ]
    result = []
    for code, qty in raw:
        if qty <= 0: continue
        cat = CATALOGUE.get(code, {})
        result.append({"article": code, "designation": cat.get("designation", code),
                       "poids": round(cat.get("poids",0)*qty,2),
                       "prix": round(cat.get("prix",0),2), "qte": qty,
                       "montant": round(cat.get("prix",0)*qty,2)})
    return result


# ─────────────────────────────────────────────
# GÉOMÉTRIE
# ─────────────────────────────────────────────

def get_geometry(params):
    mailles  = params["mailles_list"]
    esp      = float(params["espacement_niveaux"].split()[0])
    nb_n     = math.ceil(params["hauteur"] / esp)
    largeur  = 0.70 if "70" in params["materiel"] else 1.00
    c_facade = 0.70 if "70" in params["console_facade"] else (0.40 if "40" in params["console_facade"] else 0.0)
    c_gauche = 0.70 if "70" in params["console_gauche"] else (0.40 if "40" in params["console_gauche"] else 0.0)
    positions_x = [0.0]
    for m in mailles:
        positions_x.append(round(positions_x[-1] + m, 2))
    niveaux_y = [round(i * esp, 1) for i in range(nb_n + 1)]
    return {
        "mailles": mailles, "nb_t": len(mailles), "nb_n": nb_n,
        "esp": esp, "largeur": largeur, "c_facade": c_facade, "c_gauche": c_gauche,
        "positions_x": positions_x, "niveaux_y": niveaux_y,
        "total_l": round(sum(mailles), 2), "total_h": params["hauteur"],
    }


# ─────────────────────────────────────────────
# MATPLOTLIB — VUES EXACTES
# ─────────────────────────────────────────────

def draw_isometric_view(params, output_path):
    g = get_geometry(params)
    px, ny = g["positions_x"], g["niveaux_y"]
    larg, cf = g["largeur"], g["c_facade"]
    iso_x, iso_y, scale = 0.45, 0.28, 60
    fig, ax = plt.subplots(figsize=(16, 12), facecolor=C_BG)
    ax.set_facecolor(C_BG); ax.axis('off')

    def iso(x, y, z):
        return x*scale + z*scale*iso_x, y*scale + z*scale*iso_y
    ox, oy = 2.0, 1.5
    def pt(x, y, z):
        px2, py2 = iso(x, y, z)
        return ox+px2, oy+py2

    depth = larg
    from matplotlib.patches import Polygon as MplPolygon
    wall_pts = [pt(px[0],0,depth), pt(px[-1],0,depth),
                pt(px[-1],g["total_h"]+1.0,depth), pt(px[0],g["total_h"]+1.0,depth)]
    wall = MplPolygon(wall_pts, closed=True, facecolor='#8B5A2B', edgecolor='#6B4020', linewidth=1, zorder=1)
    ax.add_patch(wall)

    def tube2d(p1, p2, color=C_TUBE, lw=2.0, zorder=3):
        ax.plot([p1[0],p2[0]], [p1[1],p2[1]], color=color, linewidth=lw, solid_capstyle='round', zorder=zorder)

    def plank2d(x1, x2, h, z, color=C_PLANK):
        pts = [pt(x1,h-0.07,z), pt(x2,h-0.07,z), pt(x2,h+0.07,z), pt(x1,h+0.07,z)]
        poly = MplPolygon(pts, closed=True, facecolor=color, edgecolor='#AA2A08', linewidth=0.5, zorder=4)
        ax.add_patch(poly)

    for x in px:
        tube2d(pt(x,0,0), pt(x,g["total_h"],0), C_TUBE, 2.5, zorder=5)
        tube2d(pt(x,0,depth), pt(x,g["total_h"],depth), '#9098A0', 1.5, zorder=2)

    for n, h in enumerate(ny):
        tube2d(pt(px[0],h,0), pt(px[-1],h,0), C_TUBE, 2.0, zorder=5)
        tube2d(pt(px[0],h,depth), pt(px[-1],h,depth), '#9098A0', 1.2, zorder=2)
        tube2d(pt(px[0],h,0), pt(px[0],h,depth), '#A8B0B8', 1.5, zorder=3)
        tube2d(pt(px[-1],h,0), pt(px[-1],h,depth), '#A8B0B8', 1.5, zorder=3)
        if n < g["nb_n"]:
            h_next = ny[n+1]
            ph = h+(h_next-h)*0.78
            for i in range(g["nb_t"]):
                plank2d(px[i]+0.04, px[i+1]-0.04, ph, 0)
            for i in range(0, g["nb_t"], 2):
                x2 = px[min(i+1, g["nb_t"])]
                tube2d(pt(px[i],h,0), pt(x2,h_next,0), C_TUBE, 1.3, zorder=4)
                tube2d(pt(x2,h,0), pt(px[i],h_next,0), C_TUBE, 1.3, zorder=4)

    gc_h = g["total_h"]+0.5
    tube2d(pt(px[0],gc_h,0), pt(px[-1],gc_h,0), '#B0C8D8', 2.0, zorder=5)
    if cf > 0:
        for x in px:
            tube2d(pt(x,0,0), pt(x,0,-cf), '#C0C8D0', 1.5, zorder=5)
        tube2d(pt(px[0],0,-cf), pt(px[-1],0,-cf), '#C0C8D0', 1.5, zorder=5)

    for x in px:
        p = pt(x,0,0); p2 = pt(x,-0.3,0)
        ax.plot(p[0], p[1], 'o', color=C_VERIN, markersize=7, zorder=6)
        tube2d(p2, p, C_VERIN, 3.5, zorder=6)

    xe = px[0]-0.3
    for n in range(g["nb_n"]):
        y1, y2 = ny[n], ny[n+1]
        tube2d(pt(xe-0.12,y1,0), pt(xe-0.12,y2,0), '#A0A8B0', 1.8, zorder=6)
        tube2d(pt(xe+0.12,y1,0), pt(xe+0.12,y2,0), '#A0A8B0', 1.8, zorder=6)
        for s in range(5):
            ys = y1+(y2-y1)*s/4
            tube2d(pt(xe-0.15,ys,0), pt(xe+0.15,ys,0), '#B0B8C0', 1.2, zorder=6)

    for h in ny:
        p = pt(px[-1],h,0)
        ax.plot([p[0],p[0]+0.3*scale], [p[1],p[1]], color=C_LABEL, linewidth=1.5, zorder=7)
        ax.text(p[0]+0.35*scale, p[1], f'+{int(h)}', color=C_LABEL, fontsize=10, fontweight='bold', va='center', zorder=7)

    for i, m in enumerate(g["mailles"]):
        xm = (px[i]+px[i+1])/2
        p  = pt(xm,-0.8,0)
        ax.text(p[0], p[1], f'{i+1}', color=C_DIM, fontsize=9, ha='center', fontweight='bold', zorder=7)
        p2 = pt(xm,-1.3,0)
        ax.text(p2[0], p2[1], f'({m}m)', color=C_DIM, fontsize=8, ha='center', zorder=7)

    ax.set_title(
        f'VUE ISOMETRIQUE — Altrad Plettac Metrix\n'
        f'{g["nb_t"]} travees ({" ; ".join([str(m)+"m" for m in g["mailles"]])}) | '
        f'{g["nb_n"]} niveaux x {g["esp"]}m | L={g["total_l"]}m x H={g["total_h"]}m',
        color='white', fontsize=11, pad=15)
    ax.autoscale_view(); ax.set_aspect('equal')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print(f"    Vue isometrique : {output_path}")
    return output_path


def draw_top_view(params, output_path):
    g = get_geometry(params)
    px = g["positions_x"]
    larg, cf, cg = g["largeur"], g["c_facade"], g["c_gauche"]
    fig_w = max(14, (g["total_l"]+5)*0.8)
    fig, ax = plt.subplots(figsize=(fig_w, 5), facecolor=C_BG)
    ax.set_facecolor(C_BG); ax.axis('off')
    y_wall, y_front, y_console = larg, 0.0, -cf
    wall_rect = mpatches.FancyBboxPatch((px[0]-0.3,y_wall), g["total_l"]+0.6, 0.4,
        boxstyle="square,pad=0", facecolor='#8B5A2B', edgecolor='#6B4020', linewidth=2)
    ax.add_patch(wall_rect)
    body = mpatches.FancyBboxPatch((px[0],y_front), g["total_l"], larg,
        boxstyle="square,pad=0", facecolor='#252840', edgecolor=C_TUBE, linewidth=1.5)
    ax.add_patch(body)
    if cf > 0:
        ax.add_patch(mpatches.FancyBboxPatch((px[0],y_console), g["total_l"], cf,
            boxstyle="square,pad=0", facecolor='#1A1E35', edgecolor='#C0C8D0', linewidth=1.5, linestyle='--'))
    if cg > 0:
        ax.add_patch(mpatches.FancyBboxPatch((px[-1],y_front), cg, larg,
            boxstyle="square,pad=0", facecolor='#1A1E35', edgecolor='#C0C8D0', linewidth=1.5, linestyle='--'))
    for x in px:
        for y in [y_front,y_wall]:
            ax.plot(x, y, 's', color=C_TUBE, markersize=8, zorder=5)
        ax.plot([x,x], [y_front,y_wall], color=C_TUBE, linewidth=1.5, zorder=4)
    for i in range(g["nb_t"]):
        ax.add_patch(mpatches.FancyBboxPatch((px[i]+0.05,y_front+0.05), px[i+1]-px[i]-0.10, larg-0.10,
            boxstyle="round,pad=0.02", facecolor=C_PLANK, edgecolor='#AA2A08', linewidth=0.5, alpha=0.7, zorder=3))
    ax.text(px[0]-0.5, y_front, 'B', color=C_LABEL, fontsize=12, fontweight='bold', va='center', ha='right')
    ax.text(px[0]-0.5, y_wall,  'A', color=C_LABEL, fontsize=12, fontweight='bold', va='center', ha='right')
    ax.annotate('', xy=(px[-1]+0.8,y_wall), xytext=(px[-1]+0.8,y_front),
                arrowprops=dict(arrowstyle='<->', color=C_DIM, lw=1.5))
    ax.text(px[-1]+1.1, larg/2, f'{larg}m', color=C_DIM, fontsize=9, va='center', fontweight='bold')
    for i, m in enumerate(g["mailles"]):
        xm = (px[i]+px[i+1])/2
        ax.text(xm, y_front-0.3, f'{i+1}', color=C_DIM, fontsize=8, ha='center', fontweight='bold')
    ax.annotate('', xy=(px[-1],y_front-0.7), xytext=(px[0],y_front-0.7),
                arrowprops=dict(arrowstyle='<->', color=C_DIM, lw=1.5))
    ax.text(g["total_l"]/2, y_front-1.1, f'Total: {g["total_l"]} m', color=C_DIM, fontsize=10, ha='center', fontweight='bold')
    ax.set_xlim(px[0]-2.0, px[-1]+3.5)
    ax.set_ylim(y_console-1.5, y_wall+1.0)
    ax.set_aspect('equal')
    mailles_str = " ; ".join([f"{m}m" for m in g["mailles"]])
    ax.set_title(f'VUE DE DESSUS (PLAN) — L={g["total_l"]}m | Largeur={larg}m | Console facade={cf}m\n{g["nb_t"]} travees : {mailles_str}',
        color='white', fontsize=11, pad=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print(f"    Vue dessus : {output_path}")
    return output_path


def draw_side_view_detailed(params, output_path):
    g  = get_geometry(params)
    ny = g["niveaux_y"]
    larg, cf, cg = g["largeur"], g["c_facade"], g["c_gauche"]
    fig, ax = plt.subplots(figsize=(7, 14), facecolor=C_BG)
    ax.set_facecolor(C_BG); ax.axis('off')
    ax.add_patch(mpatches.FancyBboxPatch((-0.5,0), 0.35, g["total_h"]+1.0,
        boxstyle="square,pad=0", facecolor='#8B5A2B', edgecolor='#6B4020', linewidth=1.5))
    for z in [0.0, larg]:
        ax.plot([z,z], [0,g["total_h"]], color=C_TUBE, linewidth=3, solid_capstyle='round', zorder=4)
    if cf > 0:
        ax.plot([-cf,0], [0,0], color='#C0C8D0', linewidth=2, linestyle='--', zorder=3)
        for h in ny:
            ax.plot([-cf,0], [h,h], color='#C0C8D0', linewidth=1, linestyle=':', zorder=2)
    if cg > 0:
        ax.plot([larg,larg+cg], [0,0], color='#C0C8D0', linewidth=2, linestyle='--', zorder=3)
    for n, h in enumerate(ny):
        ax.plot([0,larg], [h,h], color=C_TUBE, linewidth=2, zorder=4)
        if n < g["nb_n"]:
            h_next = ny[n+1]; ph = h+(h_next-h)*0.78
            ax.add_patch(mpatches.FancyBboxPatch((0.03,ph-0.09), larg-0.06, 0.18,
                boxstyle="round,pad=0.01", facecolor=C_PLANK, edgecolor='#AA2A08', linewidth=0.8, zorder=5))
            ax.plot([0,larg], [h,h_next], color=C_TUBE, linewidth=1.5, alpha=0.8, zorder=4)
            ax.plot([larg,0], [h,h_next], color=C_TUBE, linewidth=1.5, alpha=0.8, zorder=4)
    ax.plot([0,larg], [g["total_h"]+0.5]*2, color='#B0C8D8', linewidth=2.5, linestyle='--', zorder=4)
    for z in [0.0, larg]:
        ax.plot(z, 0, 'o', color=C_VERIN, markersize=10, zorder=6)
        ax.plot([z,z], [-0.35,0], color=C_VERIN, linewidth=4, zorder=6)
    xe = larg+0.25
    for n in range(g["nb_n"]):
        y1, y2 = ny[n], ny[n+1]
        ax.plot([xe-0.10,xe-0.10], [y1,y2], color='#A0A8B0', linewidth=2, zorder=6)
        ax.plot([xe+0.10,xe+0.10], [y1,y2], color='#A0A8B0', linewidth=2, zorder=6)
        for s in range(6):
            ys = y1+(y2-y1)*s/5
            ax.plot([xe-0.14,xe+0.14], [ys,ys], color='#B0B8C0', linewidth=1.5, zorder=6)
        ax.add_patch(mpatches.FancyBboxPatch((xe-0.2,y2-0.12), 0.4, 0.12,
            boxstyle="round,pad=0.01", facecolor=C_PLANK, edgecolor='#AA2A08', linewidth=0.5, zorder=6))
    for h in ny:
        ax.plot([larg,larg+0.3], [h,h], color=C_LABEL, linewidth=1.5, zorder=7)
        ax.text(larg+0.4, h, f'+{int(h)}', color=C_LABEL, fontsize=11, fontweight='bold', va='center', zorder=7)
    ax.annotate('', xy=(larg+1.6,g["total_h"]), xytext=(larg+1.6,0),
                arrowprops=dict(arrowstyle='<->', color=C_DIM, lw=2))
    ax.text(larg+2.0, g["total_h"]/2, f'{g["total_h"]}m', color=C_DIM, fontsize=11, fontweight='bold', va='center', rotation=90)
    y_dim = -0.8
    if cf > 0:
        ax.annotate('', xy=(0,y_dim), xytext=(-cf,y_dim), arrowprops=dict(arrowstyle='<->', color=C_DIM, lw=1.5))
        ax.text(-cf/2, y_dim-0.35, f'A={cf}m', color=C_DIM, fontsize=9, ha='center')
    ax.annotate('', xy=(larg,y_dim), xytext=(0,y_dim), arrowprops=dict(arrowstyle='<->', color=C_DIM, lw=1.5))
    ax.text(larg/2, y_dim-0.35, f'B={larg}m', color=C_DIM, fontsize=9, ha='center')
    if cg > 0:
        ax.annotate('', xy=(larg+cg,y_dim), xytext=(larg,y_dim), arrowprops=dict(arrowstyle='<->', color=C_DIM, lw=1.5))
        ax.text(larg+cg/2, y_dim-0.35, f'{cg}m', color=C_DIM, fontsize=9, ha='center')
    ax.text(-cf-0.2 if cf > 0 else -0.3, -1.4, 'A', color=C_LABEL, fontsize=12, fontweight='bold', ha='center')
    ax.text(larg+0.2, -1.4, 'B', color=C_LABEL, fontsize=12, fontweight='bold', ha='center')
    margin = max(cf,0.3)+0.5
    ax.set_xlim(-margin-0.8, larg+2.8)
    ax.set_ylim(-2.2, g["total_h"]+1.5)
    ax.set_aspect('equal')
    ax.set_title(f'VUE DE COTE — H={g["total_h"]}m | {g["nb_n"]} niveaux x {g["esp"]}m\nLargeur B={larg}m | Console facade A={cf}m | Console gauche={cg}m',
        color='white', fontsize=11, pad=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print(f"    Vue cote : {output_path}")
    return output_path


def draw_face_view(params, output_path):
    g   = get_geometry(params)
    px, ny = g["positions_x"], g["niveaux_y"]
    fig, ax = plt.subplots(figsize=(18, 10), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    for x in px:
        ax.plot([x,x], [0,g["total_h"]], color=C_TUBE, linewidth=3, solid_capstyle='round')
    for n, h in enumerate(ny):
        ax.plot([px[0],px[-1]], [h,h], color=C_TUBE, linewidth=2)
        if n < g["nb_n"]:
            h_next = ny[n+1]; ph = h+(h_next-h)*0.80
            for i in range(g["nb_t"]):
                ax.add_patch(mpatches.FancyBboxPatch((px[i]+0.03,ph-0.08), px[i+1]-px[i]-0.06, 0.16,
                    boxstyle="round,pad=0.01", facecolor=C_PLANK, edgecolor='#AA2A08', linewidth=0.8))
            for i in range(0, g["nb_t"], 2):
                x2 = px[min(i+1,g["nb_t"])]
                ax.plot([px[i],x2], [h,h_next], color=C_TUBE, linewidth=1.5, alpha=0.8)
                ax.plot([x2,px[i]], [h,h_next], color=C_TUBE, linewidth=1.5, alpha=0.8)
    ax.plot([px[0],px[-1]], [g["total_h"]+0.5]*2, color='#B0C0D0', linewidth=2.5, linestyle='--')
    ax.text(px[-1]+0.2, g["total_h"]+0.5, 'Garde-corps permanent', color='#B0C0D0', fontsize=9, va='center')
    if g["c_facade"] > 0:
        ax.plot([px[0],px[-1]], [-g["c_facade"]]*2, color='#C0C8D0', linewidth=2, linestyle=':')
        ax.text(px[-1]+0.2, -g["c_facade"], f'Console {g["c_facade"]}m', color='#C0C8D0', fontsize=9, va='center')
    for x in px:
        ax.plot(x, 0, 'o', color=C_VERIN, markersize=10, zorder=5)
        ax.plot([x,x], [-0.3,0], color=C_VERIN, linewidth=4)
    xe = px[0]-0.25
    for n in range(g["nb_n"]):
        y1, y2 = ny[n], ny[n+1]
        ax.plot([xe-0.12,xe-0.12], [y1,y2], color='#A0A8B0', linewidth=2)
        ax.plot([xe+0.12,xe+0.12], [y1,y2], color='#A0A8B0', linewidth=2)
        for s in range(4):
            ys = y1+(y2-y1)*s/3
            ax.plot([xe-0.15,xe+0.15], [ys,ys], color='#B0B8C0', linewidth=1.5)
    for h in ny:
        ax.plot([px[-1],px[-1]+0.4], [h,h], color=C_LABEL, linewidth=1.5)
        ax.text(px[-1]+0.5, h, f'+{int(h)}m', color=C_LABEL, fontsize=12, fontweight='bold', va='center')
    for i, m in enumerate(g["mailles"]):
        xm = (px[i]+px[i+1])/2
        ax.text(xm, -0.6, f'T{i+1}', color=C_DIM, fontsize=10, ha='center', fontweight='bold')
        ax.text(xm, -1.0, f'({m}m)', color=C_DIM, fontsize=9, ha='center')
    ax.annotate('', xy=(px[-1],-1.8), xytext=(px[0],-1.8), arrowprops=dict(arrowstyle='<->', color=C_DIM, lw=2))
    ax.text(g["total_l"]/2, -2.3, f'Longueur totale : {g["total_l"]} m', color=C_DIM, fontsize=12, fontweight='bold', ha='center')
    mailles_str = " ; ".join([f"{m}m" for m in g["mailles"]])
    ax.set_xlim(px[0]-1.5, px[-1]+2.5)
    ax.set_ylim(-3.0, g["total_h"]+1.5)
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(f'VUE DE FACE — {g["total_l"]}m x {g["total_h"]}m | {g["nb_t"]} travees ({mailles_str}) | {g["nb_n"]} niveaux x {g["esp"]}m',
        color='white', fontsize=12, pad=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=C_BG)
    plt.close()
    print(f"    Vue face : {output_path}")
    return output_path


# ─────────────────────────────────────────────
# COMPOSANTS ALTRAD
# ─────────────────────────────────────────────

def _build_altrad_components(params):
    g = get_geometry(params)
    materiel_raw = params["materiel"]
    if "70" in materiel_raw:
        materiel_code="Metrix 70"; planche_code="KMC5 (Plancher acier 30x300)"
        lisse_code="KLC6 (Lisse standard 300)"; poteau_code="KPT4 (Poteau standard 200)"
        materiel_desc="Metrix 70 system — plateau width 70cm"
    else:
        materiel_code="Metrix 100"; planche_code="KMC5 (Plancher acier 30x300)"
        lisse_code="KLC6 (Lisse standard 300)"; poteau_code="KPT4 (Poteau standard 200)"
        materiel_desc="Metrix 100 system — plateau width 100cm"

    if "permanent" in params["garde_corps"].lower():
        gc_code="KGH6 (Garde-corps permanent de securite 3m)"
        gc_desc="KGH6 permanent safety guardrail — MDS system"
    else:
        gc_code="KGH4 (Garde-corps standard 2m)"; gc_desc="KGH4 standard guardrail"

    verin_code  = "ASV5 (Socle verin galva 59 — 4cm)" if "ASV5" in params["verins"] else "ASV8 (Socle verin galva — 8cm)"
    calage_code = "AMX1 (Cale madrier 8x23 L50 — 8cm)" if "AMX1" in params["calage"] else "Calage personnalise"
    diag_code   = "KDV6 (Diagonale verticale Metrix 200x300)"
    embase_code = "KEMB (Embase de depart Metrix)"
    plinthe_code= "KPI6 (Plinthe bois de 300) + KPI4 (Plinthe bois de 200)"

    def console_info(cons_str):
        if "70" in cons_str: return "KKR1 (Console Metrix renforcee 2 plateaux — 70cm)"
        elif "40" in cons_str: return "KKR8 (Console Metrix renforcee 1 plateau — 40cm)"
        return None

    cons_f = console_info(params["console_facade"])
    cons_g = console_info(params["console_gauche"])
    cons_d = console_info(params["console_droit"])
    cons_r = console_info(params["console_rue"])

    classe_raw = params["classe"]
    charge_map = {"2":"150","3":"200","4":"300","5":"450"}
    classe_num = "3"; charge_str = "200 daN/m2"
    for k,v in charge_map.items():
        if f"Classe {k}" in classe_raw:
            classe_num=k; charge_str=f"{v} daN/m2"; break

    mailles_str = " ; ".join([f"T{i+1}={m}m" for i,m in enumerate(g["mailles"])])
    niveaux_str = " / ".join([f"+{int(h)}m" for h in g["niveaux_y"]])

    consoles_lines = []
    if cons_f: consoles_lines.append(f"- Console facade: {cons_f}")
    if cons_g: consoles_lines.append(f"- Console left:   {cons_g}")
    if cons_d: consoles_lines.append(f"- Console right:  {cons_d}")
    if cons_r: consoles_lines.append(f"- Console street: {cons_r}")
    consoles_str = "\n".join(consoles_lines) if consoles_lines else "- No consoles"

    return {
        "g":g, "materiel_code":materiel_code, "materiel_desc":materiel_desc,
        "planche_code":planche_code, "lisse_code":lisse_code, "poteau_code":poteau_code,
        "gc_code":gc_code, "gc_desc":gc_desc, "verin_code":verin_code,
        "calage_code":calage_code, "diag_code":diag_code, "embase_code":embase_code,
        "plinthe_code":plinthe_code, "cons_f":cons_f, "cons_g":cons_g,
        "cons_d":cons_d, "cons_r":cons_r, "classe_num":classe_num,
        "charge_str":charge_str, "mailles_str":mailles_str, "niveaux_str":niveaux_str,
        "consoles_str":consoles_str,
    }


# ─────────────────────────────────────────────
# PROMPTS GEMINI — ANGLES PRÉCIS
# ─────────────────────────────────────────────

def prompt_render_3d(params, prev_image=False):
    """Vue isométrique — vraie 3D avec angle caméra précis."""
    c = _build_altrad_components(params)
    g = c["g"]
    style_instruction = ""
    if prev_image:
        style_instruction = """STYLE REFERENCE — CRITICAL:
- The FIRST image is your PREVIOUS render — keep EXACTLY this visual style
- Same lighting, same materials, same color palette, same render quality
- ONLY update the dimensions/geometry to match the new blueprint (second image)
- Do NOT change: background color, tube material, plank color, shadows, render style

"""
    return f"""{style_instruction}The {"last" if prev_image else "reference"} image is an exact Matplotlib blueprint of an Altrad Plettac Metrix scaffolding.
Convert it to a photorealistic TRUE ISOMETRIC 3D view. ALL components must be authentic Altrad products.

CAMERA ANGLE — CRITICAL — NOT A FRONT VIEW:
- TRUE ISOMETRIC: camera at EXACTLY 45 degrees horizontal + 30 degrees vertical
- You MUST simultaneously see THREE faces:
  1. FRONT face (showing {g["nb_t"]} bays and level labels on right)
  2. RIGHT SIDE face (showing depth of {g["largeur"]}m — this MUST be visible)
  3. TOP surface (showing floor planks from above)
- The scaffolding appears as a 3D box — NOT a flat rectangle
- Like Altrad Plettac Vision software CAD screenshot

EXACT DIMENSIONS — DO NOT CHANGE:
- EXACTLY {g["nb_t"]} bays: {c["mailles_str"]}
- EXACTLY {g["nb_n"]} levels at {g["esp"]}m spacing
- Total: {g["total_l"]}m wide x {g["total_h"]}m tall x {g["largeur"]}m deep
- Brown/ochre wall visible BEHIND scaffolding at depth {g["largeur"]}m

ALTRAD PLETTAC METRIX COMPONENTS:
- {c["poteau_code"]}: bright silver galvanized tubes on FRONT and RIGHT SIDE faces
- {c["lisse_code"]}: silver horizontal tubes at each level on front + side + back
- {c["planche_code"]}: VIVID RED/ORANGE exactly #DC3C14 — NOT brown — with wood grain
- {c["diag_code"]}: X braces on RIGHT SIDE panels ONLY — NOT on front face
- {c["gc_code"]}: {c["gc_desc"]} — horizontal tubes at top of every level
- {c["plinthe_code"]}: thin planks at every platform edge
- {c["verin_code"]}: screw jack bases at EVERY post base — clearly visible
- {c["calage_code"]}: timber wedges under screw jacks
- {c["embase_code"]}: base plates at ground level
{c["consoles_str"]}

LEVEL LABELS right side (bottom to top): {c["niveaux_str"]}
BAY LABELS at bottom: {c["mailles_str"]}

RENDER: Dark navy #1A1A2E | silver metallic tubes | VIVID RED-ORANGE planks #DC3C14
Access ladder (KPE6) on LEFT side | Safety class {c["classe_num"]} — {c["charge_str"]}
Professional Altrad Plettac Vision CAD quality"""


def prompt_view_top(params, prev_image=False):
    """Vue de dessus — caméra strictement perpendiculaire au sol."""
    c = _build_altrad_components(params)
    g = c["g"]
    style_instruction = ""
    if prev_image:
        style_instruction = """STYLE REFERENCE — CRITICAL:
- The FIRST image is your PREVIOUS render — keep EXACTLY this visual style
- Same lighting, same materials, same color palette, same render quality
- ONLY update the dimensions/geometry to match the new blueprint (second image)
- Do NOT change: background color, tube material, plank color, shadows, render style

"""
    return f"""{style_instruction}The {"last" if prev_image else "reference"} image is an exact Matplotlib top/plan view of an Altrad Plettac Metrix scaffolding.
Render it as a photorealistic STRICT TOP-DOWN PLAN VIEW.

CAMERA ANGLE — CRITICAL:
- Camera pointing STRAIGHT DOWN at 90 degrees — directly overhead
- PURE ORTHOGRAPHIC top-down projection — NO perspective distortion
- Like an architectural floor plan seen from above
- Brown wall appears as a HORIZONTAL BAND at the TOP of image
- Scaffolding body appears as a FLAT RECTANGLE below the wall
- You see ONLY the horizontal plane — no height/depth visible
- Bay dividers are VERTICAL LINES across the rectangle

EXACT DIMENSIONS:
- EXACTLY {g["nb_t"]} bays side by side: {c["mailles_str"]}
- Scaffolding depth front-to-back: {g["largeur"]}m
- Total width: {g["total_l"]}m
- Label A (wall side) on left | Label B (street side) on left
- Total {g["total_l"]}m dimension arrow at bottom
{c["consoles_str"]}

WHAT IS VISIBLE FROM ABOVE:
- {c["planche_code"]}: VIVID RED/ORANGE #DC3C14 rectangles filling each bay
- {c["lisse_code"]}: silver tube grid lines between bays
- {c["poteau_code"]}: small silver squares at bay corners
- Brown wall band at top edge of image

RENDER: Dark background #1A1A2E | RED/ORANGE planks | silver grid | professional Altrad plan view"""


def prompt_view_cote(params, prev_image=False):
    """Vue de côté — caméra strictement horizontale depuis la gauche."""
    c = _build_altrad_components(params)
    g = c["g"]
    style_instruction = ""
    if prev_image:
        style_instruction = """STYLE REFERENCE — CRITICAL:
- The FIRST image is your PREVIOUS render — keep EXACTLY this visual style
- Same lighting, same materials, same color palette, same render quality
- ONLY update the dimensions/geometry to match the new blueprint (second image)
- Do NOT change: background color, tube material, plank color, shadows, render style

"""
    return f"""{style_instruction}The {"last" if prev_image else "reference"} image is an exact Matplotlib side view of an Altrad Plettac Metrix scaffolding.
Render it as a photorealistic STRICT LEFT SIDE ELEVATION.

CAMERA ANGLE — CRITICAL:
- Camera pointing HORIZONTALLY from the LEFT end — 0 degrees elevation
- You see the scaffolding from EXACTLY the left end
- You see ONLY the depth dimension: {g["largeur"]}m wide
- The {g["nb_t"]} bays are NOT visible — you see only 1 bay deep
- Brown wall appears as a VERTICAL BAND on the LEFT side
- Access ladder (KPE6) appears on the RIGHT side
- This is a 2D elevation view — NOT isometric — NOT perspective

WHAT IS VISIBLE FROM THE LEFT SIDE:
- {g["nb_n"]} horizontal floor levels stacked at {g["esp"]}m spacing
- {c["planche_code"]}: VIVID RED/ORANGE horizontal bands at each level — {g["largeur"]}m wide
- {c["diag_code"]}: large X diagonal braces between levels
- {c["poteau_code"]}: 2 vertical silver tubes ({g["largeur"]}m apart)
- {c["verin_code"]}: screw jack bases at bottom of both posts
- {c["calage_code"]}: wedges under jacks
- {c["gc_code"]}: horizontal guardrail at top of every level
- Brown wall: vertical band touching the back post on LEFT
- KPE6 access ladder on RIGHT with rungs at each level

EXACT DIMENSIONS:
- Total height: {g["total_h"]}m | {g["nb_n"]} levels x {g["esp"]}m
- Depth shown: {g["largeur"]}m (B dimension)
- Console facade: {g["c_facade"]}m (A dimension) extends LEFT if present
{c["consoles_str"]}

LEVEL LABELS on right side: {c["niveaux_str"]}
DIMENSIONS: total height {g["total_h"]}m arrow right | A={g["c_facade"]}m | B={g["largeur"]}m at bottom

RENDER: Dark background #1A1A2E | silver tubes | VIVID RED-ORANGE planks #DC3C14
Strict left side elevation — like engineering drawing | professional Altrad quality"""


def prompt_apply_building(description, params, prev_image=False):
    """Application sur bâtiment — couverture 100%."""
    c = _build_altrad_components(params)
    g = c["g"]
    style_instruction = ""
    if prev_image:
        style_instruction = """STYLE REFERENCE — CRITICAL:
- The FIRST image is your PREVIOUS render — keep EXACTLY this visual style
- Same lighting, same render quality, same scaffolding style
- ONLY update the scaffolding dimensions to match the new blueprint
- Do NOT change the building appearance

"""
    return f"""{style_instruction}This is a {description}.
The reference image is an exact Matplotlib front elevation blueprint.
Apply this Altrad Plettac Metrix scaffolding IN FRONT of the building facade.

CAMERA AND VIEW:
- STRAIGHT FRONT VIEW — camera perpendicular to facade
- Scaffolding placed exactly in front of building
- Starts at LEFT edge of building — ends at RIGHT edge
- Starts at GROUND LEVEL — reaches FULL building height

ALTRAD PLETTAC METRIX COMPONENTS:
- System: {c["materiel_code"]} — {c["materiel_desc"]}
- {c["poteau_code"]}: bright silver galvanized tubes at each bay
- {c["planche_code"]}: VIVID RED/ORANGE #DC3C14 at EVERY level — highly saturated
- {c["lisse_code"]}: silver horizontal tubes at each level
- {c["diag_code"]}: silver X pattern every 2 bays
- {c["gc_code"]}: {c["gc_desc"]} — horizontal guardrail above every platform
- {c["plinthe_code"]}: at every platform edge
- {c["verin_code"]}: visible screw jacks at ground level
- Green safety nets (filets verts de protection) between planks
{c["consoles_str"]}

EXACT COVERAGE — MANDATORY:
- {g["nb_t"]} bays: {c["mailles_str"]}
- {g["nb_n"]} levels at {g["esp"]}m — Total: {g["total_l"]}m x {g["total_h"]}m
- 100% of facade covered — NO gap on left, right, top or bottom

BUILDING PRESERVATION — MANDATORY:
- Building colors, architecture, windows COMPLETELY UNCHANGED
- Same lighting as original photo — all existing objects preserved
- Photorealistic quality — real construction site photo style

NEGATIVE: No building change. No background change. No partial scaffolding. Full 100% mandatory."""


# ─────────────────────────────────────────────
# GEMINI — ANALYSE BÂTIMENT
# ─────────────────────────────────────────────

def analyze_building(image_path):
    if not GEMINI_API_KEY:
        return "a multi-story classical European building"
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_TEXT)
    img   = Image.open(image_path)
    print("\n  Analyse du batiment...")
    response = model.generate_content([
        "Describe this building in one short sentence in English. Reply with description only.", img])
    desc = response.text.strip()
    print(f"  -> {desc}")
    return desc


def _load_parts(paths):
    parts = []
    for p in paths:
        with open(p, "rb") as f: data = f.read()
        mime, _ = mimetypes.guess_type(p)
        parts.append(types.Part(inline_data=types.Blob(data=data, mime_type=mime or "image/jpeg")))
    return parts


def gemini_render(prompt, output_path, ref_images):
    client = genai_client.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1beta"})
    contents = _load_parts(ref_images)
    contents.append(types.Part.from_text(text=prompt))
    response = client.models.generate_content(
        model=GEMINI_MODEL, contents=contents,
        config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"]))
    saved = False
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            with open(output_path, "wb") as f: f.write(part.inline_data.data)
            saved = True
        elif part.text:
            print(f"    Info: {part.text[:80]}")
    if not saved:
        raise RuntimeError(f"Pas d'image pour {output_path}")
    print(f"    Sauvegardee: {output_path}")
    return output_path


# ─────────────────────────────────────────────
# PIPELINE COMPLET
# ─────────────────────────────────────────────

def generate_all_views(building_path, description, params, output_dir, prev_images=None):
    """
    Génère toutes les vues Matplotlib + Gemini.
    prev_images : dict optionnel avec les chemins des images Gemini précédentes.
                  Si fourni, Gemini reçoit [ancienne image] + [nouveau blueprint]
                  pour conserver exactement le même style visuel.
    """
    os.makedirs(output_dir, exist_ok=True)
    paths = {}
    has_prev = prev_images and isinstance(prev_images, dict)

    print("\n" + "="*55)
    print("  ETAPE 1 : GENERATION MATPLOTLIB (dimensions exactes)")
    print("="*55)

    print("\n  [1/4] Vue isometrique Matplotlib...")
    paths["mpl_iso"]  = draw_isometric_view(params, os.path.join(output_dir, "mpl_iso.png"))

    print("\n  [2/4] Vue de face Matplotlib...")
    paths["mpl_face"] = draw_face_view(params, os.path.join(output_dir, "mpl_face.png"))

    print("\n  [3/4] Vue de dessus Matplotlib...")
    paths["mpl_top"]  = draw_top_view(params, os.path.join(output_dir, "mpl_top.png"))

    print("\n  [4/4] Vue de cote Matplotlib...")
    paths["mpl_cote"] = draw_side_view_detailed(params, os.path.join(output_dir, "mpl_cote.png"))

    print("\n" + "="*55)
    print("  ETAPE 2 : RENDU GEMINI (depuis blueprints Matplotlib)")
    if has_prev:
        print("  MODE MODIFICATION : style de l'ancienne image conserve")
    print("="*55)

    # Vue isométrique
    print("\n  [1/4] Vue isometrique realiste ...")
    if has_prev and prev_images.get("gemini_iso") and os.path.exists(prev_images["gemini_iso"]):
        # Modification : [ancienne image Gemini] + [nouveau blueprint Matplotlib]
        ref_iso = [prev_images["gemini_iso"], paths["mpl_iso"]]
        use_prev_iso = True
        print("    -> Mode modification : ancienne image + nouveau blueprint")
    else:
        ref_iso = [paths["mpl_iso"]]
        use_prev_iso = False
    paths["gemini_iso"] = gemini_render(
        prompt_render_3d(params, prev_image=use_prev_iso),
        os.path.join(output_dir, "gemini_iso.png"),
        ref_images=ref_iso)
    time.sleep(3)

    # Vue de dessus
    print("\n  [2/4] Vue de dessus realiste (Matplotlib → Gemini)...")
    if has_prev and prev_images.get("gemini_top") and os.path.exists(prev_images["gemini_top"]):
        ref_top = [prev_images["gemini_top"], paths["mpl_top"]]
        use_prev_top = True
        print("    -> Mode modification : ancienne image + nouveau blueprint")
    else:
        ref_top = [paths["mpl_top"]]
        use_prev_top = False
    paths["gemini_top"] = gemini_render(
        prompt_view_top(params, prev_image=use_prev_top),
        os.path.join(output_dir, "gemini_top.png"),
        ref_images=ref_top)
    time.sleep(3)

    # Vue de côté
    print("\n  [3/4] Vue de cote realiste (Matplotlib → Gemini)...")
    if has_prev and prev_images.get("gemini_cote") and os.path.exists(prev_images["gemini_cote"]):
        ref_cote = [prev_images["gemini_cote"], paths["mpl_cote"]]
        use_prev_cote = True
        print("    -> Mode modification : ancienne image + nouveau blueprint")
    else:
        ref_cote = [paths["mpl_cote"]]
        use_prev_cote = False
    paths["gemini_cote"] = gemini_render(
        prompt_view_cote(params, prev_image=use_prev_cote),
        os.path.join(output_dir, "gemini_cote.png"),
        ref_images=ref_cote)
    time.sleep(3)

    # Application sur bâtiment
    print("\n  [4/4] Application sur batiment (Matplotlib + batiment → Gemini)...")
    if has_prev and prev_images.get("batiment") and os.path.exists(prev_images["batiment"]):
        ref_bat = [prev_images["batiment"], building_path, paths["mpl_face"]]
        use_prev_bat = True
        print("    -> Mode modification : ancienne image + batiment + nouveau blueprint")
    else:
        ref_bat = [building_path, paths["mpl_face"]]
        use_prev_bat = False
    paths["batiment"] = gemini_render(
        prompt_apply_building(description, params, prev_image=use_prev_bat),
        os.path.join(output_dir, "batiment_echafaudage.png"),
        ref_images=ref_bat)

    paths["face"] = paths["mpl_face"]
    return paths


def generate_pdf(project_info, params, materials, image_paths, original_image, output_pdf):
    doc = SimpleDocTemplate(output_pdf, pagesize=A4,
                            rightMargin=1.5*cm, leftMargin=1.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story  = []
    ORANGE = colors.HexColor("#E8401C")
    DARK   = colors.HexColor("#1A1A2E")
    GREY   = colors.HexColor("#F5F5F5")
    LGREY  = colors.HexColor("#EEEEEE")

    title_s = ParagraphStyle("T", parent=styles["Title"], fontSize=20, textColor=DARK,
                              spaceAfter=4, alignment=TA_CENTER, fontName="Helvetica-Bold")
    sub_s   = ParagraphStyle("S", parent=styles["Normal"], fontSize=10,
                              textColor=colors.HexColor("#666666"), spaceAfter=16, alignment=TA_CENTER)
    sec_s   = ParagraphStyle("Se", parent=styles["Heading1"], fontSize=12,
                              textColor=colors.white, backColor=ORANGE,
                              spaceBefore=12, spaceAfter=6, leftIndent=6, fontName="Helvetica-Bold")
    norm_s  = ParagraphStyle("N", parent=styles["Normal"], fontSize=9, spaceAfter=3)
    label_s = ParagraphStyle("L", parent=styles["Normal"], fontSize=7,
                              alignment=TA_CENTER, textColor=colors.HexColor("#666666"))
    foot_s  = ParagraphStyle("F", parent=styles["Normal"], fontSize=7,
                              textColor=colors.HexColor("#999999"), alignment=TA_CENTER)

    mailles = params["mailles_list"]
    nb_t    = len(mailles)
    esp     = float(params["espacement_niveaux"].split()[0])
    nb_n    = math.ceil(params["hauteur"] / esp)
    mailles_str = " ; ".join([f"{m}m" for m in mailles])
    niveaux_str = " ; ".join([f"{round(i*esp)}m" for i in range(nb_n+1) if round(i*esp) <= round(nb_n*esp)])

    # PAGE 1
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("RAPPORT D'ECHAFAUDAGE", title_s))
    story.append(Paragraph("Configurateur style Altrad Plettac Vision", sub_s))
    story.append(HRFlowable(width="100%", thickness=3, color=ORANGE, spaceAfter=10))
    hdata = [
        [Paragraph(f"<b>Nom du projet :</b> {project_info['nom_projet']}", norm_s),
         Paragraph(f"<b>N : {datetime.now().strftime('%y-%m%d')}</b>", norm_s)],
        [Paragraph(f"<b>Cree le :</b> {datetime.now().strftime('%d/%m/%Y')}", norm_s), ""],
    ]
    htable = Table(hdata, colWidths=[13*cm, 4*cm])
    htable.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#CCCCCC")),
                                ("PADDING",(0,0),(-1,-1),6),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story.append(htable); story.append(Spacer(1, 0.3*cm))
    adata = [[
        Paragraph(f"<b>Adresse :</b><br/>{project_info['adresse']}", norm_s),
        Paragraph(f"<b>Entreprise utilisatrice :</b><br/>{project_info['entreprise']}", norm_s),
        Paragraph(f"<b>Entreprise montage :</b><br/>{project_info['montage']}", norm_s),
    ]]
    atable = Table(adata, colWidths=[5.5*cm, 5.5*cm, 6*cm])
    atable.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#CCCCCC")),
                                ("PADDING",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"TOP"),
                                ("MINROWHEIGHT",(0,0),(-1,-1),1.5*cm)]))
    story.append(atable); story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("PARAMETRES DE CONFIGURATION", sec_s))
    story.append(Spacer(1, 0.2*cm))
    pdata = [["Parametre", "Valeur"],
             ["Type de materiel",          params["materiel"][:35]],
             ["Type de garde-corps",       params["garde_corps"][:45]],
             ["Longueur de l'echafaudage", f"{params['longueur']} m"],
             ["Nombre de travees",         f"{nb_t} travees"],
             ["Longueurs des mailles",     mailles_str],
             ["Hauteur de la facade",      f"{params['hauteur']} m"],
             ["Espacement des niveaux",    params["espacement_niveaux"]],
             ["Hauteur des niveaux",       niveaux_str],
             ["Type de verins",            params["verins"][:25]],
             ["Type de calage",            params["calage"][:30]],
             ["Consoles cote facade",      params["console_facade"]],
             ["Consoles cote rue",         params["console_rue"]],
             ["Consoles cote gauche",      params["console_gauche"]],
             ["Consoles cote droit",       params["console_droit"]],
             ["Classe",                    params["classe"][:35]]]
    ptable = Table(pdata, colWidths=[7*cm, 10*cm])
    ptable.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),ORANGE),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),
        ("BACKGROUND",(0,1),(0,-1),LGREY),("FONTNAME",(0,1),(0,-1),"Helvetica-Bold"),
        ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,GREY]),
        ("PADDING",(0,0),(-1,-1),5),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    story.append(ptable)

    # PAGE 2
    story.append(PageBreak())
    story.append(Paragraph("VUE DE FACADE — APPLICATION SUR BATIMENT", sec_s))
    story.append(Spacer(1, 0.3*cm))
    W, H = 8.5*cm, 6.5*cm
    img1 = Table(
        [[RLImage(original_image, W, H), RLImage(image_paths["batiment"], W, H)],
         [Paragraph("Photo originale", label_s), Paragraph("Avec echafaudage Altrad (Gemini)", label_s)]],
        colWidths=[W+0.5*cm, W+0.5*cm])
    img1.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),("PADDING",(0,0),(-1,-1),4)]))
    story.append(img1); story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("ECHAFAUDAGE DE REFERENCE 3D — Rendu Gemini", sec_s))
    story.append(Spacer(1, 0.3*cm))
    story.append(RLImage(image_paths["gemini_iso"], 16*cm, 10*cm))
    story.append(Paragraph("Vue isometrique realiste — Altrad Plettac Metrix (Matplotlib → Gemini)", label_s))

    # PAGE 3
    story.append(PageBreak())
    story.append(Paragraph("VUES TECHNIQUES", sec_s))
    story.append(Spacer(1, 0.3*cm))
    W2, H2 = 8.5*cm, 10*cm
    vtable = Table(
        [[RLImage(image_paths["gemini_iso"],  W2, H2), RLImage(image_paths["gemini_top"],  W2, H2)],
         [Paragraph("Vue isometrique",        label_s), Paragraph("Vue de dessus",          label_s)],
         [RLImage(image_paths["gemini_cote"], W2, H2), Paragraph("", label_s)],
         [Paragraph("Vue de cote",            label_s), Paragraph("", label_s)]],
        colWidths=[W2+0.5*cm, W2+0.5*cm])
    vtable.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),
                                ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("PADDING",(0,0),(-1,-1),4)]))
    story.append(vtable)

    # PAGE 4
    story.append(PageBreak())
    story.append(Paragraph("LISTE DE MATERIEL", sec_s))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"Echafaudage de facade — Longueur : {params['longueur']} m ({nb_t} travees) — "
        f"Hauteur : {params['hauteur']} m ({nb_n} niveaux)", norm_s))
    story.append(Spacer(1, 0.3*cm))
    total_montant = sum(m["montant"] for m in materials)
    mdata = [["Article", "Designation", "Poids (kg)", "Prix (EUR)", "Qte", "Montant (EUR)"]]
    for m in materials:
        mdata.append([m["article"], m["designation"], f"{m['poids']:.2f}",
                      f"{m['prix']:.2f}", str(m["qte"]), f"{m['montant']:.2f}"])
    mdata.append(["", "TOTAL", "", "", "", f"{total_montant:.2f}"])
    mtable = Table(mdata, colWidths=[1.8*cm, 7.5*cm, 2*cm, 2.2*cm, 1.2*cm, 2.3*cm])
    mtable.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),ORANGE),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),7),
        ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS",(0,1),(-1,-2),[colors.white,GREY]),
        ("PADDING",(0,0),(-1,-1),4),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(2,0),(5,-1),"CENTER"),
        ("BACKGROUND",(0,-1),(-1,-1),DARK),("TEXTCOLOR",(0,-1),(-1,-1),colors.white),
        ("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),
    ]))
    story.append(mtable)
    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=ORANGE))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"Document genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')} "
        "— Configurateur d'echafaudage IA Style Altrad Plettac Vision", foot_s))
    story.append(Paragraph(f"Total materiel : {total_montant:.2f} EUR", foot_s))
    doc.build(story)
    print(f"\n  PDF genere : {output_pdf}")
    return output_pdf


# ─────────────────────────────────────────────
# JSON SUPPORT
# ─────────────────────────────────────────────

CONSOLE_MAP = {
    0:"Pas de console", 40:"Console largeur 40 cm", 70:"Console largeur 70 cm",
    "0":"Pas de console","40":"Console largeur 40 cm","70":"Console largeur 70 cm",
    "Pas de console":"Pas de console","Console largeur 40 cm":"Console largeur 40 cm",
    "Console largeur 70 cm":"Console largeur 70 cm",
}
CLASSE_MAP = {
    2:"Classe 2 — 150 daN/m2",3:"Classe 3 — 200 daN/m2",
    4:"Classe 4 — 300 daN/m2",5:"Classe 5 — 450 daN/m2",
    "2":"Classe 2 — 150 daN/m2","3":"Classe 3 — 200 daN/m2",
    "4":"Classe 4 — 300 daN/m2","5":"Classe 5 — 450 daN/m2",
}
MATERIEL_MAP = {
    70:"Metrix 70 — Largeur 70 cm",100:"Metrix 100 — Largeur 100 cm",
    "70":"Metrix 70 — Largeur 70 cm","100":"Metrix 100 — Largeur 100 cm",
    "Metrix 70 — Largeur 70 cm":"Metrix 70 — Largeur 70 cm",
    "Metrix 100 — Largeur 100 cm":"Metrix 100 — Largeur 100 cm",
}
GARDECORPS_MAP = {
    "permanent":"Garde-corps permanent de securite",
    "standard":"Garde-corps standard",
    "Garde-corps permanent de securite":"Garde-corps permanent de securite",
    "Garde-corps standard":"Garde-corps standard",
}
VERINS_MAP = {
    "ASV5":"ASV5 — 4 cm","ASV8":"ASV8 — 8 cm",
    "ASV5 — 4 cm":"ASV5 — 4 cm","ASV8 — 8 cm":"ASV8 — 8 cm",
}
CALAGE_MAP = {
    "AMX1":"AMX1 — 8 cm (standard)","personnalise":"Calage personnalise — 4 cm min",
    "AMX1 — 8 cm (standard)":"AMX1 — 8 cm (standard)",
    "Calage personnalise — 4 cm min":"Calage personnalise — 4 cm min",
}
ESP_MAP = {
    2.0:"2.0 m (standard)",2.5:"2.5 m",3.0:"3.0 m",
    "2.0":"2.0 m (standard)","2.5":"2.5 m","3.0":"3.0 m",
    "2.0 m (standard)":"2.0 m (standard)","2.5 m":"2.5 m","3.0 m":"3.0 m",
}


def load_from_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    proj = data.get("project", {})
    project_info = {
        "nom_projet": proj.get("nom_projet","Mon projet"),
        "adresse":    proj.get("adresse",""),
        "entreprise": proj.get("entreprise",""),
        "montage":    proj.get("montage",""),
    }
    s = data["scaffolding"]
    maille_val  = float(s["maille"])
    esp_val     = float(s.get("espacement_niveaux", 2.0))
    if "mailles_list" in s and s["mailles_list"]:
        mailles_list = [float(m) for m in s["mailles_list"]]
    else:
        mailles_list = [maille_val] * math.ceil(float(s["longueur"]) / maille_val)
    nb_t = len(mailles_list)
    params = {
        "classe":            CLASSE_MAP.get(s["classe"],       str(s["classe"])),
        "materiel":          MATERIEL_MAP.get(s["materiel"],   str(s["materiel"])),
        "garde_corps":       GARDECORPS_MAP.get(s["garde_corps"], str(s["garde_corps"])),
        "longueur":          float(s["longueur"]),
        "hauteur":           float(s["hauteur"]),
        "maille":            f"{maille_val} m",
        "mailles_list":      mailles_list,
        "espacement_niveaux":ESP_MAP.get(esp_val, f"{esp_val} m"),
        "verins":            VERINS_MAP.get(s.get("verins","ASV5"),  "ASV5 — 4 cm"),
        "calage":            CALAGE_MAP.get(s.get("calage","AMX1"),  "AMX1 — 8 cm (standard)"),
        "console_facade":    CONSOLE_MAP.get(s.get("console_facade",0), "Pas de console"),
        "console_rue":       CONSOLE_MAP.get(s.get("console_rue",   0), "Pas de console"),
        "console_gauche":    CONSOLE_MAP.get(s.get("console_gauche",0), "Pas de console"),
        "console_droit":     CONSOLE_MAP.get(s.get("console_droit", 0), "Pas de console"),
    }
    esp  = float(params["espacement_niveaux"].split()[0])
    nb_n = math.ceil(params["hauteur"] / esp)
    print("\n" + "="*60)
    print(f"  PARAMETRES CHARGES DEPUIS : {json_path}")
    print("="*60)
    print(f"  Projet     : {project_info['nom_projet']}")
    print(f"  Longueur   : {params['longueur']}m | {nb_t} travees : {' ; '.join([str(m)+'m' for m in mailles_list])}")
    print(f"  Hauteur    : {params['hauteur']}m  | {nb_n} niveaux x {esp}m")
    print(f"  Materiel   : {params['materiel'][:20]}")
    print(f"  Garde-corps: {params['garde_corps'][:30]}")
    print(f"  Classe     : {params['classe'][:20]}")
    print(f"  Consoles   : facade={params['console_facade']} | gauche={params['console_gauche']}")
    print("="*60)
    return project_info, params


def generate_json_template(output_path="params_template.json"):
    template = {
        "_comment": "Fichier de parametres pour le generateur d'echafaudage",
        "project": {
            "nom_projet":  "Projet Altrad", "adresse": "Adresse du chantier",
            "entreprise":  "Entreprise utilisatrice", "montage": "Entreprise chargee du montage"
        },
        "scaffolding": {
            "_classe":"2, 3, 4 ou 5", "classe":5,
            "_materiel":"70 ou 100", "materiel":70,
            "_garde_corps":"permanent ou standard", "garde_corps":"permanent",
            "longueur":19.0, "hauteur":12.0,
            "_maille":"maille principale en metres : 2.0, 2.5 ou 3.0", "maille":3.0,
            "_mailles_list":"liste des mailles par travee (laisser vide pour maille uniforme)",
            "mailles_list":[2.0,3.0,3.0,3.0,3.0,3.0,2.0],
            "_espacement":"espacement entre niveaux en metres : 2.0, 2.5 ou 3.0",
            "espacement_niveaux":2.0,
            "_verins":"ASV5 ou ASV8", "verins":"ASV5",
            "_calage":"AMX1 ou personnalise", "calage":"AMX1",
            "_consoles":"largeur en cm : 0 (pas de console), 40 ou 70",
            "console_facade":70, "console_rue":0, "console_gauche":40, "console_droit":0
        }
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    print(f"\n  Template JSON genere : {output_path}")
    return output_path


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def generate_scaffolding_on_building(input_image_path, output_dir="output_scaffolding",
                                      params_json=None):
    print(f"\n{'='*60}")
    print("  GENERATEUR D'ECHAFAUDAGE — Matplotlib + Gemini")
    print(f"{'='*60}")

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY non defini dans .env")

    if params_json:
        project_info, params = load_from_json(params_json)
    else:
        project_info = collect_project_info()
        params       = collect_user_parameters()

    materials   = calculate_materials(params)
    description = analyze_building(input_image_path)
    image_paths = generate_all_views(input_image_path, description, params, output_dir)
    output_pdf  = os.path.join(output_dir, "rapport_echafaudage.pdf")
    generate_pdf(project_info, params, materials, image_paths, input_image_path, output_pdf)

    print(f"\n{'='*60}")
    print("  TERMINE !")
    print(f"  PDF : {output_pdf}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generateur d'echafaudage IA — Matplotlib + Gemini",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-i", "--image",   help="Photo de la facade du batiment")
    parser.add_argument("-p", "--params",  help="Fichier JSON des parametres (optionnel)")
    parser.add_argument("-o", "--output",  default="output_scaffolding", help="Dossier de sortie")
    parser.add_argument("--template",      action="store_true", help="Generer un JSON template et quitter")
    args = parser.parse_args()

    if args.template:
        generate_json_template("params_template.json")
        print("  python scaffolding_gemini.py -i image.jpg -p params_template.json")
        exit(0)

    if not args.image:
        parser.error("-i/--image est requis")

    generate_scaffolding_on_building(
        input_image_path=args.image,
        output_dir=args.output,
        params_json=args.params
    )