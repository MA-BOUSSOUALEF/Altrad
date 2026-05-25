# """
# Application Streamlit — Chat Altrad Plettac Vision
# Interface style LITT — Agent GPT-4o + Génération Gemini
# """

# import streamlit as st
# import os
# import json
# import time
# import math
# import tempfile
# from pathlib import Path
# from dotenv import load_dotenv

# load_dotenv()

# # ─────────────────────────────────────────────
# # CONFIG PAGE
# # ─────────────────────────────────────────────

# st.set_page_config(
#     page_title="Altrad Plettac Vision — Configurateur IA",
#     page_icon="🏗️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# st.markdown("""
# <style>
#     /* ── RESET & BASE ── */
#     .stApp { background-color: #F4F6F9; }
#     section[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E5E7EB; }
#     section[data-testid="stSidebar"] > div { padding: 0 !important; }

#     /* ── SIDEBAR LOGO ── */
#     .sidebar-logo {
#         display: flex; align-items: center; gap: 10px;
#         padding: 18px 16px 14px 16px;
#         border-bottom: 1px solid #F0F0F0;
#     }
#     .sidebar-logo-img {
#         width: 42px; height: 42px; border-radius: 10px;
#         background: linear-gradient(135deg, #E8401C 0%, #FF6B4A 100%);
#         display: flex; align-items: center; justify-content: center;
#         font-size: 1.4em; font-weight: 900; color: white;
#         font-family: 'Arial Black', sans-serif; flex-shrink: 0;
#     }
#     .sidebar-logo-text { line-height: 1.1; }
#     .sidebar-logo-text .brand { font-size: 1.05em; font-weight: 800; color: #E8401C; letter-spacing: -0.3px; }
#     .sidebar-logo-text .sub { font-size: 0.72em; color: #9CA3AF; font-weight: 400; }

#     /* ── SIDEBAR NEW CONV BUTTON ── */
#     .new-conv-wrapper { padding: 12px 14px; }
#     .stButton > button[kind="primary"] {
#         background: #E8401C !important; color: white !important;
#         border: none !important; border-radius: 8px !important;
#         font-weight: 600 !important; font-size: 0.88em !important;
#         padding: 9px 14px !important; width: 100% !important;
#         cursor: pointer !important;
#     }
#     .stButton > button[kind="primary"]:hover { background: #C5341A !important; }

#     /* ── SIDEBAR NAV SECTIONS ── */
#     .sidebar-section-title {
#         font-size: 0.72em; font-weight: 600; color: #9CA3AF;
#         text-transform: uppercase; letter-spacing: 0.8px;
#         padding: 10px 16px 4px 16px;
#     }
#     .conv-item {
#         display: flex; align-items: center; gap: 8px;
#         padding: 8px 16px; cursor: pointer; border-radius: 0;
#         transition: background 0.15s;
#         font-size: 0.85em; color: #374151;
#         white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
#         border-left: 3px solid transparent;
#     }
#     .conv-item:hover { background: #FEF2F0; color: #E8401C; }
#     .conv-item.active { background: #FEF2F0; color: #E8401C; border-left: 3px solid #E8401C; font-weight: 600; }
#     .conv-icon { font-size: 0.9em; flex-shrink: 0; }

#     /* ── SIDEBAR USER ── */
#     .sidebar-user {
#         display: flex; align-items: center; gap: 10px;
#         padding: 12px 16px;
#         border-top: 1px solid #F0F0F0;
#         position: absolute; bottom: 0; width: 100%;
#         background: white;
#     }
#     .user-avatar {
#         width: 32px; height: 32px; border-radius: 50%;
#         background: linear-gradient(135deg, #E8401C, #FF6B4A);
#         display: flex; align-items: center; justify-content: center;
#         color: white; font-weight: 700; font-size: 0.85em; flex-shrink: 0;
#     }
#     .user-info .name { font-size: 0.82em; font-weight: 600; color: #111827; }
#     .user-info .email { font-size: 0.72em; color: #9CA3AF; }

#     /* ── MAIN HEADER ── */
#     .main-header {
#         display: flex; align-items: center; gap: 12px;
#         padding: 14px 0 10px 0; border-bottom: 1px solid #E5E7EB;
#         margin-bottom: 12px;
#     }
#     .main-header-icon {
#         width: 36px; height: 36px; border-radius: 50%;
#         background: linear-gradient(135deg, #E8401C 0%, #FF6B4A 100%);
#         display: flex; align-items: center; justify-content: center;
#         font-size: 1.1em; flex-shrink: 0;
#     }
#     .main-header-text .title { font-size: 1.0em; font-weight: 700; color: #111827; }
#     .main-header-text .sub { font-size: 0.75em; color: #6B7280; }

#     /* ── CHAT MESSAGES ── */
#     .chat-wrapper { max-width: 780px; margin: 0 auto; }

#     .msg-row-user { display: flex; justify-content: flex-end; margin: 10px 0; }
#     .msg-row-agent { display: flex; align-items: flex-start; gap: 10px; margin: 10px 0; }
#     .msg-row-system { display: flex; justify-content: center; margin: 6px 0; }

#     .msg-avatar {
#         width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
#         background: linear-gradient(135deg, #E8401C, #FF6B4A);
#         display: flex; align-items: center; justify-content: center;
#         font-size: 0.9em; margin-top: 2px;
#     }

#     .bubble-user {
#         background: #E8401C; color: white;
#         padding: 11px 16px; border-radius: 18px 18px 4px 18px;
#         max-width: 72%; font-size: 0.92em; line-height: 1.5;
#         box-shadow: 0 2px 8px rgba(232,64,28,0.25);
#     }
#     .bubble-agent {
#         background: #FFFFFF; color: #1F2937;
#         padding: 11px 16px; border-radius: 18px 18px 18px 4px;
#         max-width: 78%; font-size: 0.92em; line-height: 1.5;
#         border: 1px solid #E5E7EB;
#         box-shadow: 0 1px 4px rgba(0,0,0,0.06);
#     }
#     .bubble-system {
#         background: #F3F4F6; color: #6B7280;
#         padding: 5px 14px; border-radius: 20px;
#         font-size: 0.78em; font-style: italic;
#     }

#     /* ── WELCOME MESSAGE ── */
#     .welcome-box {
#         background: white; border: 1px solid #E5E7EB;
#         border-radius: 16px; padding: 22px 24px;
#         max-width: 600px; margin: 20px auto 28px auto;
#         box-shadow: 0 2px 8px rgba(0,0,0,0.05);
#     }
#     .welcome-box h3 { color: #E8401C; font-size: 1.05em; margin: 0 0 10px 0; }
#     .welcome-box p, .welcome-box li { color: #374151; font-size: 0.88em; line-height: 1.6; }

#     /* ── CHAT INPUT AREA ── */
#     .input-wrapper {
#         max-width: 780px; margin: 0 auto;
#         background: white; border-radius: 14px;
#         border: 1.5px solid #E5E7EB;
#         box-shadow: 0 2px 12px rgba(0,0,0,0.06);
#         padding: 0;
#     }
#     .stTextInput > div > div > input {
#         background: transparent !important;
#         color: #111827 !important;
#         border: none !important;
#         outline: none !important;
#         box-shadow: none !important;
#         border-radius: 14px !important;
#         font-size: 0.92em !important;
#         padding: 14px 18px !important;
#     }

#     /* ── SUGGESTIONS ── */
#     .suggestion-pill > button {
#         background: white !important; color: #374151 !important;
#         border: 1.5px solid #E5E7EB !important;
#         border-radius: 20px !important; font-size: 0.82em !important;
#         padding: 6px 14px !important; font-weight: 500 !important;
#         transition: all 0.15s !important;
#         white-space: nowrap !important;
#     }
#     .suggestion-pill > button:hover {
#         border-color: #E8401C !important; color: #E8401C !important;
#         background: #FEF2F0 !important;
#     }

#     /* ── PARAMS SIDEBAR CARD ── */
#     .param-card {
#         background: #FAFAFA; border: 1px solid #F0F0F0;
#         border-radius: 10px; padding: 12px 14px; margin-bottom: 8px;
#     }
#     .param-title {
#         color: #E8401C; font-weight: 700; font-size: 0.78em;
#         text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 7px;
#     }
#     .param-row {
#         display: flex; justify-content: space-between;
#         color: #6B7280; font-size: 0.82em; padding: 2px 0;
#     }
#     .param-value { color: #111827; font-weight: 600; }

#     /* ── STATUS BADGES ── */
#     .badge-generating {
#         background: #FFF7ED; border: 1px solid #E8401C;
#         color: #E8401C; padding: 4px 12px; border-radius: 20px;
#         font-size: 0.78em; display: inline-block;
#         animation: pulse 1.5s infinite;
#     }
#     @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
#     .badge-done {
#         background: #F0FDF4; border: 1px solid #22C55E;
#         color: #16A34A; padding: 4px 12px; border-radius: 20px;
#         font-size: 0.78em; display: inline-block;
#     }

#     /* ── MISC ── */
#     #MainMenu, footer, header { visibility: hidden; }
#     .stDivider { margin: 8px 0 !important; }
#     .stButton > button { font-weight: 600 !important; }
# </style>
# """, unsafe_allow_html=True)


# # ─────────────────────────────────────────────
# # SESSION STATE
# # ─────────────────────────────────────────────

# def init_session():
#     from agent import get_default_params
#     if "params" not in st.session_state:
#         st.session_state.params = get_default_params()
#     if "messages" not in st.session_state:
#         st.session_state.messages = []
#     if "conversation_history" not in st.session_state:
#         st.session_state.conversation_history = []
#     if "generated_images" not in st.session_state:
#         st.session_state.generated_images = {}
#     if "building_image" not in st.session_state:
#         st.session_state.building_image = None
#     if "output_dir" not in st.session_state:
#         st.session_state.output_dir = tempfile.mkdtemp()
#     if "pdf_path" not in st.session_state:
#         st.session_state.pdf_path = None
#     if "last_params" not in st.session_state:
#         st.session_state.last_params = None
#     if "last_project_info" not in st.session_state:
#         st.session_state.last_project_info = None
#     if "last_description" not in st.session_state:
#         st.session_state.last_description = ""
#     if "conversations" not in st.session_state:
#         # Historique multi-conversations : liste de dicts {id, title, messages, params, images}
#         st.session_state.conversations = []
#     if "active_conv_id" not in st.session_state:
#         st.session_state.active_conv_id = None

# init_session()


# # ─────────────────────────────────────────────
# # HELPERS
# # ─────────────────────────────────────────────

# def add_message(role, content, images=None, pdf_path=None):
#     msg = {
#         "role": role,
#         "content": content,
#         "images": images or [],
#         "id": str(time.time()),
#     }
#     if pdf_path:
#         msg["pdf_path"] = pdf_path
#     st.session_state.messages.append(msg)


# def save_current_conversation():
#     """Sauvegarde la conversation active dans l'historique."""
#     if not st.session_state.messages:
#         return
#     # Trouver le titre (premier message user)
#     title = "Nouvelle conversation"
#     for m in st.session_state.messages:
#         if m["role"] == "user":
#             title = m["content"][:45] + ("…" if len(m["content"]) > 45 else "")
#             break

#     conv = {
#         "id": st.session_state.active_conv_id or str(time.time()),
#         "title": title,
#         "messages": list(st.session_state.messages),
#         "params": dict(st.session_state.params),
#         "generated_images": dict(st.session_state.generated_images),
#         "conversation_history": list(st.session_state.conversation_history),
#         "building_image": st.session_state.building_image,
#     }
#     # Mettre à jour ou ajouter
#     for i, c in enumerate(st.session_state.conversations):
#         if c["id"] == conv["id"]:
#             st.session_state.conversations[i] = conv
#             return
#     st.session_state.conversations.insert(0, conv)
#     st.session_state.active_conv_id = conv["id"]


# def load_conversation(conv_id):
#     """Charge une conversation depuis l'historique."""
#     from agent import get_default_params
#     for conv in st.session_state.conversations:
#         if conv["id"] == conv_id:
#             st.session_state.messages = list(conv["messages"])
#             st.session_state.params = dict(conv["params"])
#             st.session_state.generated_images = dict(conv["generated_images"])
#             st.session_state.conversation_history = list(conv["conversation_history"])
#             st.session_state.building_image = conv.get("building_image")
#             st.session_state.active_conv_id = conv_id
#             return


# def new_conversation():
#     """Démarre une nouvelle conversation (sauvegarde l'ancienne)."""
#     from agent import get_default_params
#     save_current_conversation()
#     st.session_state.messages = []
#     st.session_state.conversation_history = []
#     st.session_state.generated_images = {}
#     st.session_state.params = get_default_params()
#     st.session_state.building_image = None
#     st.session_state.active_conv_id = str(time.time())
#     st.session_state.pdf_path = None
#     st.session_state.last_params = None
#     st.session_state.last_description = ""


# def params_to_scaffolding_params(params):
#     s = params["scaffolding"]
#     materiel_map = {70: "Metrix 70 — Largeur 70 cm", 100: "Metrix 100 — Largeur 100 cm"}
#     gc_map = {"permanent": "Garde-corps permanent de securite", "standard": "Garde-corps standard"}
#     verins_map = {"ASV5": "ASV5 — 4 cm", "ASV8": "ASV8 — 8 cm"}
#     calage_map = {"AMX1": "AMX1 — 8 cm (standard)", "personnalise": "Calage personnalise — 4 cm min"}
#     console_map = {0: "Pas de console", 40: "Console largeur 40 cm", 70: "Console largeur 70 cm"}
#     classe_map = {2: "Classe 2 — 150 daN/m2", 3: "Classe 3 — 200 daN/m2",
#                   4: "Classe 4 — 300 daN/m2", 5: "Classe 5 — 450 daN/m2"}
#     esp_map = {2.0: "2.0 m (standard)", 2.5: "2.5 m", 3.0: "3.0 m"}

#     maille_val = s["maille"]
#     mailles_list = s["mailles_list"]
#     if not mailles_list:
#         nb_t = math.ceil(s["longueur"] / maille_val)
#         mailles_list = [maille_val] * nb_t

#     return {
#         "classe":            classe_map.get(s["classe"], f"Classe {s['classe']}"),
#         "materiel":          materiel_map.get(s["materiel"], f"Metrix {s['materiel']}"),
#         "garde_corps":       gc_map.get(s["garde_corps"], s["garde_corps"]),
#         "longueur":          float(s["longueur"]),
#         "hauteur":           float(s["hauteur"]),
#         "maille":            f"{maille_val} m",
#         "mailles_list":      [float(m) for m in mailles_list],
#         "espacement_niveaux": esp_map.get(float(s["espacement_niveaux"]), f"{s['espacement_niveaux']} m"),
#         "verins":            verins_map.get(s["verins"], s["verins"]),
#         "calage":            calage_map.get(s["calage"], s["calage"]),
#         "console_facade":    console_map.get(s["console_facade"], "Pas de console"),
#         "console_rue":       console_map.get(s["console_rue"], "Pas de console"),
#         "console_gauche":    console_map.get(s["console_gauche"], "Pas de console"),
#         "console_droit":     console_map.get(s["console_droit"], "Pas de console"),
#     }


# def generate_views():
#     import sys
#     sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
#     import scaffolding_gemini as sg

#     output_dir = st.session_state.output_dir
#     building_path = st.session_state.building_image
#     params = params_to_scaffolding_params(st.session_state.params)
#     project_info = st.session_state.params["project"]

#     from agent import analyze_building_gpt4o
#     description = analyze_building_gpt4o(building_path)
#     st.session_state.last_description = description

#     # Récupérer les images précédentes pour conserver le style
#     prev_images = st.session_state.generated_images if st.session_state.generated_images else None

#     image_paths = sg.generate_all_views(
#         building_path, description, params, output_dir,
#         prev_images=prev_images
#     )
#     return image_paths, description, params, project_info


# def generate_pdf_report(image_paths, description, params, project_info):
#     import sys
#     sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
#     import scaffolding_gemini as sg

#     output_dir = st.session_state.output_dir
#     materials = sg.calculate_materials(params)
#     output_pdf = os.path.join(output_dir, "rapport_echafaudage.pdf")
#     original_image = st.session_state.building_image
#     sg.generate_pdf(project_info, params, materials, image_paths, original_image, output_pdf)
#     return output_pdf


# # ─────────────────────────────────────────────
# # SIDEBAR
# # ─────────────────────────────────────────────

# with st.sidebar:
#     # ── LOGO ALTRAD ──
#     st.markdown("""
#     <div class='sidebar-logo'>
#         <div class='sidebar-logo-img'>A</div>
#         <div class='sidebar-logo-text'>
#             <div class='brand'>ALTRAD</div>
#             <div class='sub'>La réussite de vos chantiers</div>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

#     # ── NOUVELLE CONVERSATION ──
#     st.markdown("<div class='new-conv-wrapper'>", unsafe_allow_html=True)
#     if st.button("＋  Nouvelle conversation", type="primary", use_container_width=True):
#         new_conversation()
#         st.rerun()
#     st.markdown("</div>", unsafe_allow_html=True)

#     # ── UPLOAD PHOTO ──
#     st.markdown("<div class='sidebar-section-title'>📸 Photo du bâtiment</div>", unsafe_allow_html=True)
#     with st.container():
#         uploaded = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
#         if uploaded:
#             img_path = os.path.join(st.session_state.output_dir, "building.jpg")
#             with open(img_path, "wb") as f:
#                 f.write(uploaded.getbuffer())
#             st.session_state.building_image = img_path
#             st.image(uploaded, use_container_width=True)
#             st.success("Photo chargée ✓")

#     st.divider()

#     # ── HISTORIQUE CONVERSATIONS ──
#     if st.session_state.conversations:
#         st.markdown("<div class='sidebar-section-title'>Conversations</div>", unsafe_allow_html=True)
#         for conv in st.session_state.conversations[:15]:
#             is_active = conv["id"] == st.session_state.active_conv_id
#             css_class = "conv-item active" if is_active else "conv-item"
#             # Bouton cliquable pour chaque conversation
#             btn_label = f"💬  {conv['title']}"
#             if st.button(btn_label, key=f"conv_{conv['id']}", use_container_width=True):
#                 save_current_conversation()
#                 load_conversation(conv["id"])
#                 st.rerun()

#     st.divider()

#     # ── CONFIGURATION ACTUELLE ──
#     s = st.session_state.params["scaffolding"]
#     p = st.session_state.params["project"]
#     nb_t = len(s["mailles_list"]) if s["mailles_list"] else math.ceil(s["longueur"] / s["maille"])
#     nb_n = math.ceil(s["hauteur"] / s["espacement_niveaux"])

#     st.markdown("<div class='sidebar-section-title'>⚙️ Configuration actuelle</div>", unsafe_allow_html=True)
#     st.markdown(f"""
#     <div class='param-card'>
#         <div class='param-title'>📐 Dimensions</div>
#         <div class='param-row'><span>Longueur</span><span class='param-value'>{s['longueur']}m</span></div>
#         <div class='param-row'><span>Hauteur</span><span class='param-value'>{s['hauteur']}m</span></div>
#         <div class='param-row'><span>Travées</span><span class='param-value'>{nb_t}</span></div>
#         <div class='param-row'><span>Niveaux</span><span class='param-value'>{nb_n}</span></div>
#     </div>
#     <div class='param-card'>
#         <div class='param-title'>🔧 Matériel</div>
#         <div class='param-row'><span>Système</span><span class='param-value'>Metrix {s['materiel']}</span></div>
#         <div class='param-row'><span>Classe</span><span class='param-value'>{s['classe']}</span></div>
#         <div class='param-row'><span>Garde-corps</span><span class='param-value'>{s['garde_corps']}</span></div>
#         <div class='param-row'><span>Vérins</span><span class='param-value'>{s['verins']}</span></div>
#     </div>
#     <div class='param-card'>
#         <div class='param-title'>📦 Consoles</div>
#         <div class='param-row'><span>Façade</span><span class='param-value'>{s['console_facade']}cm</span></div>
#         <div class='param-row'><span>Gauche</span><span class='param-value'>{s['console_gauche']}cm</span></div>
#         <div class='param-row'><span>Rue</span><span class='param-value'>{s['console_rue']}cm</span></div>
#         <div class='param-row'><span>Droit</span><span class='param-value'>{s['console_droit']}cm</span></div>
#     </div>
#     """, unsafe_allow_html=True)

#     # ── RESET ──
#     if st.button("🔄 Réinitialiser", use_container_width=True):
#         new_conversation()
#         st.rerun()


# # ─────────────────────────────────────────────
# # ZONE PRINCIPALE — CHAT
# # ─────────────────────────────────────────────

# # Header principal
# st.markdown("""
# <div class='main-header'>
#     <div class='main-header-icon'>🏗️</div>
#     <div class='main-header-text'>
#         <div class='title'>Comment puis-je vous aider, quelle est votre question ?</div>
#         <div class='sub'>propulsé par Altrad Plettac Vision IA — GPT-4o × Gemini</div>
#     </div>
# </div>
# """, unsafe_allow_html=True)

# # ── MESSAGES ──
# chat_col, _ = st.columns([3, 0.001])  # Centrage léger
# with chat_col:
#     # Message de bienvenue si pas de messages
#     if not st.session_state.messages:
#         st.markdown("""
#         <div class='welcome-box'>
#             <h3>👋 Bienvenue sur Altrad Plettac Vision</h3>
#             <p>Je suis votre assistant configurateur d'échafaudage IA.<br>
#             Uploadez la photo de votre bâtiment dans la sidebar, puis décrivez votre projet :</p>
#             <ul>
#                 <li><em>« Je veux un échafaudage de 20m de long et 10m de haut »</em></li>
#                 <li><em>« Classe 5, Metrix 70, avec console 70cm en façade »</em></li>
#                 <li><em>« C'est pour un ravalement, entreprise BTP Atlas »</em></li>
#             </ul>
#         </div>
#         """, unsafe_allow_html=True)

#     # Affichage de TOUS les messages (historique complet, ne s'efface jamais)
#     for msg in st.session_state.messages:
#         if msg["role"] == "user":
#             st.markdown(f"""
#             <div class='msg-row-user'>
#                 <div class='bubble-user'>{msg['content']}</div>
#             </div>""", unsafe_allow_html=True)

#         elif msg["role"] == "agent":
#             st.markdown(f"""
#             <div class='msg-row-agent'>
#                 <div class='msg-avatar'>🏗️</div>
#                 <div class='bubble-agent'>{msg['content']}</div>
#             </div>""", unsafe_allow_html=True)

#         elif msg["role"] == "system":
#             st.markdown(f"""
#             <div class='msg-row-system'>
#                 <div class='bubble-system'>{msg['content']}</div>
#             </div>""", unsafe_allow_html=True)

#         # Images générées
#         if msg.get("images"):
#             valid_imgs = [p for p in msg["images"] if os.path.exists(p)]
#             if valid_imgs:
#                 cols = st.columns(2)
#                 for idx, img_path in enumerate(valid_imgs):
#                     with cols[idx % 2]:
#                         st.image(img_path, use_container_width=True)

#         # Téléchargement PDF
#         if msg.get("pdf_path") and os.path.exists(msg["pdf_path"]):
#             with open(msg["pdf_path"], "rb") as f:
#                 st.download_button(
#                     "📄 Télécharger le rapport PDF",
#                     f.read(),
#                     file_name="rapport_echafaudage_altrad.pdf",
#                     mime="application/pdf",
#                     key=f"pdf_{msg.get('id', time.time())}"
#                 )


# # ─────────────────────────────────────────────
# # ZONE SAISIE
# # ─────────────────────────────────────────────

# st.markdown("<br>", unsafe_allow_html=True)

# col_input, col_send = st.columns([6, 1])
# with col_input:
#     user_input = st.text_input(
#         "",
#         placeholder="Toutes vos questions...",
#         key="chat_input",
#         label_visibility="collapsed"
#     )
# with col_send:
#     send_btn = st.button("Envoyer ▶", use_container_width=True)

# # Suggestions rapides
# sug_cols = st.columns(4)
# suggestions_list = [
#     ("Chiffrage Cloison ALTRAD", "Chiffrage Cloison ALTRAD"),
#     ("Ajouter un étage", "Ajouter un étage"),
#     ("Console 70cm façade", "Console 70cm façade"),
#     ("Générer le PDF", "Générer le PDF"),
# ]
# clicked_suggestion = None
# for i, (label, value) in enumerate(suggestions_list):
#     with sug_cols[i]:
#         with st.container():
#             st.markdown("<div class='suggestion-pill'>", unsafe_allow_html=True)
#             if st.button(label, key=f"sug_{i}", use_container_width=True):
#                 clicked_suggestion = value
#             st.markdown("</div>", unsafe_allow_html=True)


# # ─────────────────────────────────────────────
# # TRAITEMENT MESSAGE
# # ─────────────────────────────────────────────

# message_to_process = None
# if send_btn and user_input.strip():
#     message_to_process = user_input.strip()
# elif clicked_suggestion:
#     message_to_process = clicked_suggestion

# if message_to_process:
#     if not st.session_state.building_image:
#         add_message("agent",
#                     "⚠️ Veuillez d'abord uploader la photo de votre bâtiment dans la sidebar à gauche.")
#         st.rerun()

#     add_message("user", message_to_process)

#     from agent import chat_with_agent
#     with st.spinner("L'agent réfléchit..."):
#         result, updated_params, updated_history = chat_with_agent(
#             message_to_process,
#             st.session_state.params,
#             st.session_state.conversation_history
#         )

#     st.session_state.params = updated_params
#     st.session_state.conversation_history = updated_history

#     agent_message = result.get("message", "")
#     add_message("agent", agent_message)

#     if result.get("modifications"):
#         add_message("system", f"✏️ Paramètres mis à jour : {', '.join(result['modifications'].keys())}")

#     if result.get("demande_generation"):
#         add_message("system", "⏳ Génération en cours (Matplotlib → Gemini)...")

#     if result.get("demande_pdf"):
#         if st.session_state.generated_images:
#             add_message("system", "⏳ Génération du PDF en cours...")
#         else:
#             add_message("agent", "⚠️ Veuillez d'abord générer les vues avant de créer le PDF.")

#     # Sauvegarder la conversation dans l'historique après chaque échange
#     save_current_conversation()
#     st.rerun()


# # ─────────────────────────────────────────────
# # GÉNÉRATION EN ARRIÈRE-PLAN
# # ─────────────────────────────────────────────

# last_msg = st.session_state.messages[-1] if st.session_state.messages else None
# need_generation = last_msg and last_msg.get("role") == "system" and "Génération en cours" in last_msg.get("content", "")
# need_pdf = last_msg and last_msg.get("role") == "system" and "PDF en cours" in last_msg.get("content", "")

# if need_generation:
#     try:
#         with st.spinner("🔄 Génération des vues (Matplotlib → Gemini)..."):
#             image_paths, description, params, project_info = generate_views()

#             # Stocker les nouvelles images générées (pour la prochaine modification)
#             st.session_state.generated_images = image_paths
#             st.session_state.last_params = params
#             st.session_state.last_project_info = project_info

#             images_to_show = []
#             for key in ["batiment", "gemini_iso", "gemini_top", "gemini_cote"]:
#                 if key in image_paths and os.path.exists(image_paths[key]):
#                     images_to_show.append(image_paths[key])

#             # Supprimer les messages temporaires (en cours, étapes)
#             st.session_state.messages = [
#                 m for m in st.session_state.messages
#                 if "en cours" not in m.get("content", "")
#                 and "Étape" not in m.get("content", "")
#             ]

#             st.session_state.messages.append({
#                 "role": "agent",
#                 "content": "✅ Vues générées ! Voici votre échafaudage Altrad Plettac Metrix.<br>"
#                            "Vous pouvez demander des modifications ou me dire <strong>« génère le PDF »</strong>.",
#                 "images": images_to_show,
#                 "id": str(time.time()),
#             })

#     except Exception as e:
#         st.session_state.messages = [
#             m for m in st.session_state.messages
#             if "en cours" not in m.get("content", "")
#         ]
#         add_message("agent", f"❌ Erreur lors de la génération : {str(e)}")

#     save_current_conversation()
#     st.rerun()

# if need_pdf:
#     try:
#         with st.spinner("📄 Génération du PDF..."):
#             if st.session_state.last_params and st.session_state.generated_images:
#                 pdf_path = generate_pdf_report(
#                     st.session_state.generated_images,
#                     st.session_state.last_description,
#                     st.session_state.last_params,
#                     st.session_state.last_project_info
#                 )
#                 st.session_state.pdf_path = pdf_path

#                 st.session_state.messages = [
#                     m for m in st.session_state.messages
#                     if "en cours" not in m.get("content", "")
#                 ]

#                 st.session_state.messages.append({
#                     "role": "agent",
#                     "content": "✅ Votre rapport PDF est prêt ! Cliquez pour le télécharger.",
#                     "images": [],
#                     "pdf_path": pdf_path,
#                     "id": str(time.time()),
#                 })
#             else:
#                 st.session_state.messages = [
#                     m for m in st.session_state.messages
#                     if "en cours" not in m.get("content", "")
#                 ]
#                 add_message("agent", "⚠️ Veuillez d'abord générer les vues. Dites 'génère les vues'.")

#     except Exception as e:
#         st.session_state.messages = [
#             m for m in st.session_state.messages
#             if "en cours" not in m.get("content", "")
#         ]
#         add_message("agent", f"❌ Erreur PDF : {str(e)}")

#     save_current_conversation()
#     st.rerun()

"""
Application Streamlit — Chat Altrad Plettac Vision
Interface style LITT — Agent GPT-4o + Génération Gemini
"""

import streamlit as st
import os
import json
import time
import math
import tempfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# CONFIG PAGE
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Altrad Plettac Vision — Configurateur IA",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* ── RESET & BASE ── */
    .stApp { background-color: #F4F6F9; }
    section[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E5E7EB; }
    section[data-testid="stSidebar"] > div { padding: 0 !important; }

    /* ── SIDEBAR LOGO ── */
    .sidebar-logo {
        display: flex; align-items: center; gap: 10px;
        padding: 18px 16px 14px 16px;
        border-bottom: 1px solid #F0F0F0;
    }
    .sidebar-logo-img {
        width: 42px; height: 42px; border-radius: 10px;
        background: linear-gradient(135deg, #E8401C 0%, #FF6B4A 100%);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.4em; font-weight: 900; color: white;
        font-family: 'Arial Black', sans-serif; flex-shrink: 0;
    }
    .sidebar-logo-text { line-height: 1.1; }
    .sidebar-logo-text .brand { font-size: 1.05em; font-weight: 800; color: #E8401C; letter-spacing: -0.3px; }
    .sidebar-logo-text .sub { font-size: 0.72em; color: #9CA3AF; font-weight: 400; }

    /* ── SIDEBAR NEW CONV BUTTON ── */
    .new-conv-wrapper { padding: 12px 14px; }
    .stButton > button[kind="primary"] {
        background: #E8401C !important; color: white !important;
        border: none !important; border-radius: 8px !important;
        font-weight: 600 !important; font-size: 0.88em !important;
        padding: 9px 14px !important; width: 100% !important;
        cursor: pointer !important;
    }
    .stButton > button[kind="primary"]:hover { background: #C5341A !important; }

    /* ── SIDEBAR NAV SECTIONS ── */
    .sidebar-section-title {
        font-size: 0.72em; font-weight: 600; color: #9CA3AF;
        text-transform: uppercase; letter-spacing: 0.8px;
        padding: 10px 16px 4px 16px;
    }
    .conv-item {
        display: flex; align-items: center; gap: 8px;
        padding: 8px 16px; cursor: pointer; border-radius: 0;
        transition: background 0.15s;
        font-size: 0.85em; color: #374151;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        border-left: 3px solid transparent;
    }
    .conv-item:hover { background: #FEF2F0; color: #E8401C; }
    .conv-item.active { background: #FEF2F0; color: #E8401C; border-left: 3px solid #E8401C; font-weight: 600; }
    .conv-icon { font-size: 0.9em; flex-shrink: 0; }

    /* ── SIDEBAR USER ── */
    .sidebar-user {
        display: flex; align-items: center; gap: 10px;
        padding: 12px 16px;
        border-top: 1px solid #F0F0F0;
        position: absolute; bottom: 0; width: 100%;
        background: white;
    }
    .user-avatar {
        width: 32px; height: 32px; border-radius: 50%;
        background: linear-gradient(135deg, #E8401C, #FF6B4A);
        display: flex; align-items: center; justify-content: center;
        color: white; font-weight: 700; font-size: 0.85em; flex-shrink: 0;
    }
    .user-info .name { font-size: 0.82em; font-weight: 600; color: #111827; }
    .user-info .email { font-size: 0.72em; color: #9CA3AF; }

    /* ── MAIN HEADER ── */
    .main-header {
        display: flex; align-items: center; gap: 12px;
        padding: 14px 0 10px 0; border-bottom: 1px solid #E5E7EB;
        margin-bottom: 12px;
    }
    .main-header-icon {
        width: 36px; height: 36px; border-radius: 50%;
        background: linear-gradient(135deg, #E8401C 0%, #FF6B4A 100%);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.1em; flex-shrink: 0;
    }
    .main-header-text .title { font-size: 1.0em; font-weight: 700; color: #111827; }
    .main-header-text .sub { font-size: 0.75em; color: #6B7280; }

    /* ── CHAT MESSAGES ── */
    .chat-wrapper { max-width: 780px; margin: 0 auto; }

    .msg-row-user { display: flex; justify-content: flex-end; margin: 10px 0; }
    .msg-row-agent { display: flex; align-items: flex-start; gap: 10px; margin: 10px 0; }
    .msg-row-system { display: flex; justify-content: center; margin: 6px 0; }

    .msg-avatar {
        width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
        background: linear-gradient(135deg, #E8401C, #FF6B4A);
        display: flex; align-items: center; justify-content: center;
        font-size: 0.9em; margin-top: 2px;
    }

    .bubble-user {
        background: #E8401C; color: white;
        padding: 11px 16px; border-radius: 18px 18px 4px 18px;
        max-width: 72%; font-size: 0.92em; line-height: 1.5;
        box-shadow: 0 2px 8px rgba(232,64,28,0.25);
    }
    .bubble-agent {
        background: #FFFFFF; color: #1F2937;
        padding: 11px 16px; border-radius: 18px 18px 18px 4px;
        max-width: 78%; font-size: 0.92em; line-height: 1.5;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .bubble-system {
        background: #F3F4F6; color: #6B7280;
        padding: 5px 14px; border-radius: 20px;
        font-size: 0.78em; font-style: italic;
    }

    /* ── WELCOME MESSAGE ── */
    .welcome-box {
        background: white; border: 1px solid #E5E7EB;
        border-radius: 16px; padding: 22px 24px;
        max-width: 600px; margin: 20px auto 28px auto;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .welcome-box h3 { color: #E8401C; font-size: 1.05em; margin: 0 0 10px 0; }
    .welcome-box p, .welcome-box li { color: #374151; font-size: 0.88em; line-height: 1.6; }

    /* ── CHAT INPUT AREA ── */
    .input-wrapper {
        max-width: 780px; margin: 0 auto;
        background: white; border-radius: 14px;
        border: 1.5px solid #E5E7EB;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        padding: 0;
    }
    /* Force fond blanc + texte foncé sur l'input dans tous les thèmes */
    .stTextInput > div > div > input,
    .stTextInput > div > div > input:focus,
    .stTextInput > div > div > input:active {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1.5px solid #E5E7EB !important;
        outline: none !important;
        box-shadow: none !important;
        border-radius: 12px !important;
        font-size: 0.92em !important;
        padding: 14px 18px !important;
        caret-color: #E8401C !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #9CA3AF !important;
    }
    /* Spinner visible sur fond blanc */
    [data-testid="stSpinner"] p,
    [data-testid="stSpinner"] span,
    .stSpinner p,
    .stSpinner > div { color: #374151 !important; font-weight: 500 !important; }

    /* ── SUGGESTIONS ── */
    .suggestion-pill > button {
        background: white !important; color: #374151 !important;
        border: 1.5px solid #E5E7EB !important;
        border-radius: 20px !important; font-size: 0.82em !important;
        padding: 6px 14px !important; font-weight: 500 !important;
        transition: all 0.15s !important;
        white-space: nowrap !important;
    }
    .suggestion-pill > button:hover {
        border-color: #E8401C !important; color: #E8401C !important;
        background: #FEF2F0 !important;
    }

    /* ── PARAMS SIDEBAR CARD ── */
    .param-card {
        background: #FAFAFA; border: 1px solid #F0F0F0;
        border-radius: 10px; padding: 12px 14px; margin-bottom: 8px;
    }
    .param-title {
        color: #E8401C; font-weight: 700; font-size: 0.78em;
        text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 7px;
    }
    .param-row {
        display: flex; justify-content: space-between;
        color: #6B7280; font-size: 0.82em; padding: 2px 0;
    }
    .param-value { color: #111827; font-weight: 600; }

    /* ── STATUS BADGES ── */
    .badge-generating {
        background: #FFF7ED; border: 1px solid #E8401C;
        color: #E8401C; padding: 4px 12px; border-radius: 20px;
        font-size: 0.78em; display: inline-block;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
    .badge-done {
        background: #F0FDF4; border: 1px solid #22C55E;
        color: #16A34A; padding: 4px 12px; border-radius: 20px;
        font-size: 0.78em; display: inline-block;
    }

    /* ── MISC ── */
    #MainMenu, footer, header { visibility: hidden; }
    .stDivider { margin: 8px 0 !important; }
    .stButton > button { font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────

def init_session():
    from agent import get_default_params
    if "params" not in st.session_state:
        st.session_state.params = get_default_params()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "generated_images" not in st.session_state:
        st.session_state.generated_images = {}
    if "building_image" not in st.session_state:
        st.session_state.building_image = None
    if "output_dir" not in st.session_state:
        st.session_state.output_dir = tempfile.mkdtemp()
    if "pdf_path" not in st.session_state:
        st.session_state.pdf_path = None
    if "last_params" not in st.session_state:
        st.session_state.last_params = None
    if "last_project_info" not in st.session_state:
        st.session_state.last_project_info = None
    if "last_description" not in st.session_state:
        st.session_state.last_description = ""
    if "conversations" not in st.session_state:
        # Historique multi-conversations : liste de dicts {id, title, messages, params, images}
        st.session_state.conversations = []
    if "active_conv_id" not in st.session_state:
        st.session_state.active_conv_id = None

init_session()


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def add_message(role, content, images=None, pdf_path=None):
    msg = {
        "role": role,
        "content": content,
        "images": images or [],
        "id": str(time.time()),
    }
    if pdf_path:
        msg["pdf_path"] = pdf_path
    st.session_state.messages.append(msg)


def save_current_conversation():
    """Sauvegarde la conversation active dans l'historique."""
    if not st.session_state.messages:
        return
    # Trouver le titre (premier message user)
    title = "Nouvelle conversation"
    for m in st.session_state.messages:
        if m["role"] == "user":
            title = m["content"][:45] + ("…" if len(m["content"]) > 45 else "")
            break

    conv = {
        "id": st.session_state.active_conv_id or str(time.time()),
        "title": title,
        "messages": list(st.session_state.messages),
        "params": dict(st.session_state.params),
        "generated_images": dict(st.session_state.generated_images),
        "conversation_history": list(st.session_state.conversation_history),
        "building_image": st.session_state.building_image,
    }
    # Mettre à jour ou ajouter
    for i, c in enumerate(st.session_state.conversations):
        if c["id"] == conv["id"]:
            st.session_state.conversations[i] = conv
            return
    st.session_state.conversations.insert(0, conv)
    st.session_state.active_conv_id = conv["id"]


def load_conversation(conv_id):
    """Charge une conversation depuis l'historique."""
    from agent import get_default_params
    for conv in st.session_state.conversations:
        if conv["id"] == conv_id:
            st.session_state.messages = list(conv["messages"])
            st.session_state.params = dict(conv["params"])
            st.session_state.generated_images = dict(conv["generated_images"])
            st.session_state.conversation_history = list(conv["conversation_history"])
            st.session_state.building_image = conv.get("building_image")
            st.session_state.active_conv_id = conv_id
            return


def new_conversation():
    """Démarre une nouvelle conversation (sauvegarde l'ancienne)."""
    from agent import get_default_params
    save_current_conversation()
    st.session_state.messages = []
    st.session_state.conversation_history = []
    st.session_state.generated_images = {}
    st.session_state.params = get_default_params()
    st.session_state.building_image = None
    st.session_state.active_conv_id = str(time.time())
    st.session_state.pdf_path = None
    st.session_state.last_params = None
    st.session_state.last_description = ""


def params_to_scaffolding_params(params):
    s = params["scaffolding"]
    materiel_map = {70: "Metrix 70 — Largeur 70 cm", 100: "Metrix 100 — Largeur 100 cm"}
    gc_map = {"permanent": "Garde-corps permanent de securite", "standard": "Garde-corps standard"}
    verins_map = {"ASV5": "ASV5 — 4 cm", "ASV8": "ASV8 — 8 cm"}
    calage_map = {"AMX1": "AMX1 — 8 cm (standard)", "personnalise": "Calage personnalise — 4 cm min"}
    console_map = {0: "Pas de console", 40: "Console largeur 40 cm", 70: "Console largeur 70 cm"}
    classe_map = {2: "Classe 2 — 150 daN/m2", 3: "Classe 3 — 200 daN/m2",
                  4: "Classe 4 — 300 daN/m2", 5: "Classe 5 — 450 daN/m2"}
    esp_map = {2.0: "2.0 m (standard)", 2.5: "2.5 m", 3.0: "3.0 m"}

    maille_val = s["maille"]
    mailles_list = s["mailles_list"]
    if not mailles_list:
        nb_t = math.ceil(s["longueur"] / maille_val)
        mailles_list = [maille_val] * nb_t

    return {
        "classe":            classe_map.get(s["classe"], f"Classe {s['classe']}"),
        "materiel":          materiel_map.get(s["materiel"], f"Metrix {s['materiel']}"),
        "garde_corps":       gc_map.get(s["garde_corps"], s["garde_corps"]),
        "longueur":          float(s["longueur"]),
        "hauteur":           float(s["hauteur"]),
        "maille":            f"{maille_val} m",
        "mailles_list":      [float(m) for m in mailles_list],
        "espacement_niveaux": esp_map.get(float(s["espacement_niveaux"]), f"{s['espacement_niveaux']} m"),
        "verins":            verins_map.get(s["verins"], s["verins"]),
        "calage":            calage_map.get(s["calage"], s["calage"]),
        "console_facade":    console_map.get(s["console_facade"], "Pas de console"),
        "console_rue":       console_map.get(s["console_rue"], "Pas de console"),
        "console_gauche":    console_map.get(s["console_gauche"], "Pas de console"),
        "console_droit":     console_map.get(s["console_droit"], "Pas de console"),
    }


def generate_views():
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import scaffolding_gemini as sg

    output_dir = st.session_state.output_dir
    building_path = st.session_state.building_image
    params = params_to_scaffolding_params(st.session_state.params)
    project_info = st.session_state.params["project"]

    # Si pas de photo → créer une image de fond générique (mur neutre)
    if not building_path or not os.path.exists(building_path):
        from PIL import Image as PILImage
        import numpy as np
        # Fond neutre couleur façade
        w, h = 1200, 900
        arr = np.full((h, w, 3), [200, 190, 175], dtype=np.uint8)
        placeholder_path = os.path.join(output_dir, "building_placeholder.jpg")
        PILImage.fromarray(arr).save(placeholder_path)
        building_path = placeholder_path
        description = "a neutral building facade (no photo provided)"
    else:
        from agent import analyze_building_gpt4o
        description = analyze_building_gpt4o(building_path)

    st.session_state.last_description = description

    # Récupérer les images précédentes pour conserver le style
    prev_images = st.session_state.generated_images if st.session_state.generated_images else None

    image_paths = sg.generate_all_views(
        building_path, description, params, output_dir,
        prev_images=prev_images
    )
    return image_paths, description, params, project_info


def generate_pdf_report(image_paths, description, params, project_info):
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import scaffolding_gemini as sg

    output_dir = st.session_state.output_dir
    materials = sg.calculate_materials(params)
    output_pdf = os.path.join(output_dir, "rapport_echafaudage.pdf")
    original_image = st.session_state.building_image
    sg.generate_pdf(project_info, params, materials, image_paths, original_image, output_pdf)
    return output_pdf


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    # ── LOGO ALTRAD ──
    st.markdown("""
    <div class='sidebar-logo'>
        <div class='sidebar-logo-img'>A</div>
        <div class='sidebar-logo-text'>
            <div class='brand'>ALTRAD</div>
            <div class='sub'>La réussite de vos chantiers</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── NOUVELLE CONVERSATION ──
    st.markdown("<div class='new-conv-wrapper'>", unsafe_allow_html=True)
    if st.button("＋  Nouvelle conversation", type="primary", use_container_width=True):
        new_conversation()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # ── UPLOAD PHOTO ──
    st.markdown("<div class='sidebar-section-title'>📸 Photo du bâtiment</div>", unsafe_allow_html=True)
    with st.container():
        uploaded = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if uploaded:
            img_path = os.path.join(st.session_state.output_dir, "building.jpg")
            with open(img_path, "wb") as f:
                f.write(uploaded.getbuffer())
            st.session_state.building_image = img_path
            st.image(uploaded, use_container_width=True)
            st.success("Photo chargée ✓")

    st.divider()

    # ── HISTORIQUE CONVERSATIONS ──
    if st.session_state.conversations:
        st.markdown("<div class='sidebar-section-title'>Conversations</div>", unsafe_allow_html=True)
        for conv in st.session_state.conversations[:15]:
            is_active = conv["id"] == st.session_state.active_conv_id
            css_class = "conv-item active" if is_active else "conv-item"
            # Bouton cliquable pour chaque conversation
            btn_label = f"💬  {conv['title']}"
            if st.button(btn_label, key=f"conv_{conv['id']}", use_container_width=True):
                save_current_conversation()
                load_conversation(conv["id"])
                st.rerun()

    st.divider()

    # ── CONFIGURATION ACTUELLE ──
    s = st.session_state.params["scaffolding"]
    p = st.session_state.params["project"]
    nb_t = len(s["mailles_list"]) if s["mailles_list"] else math.ceil(s["longueur"] / s["maille"])
    nb_n = math.ceil(s["hauteur"] / s["espacement_niveaux"])

    st.markdown("<div class='sidebar-section-title'>⚙️ Configuration actuelle</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='param-card'>
        <div class='param-title'>📐 Dimensions</div>
        <div class='param-row'><span>Longueur</span><span class='param-value'>{s['longueur']}m</span></div>
        <div class='param-row'><span>Hauteur</span><span class='param-value'>{s['hauteur']}m</span></div>
        <div class='param-row'><span>Travées</span><span class='param-value'>{nb_t}</span></div>
        <div class='param-row'><span>Niveaux</span><span class='param-value'>{nb_n}</span></div>
    </div>
    <div class='param-card'>
        <div class='param-title'>🔧 Matériel</div>
        <div class='param-row'><span>Système</span><span class='param-value'>Metrix {s['materiel']}</span></div>
        <div class='param-row'><span>Classe</span><span class='param-value'>{s['classe']}</span></div>
        <div class='param-row'><span>Garde-corps</span><span class='param-value'>{s['garde_corps']}</span></div>
        <div class='param-row'><span>Vérins</span><span class='param-value'>{s['verins']}</span></div>
    </div>
    <div class='param-card'>
        <div class='param-title'>📦 Consoles</div>
        <div class='param-row'><span>Façade</span><span class='param-value'>{s['console_facade']}cm</span></div>
        <div class='param-row'><span>Gauche</span><span class='param-value'>{s['console_gauche']}cm</span></div>
        <div class='param-row'><span>Rue</span><span class='param-value'>{s['console_rue']}cm</span></div>
        <div class='param-row'><span>Droit</span><span class='param-value'>{s['console_droit']}cm</span></div>
    </div>
    """, unsafe_allow_html=True)

    # ── RESET ──
    if st.button("🔄 Réinitialiser", use_container_width=True):
        new_conversation()
        st.rerun()


# ─────────────────────────────────────────────
# ZONE PRINCIPALE — CHAT
# ─────────────────────────────────────────────

# Header principal
st.markdown("""
<div class='main-header'>
    <div class='main-header-icon'>🏗️</div>
    <div class='main-header-text'>
        <div class='title'>Comment puis-je vous aider, quelle est votre question ?</div>
        <div class='sub'>propulsé par Altrad Plettac Vision IA — GPT-4o × Gemini</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── MESSAGES ──
chat_col, _ = st.columns([3, 0.001])  # Centrage léger
with chat_col:
    # Message de bienvenue si pas de messages
    if not st.session_state.messages:
        st.markdown("""
        <div class='welcome-box'>
            <h3>👋 Bienvenue sur Altrad Plettac Vision</h3>
            <p>Je suis votre assistant configurateur d'échafaudage IA.<br>
            Uploadez la photo de votre bâtiment dans la sidebar, puis décrivez votre projet :</p>
            <ul>
                <li><em>« Je veux un échafaudage de 20m de long et 10m de haut »</em></li>
                <li><em>« Classe 5, Metrix 70, avec console 70cm en façade »</em></li>
                <li><em>« C'est pour un ravalement, entreprise BTP Atlas »</em></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Affichage de TOUS les messages (historique complet, ne s'efface jamais)
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class='msg-row-user'>
                <div class='bubble-user'>{msg['content']}</div>
            </div>""", unsafe_allow_html=True)

        elif msg["role"] == "agent":
            st.markdown(f"""
            <div class='msg-row-agent'>
                <div class='msg-avatar'>🏗️</div>
                <div class='bubble-agent'>{msg['content']}</div>
            </div>""", unsafe_allow_html=True)

        elif msg["role"] == "system":
            st.markdown(f"""
            <div class='msg-row-system'>
                <div class='bubble-system'>{msg['content']}</div>
            </div>""", unsafe_allow_html=True)

        # Images générées
        if msg.get("images"):
            valid_imgs = [p for p in msg["images"] if os.path.exists(p)]
            if valid_imgs:
                cols = st.columns(2)
                for idx, img_path in enumerate(valid_imgs):
                    with cols[idx % 2]:
                        st.image(img_path, use_container_width=True)

        # Téléchargement PDF
        if msg.get("pdf_path") and os.path.exists(msg["pdf_path"]):
            with open(msg["pdf_path"], "rb") as f:
                st.download_button(
                    "📄 Télécharger le rapport PDF",
                    f.read(),
                    file_name="rapport_echafaudage_altrad.pdf",
                    mime="application/pdf",
                    key=f"pdf_{msg.get('id', time.time())}"
                )


# ─────────────────────────────────────────────
# ZONE SAISIE
# ─────────────────────────────────────────────

st.markdown("<br>", unsafe_allow_html=True)

# st.form capture la touche Entrée ET le bouton Envoyer
with st.form(key="chat_form", clear_on_submit=True):
    col_input, col_send = st.columns([6, 1])
    with col_input:
        user_input = st.text_input(
            "",
            placeholder="Toutes vos questions...",
            key="chat_input",
            label_visibility="collapsed"
        )
    with col_send:
        send_btn = st.form_submit_button("Envoyer ▶", use_container_width=True)

# Suggestions rapides (hors du form)
sug_cols = st.columns(4)
suggestions_list = [
    ("Chiffrage Cloison ALTRAD", "Chiffrage Cloison ALTRAD"),
    ("Ajouter un étage", "Ajouter un étage"),
    ("Console 70cm façade", "Console 70cm façade"),
    ("Générer le PDF", "Générer le PDF"),
]
clicked_suggestion = None
for i, (label, value) in enumerate(suggestions_list):
    with sug_cols[i]:
        with st.container():
            st.markdown("<div class='suggestion-pill'>", unsafe_allow_html=True)
            if st.button(label, key=f"sug_{i}", use_container_width=True):
                clicked_suggestion = value
            st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TRAITEMENT MESSAGE
# ─────────────────────────────────────────────

message_to_process = None
if send_btn and user_input.strip():
    message_to_process = user_input.strip()
elif clicked_suggestion:
    message_to_process = clicked_suggestion

if message_to_process:
    add_message("user", message_to_process)

    from agent import chat_with_agent
    # Afficher "l'agent réfléchit" dans la zone messages
    add_message("system", "⏳ L'agent réfléchit...")
    save_current_conversation()
    st.rerun()

# Détecter si l'agent doit réfléchir (dernier message = "L'agent réfléchit...")
last_msg_content = st.session_state.messages[-1].get("content", "") if st.session_state.messages else ""
need_agent = (
    st.session_state.messages
    and st.session_state.messages[-1].get("role") == "system"
    and "L'agent réfléchit" in last_msg_content
    and len(st.session_state.messages) >= 2
    and st.session_state.messages[-2].get("role") == "user"
)

if need_agent:
    user_msg = st.session_state.messages[-2]["content"]
    # Supprimer le message "L'agent réfléchit..."
    st.session_state.messages = [
        m for m in st.session_state.messages
        if "L'agent réfléchit" not in m.get("content", "")
    ]

    from agent import chat_with_agent
    result, updated_params, updated_history = chat_with_agent(
        user_msg,
        st.session_state.params,
        st.session_state.conversation_history
    )

    st.session_state.params = updated_params
    st.session_state.conversation_history = updated_history

    agent_message = result.get("message", "")
    add_message("agent", agent_message)

    if result.get("modifications"):
        add_message("system", f"✏️ Paramètres mis à jour : {', '.join(result['modifications'].keys())}")

    if result.get("demande_generation"):
        # Vérifier si une photo est disponible ; sinon générer sans (Gemini utilisera un fond générique)
        if not st.session_state.building_image:
            add_message("system", "ℹ️ Aucune photo uploadée — génération sans bâtiment.")
        add_message("system", "⏳ Génération en cours ...")

    if result.get("demande_pdf"):
        if st.session_state.generated_images:
            add_message("system", "⏳ Génération du PDF en cours...")
        else:
            add_message("agent", "⚠️ Veuillez d'abord générer les vues avant de créer le PDF.")

    save_current_conversation()
    st.rerun()


# ─────────────────────────────────────────────
# GÉNÉRATION EN ARRIÈRE-PLAN
# ─────────────────────────────────────────────

last_msg = st.session_state.messages[-1] if st.session_state.messages else None
need_generation = last_msg and last_msg.get("role") == "system" and "Génération en cours" in last_msg.get("content", "")
need_pdf = last_msg and last_msg.get("role") == "system" and "PDF en cours" in last_msg.get("content", "")

if need_generation:
    try:
        image_paths, description, params, project_info = generate_views()

        # Stocker les nouvelles images générées (pour la prochaine modification)
        st.session_state.generated_images = image_paths
        st.session_state.last_params = params
        st.session_state.last_project_info = project_info

        images_to_show = []
        for key in ["batiment", "gemini_iso", "gemini_top", "gemini_cote"]:
            if key in image_paths and os.path.exists(image_paths[key]):
                images_to_show.append(image_paths[key])

        # Supprimer les messages temporaires (en cours, étapes, info)
        st.session_state.messages = [
            m for m in st.session_state.messages
            if "en cours" not in m.get("content", "")
            and "Étape" not in m.get("content", "")
            and "Aucune photo" not in m.get("content", "")
        ]

        st.session_state.messages.append({
            "role": "agent",
            "content": "✅ Vues générées ! Voici votre échafaudage Altrad Plettac Metrix.<br>"
                       "Vous pouvez demander des modifications ou me dire <strong>« génère le PDF »</strong>.",
            "images": images_to_show,
            "id": str(time.time()),
        })

    except Exception as e:
        st.session_state.messages = [
            m for m in st.session_state.messages
            if "en cours" not in m.get("content", "")
            and "Aucune photo" not in m.get("content", "")
        ]
        add_message("agent", f"❌ Erreur lors de la génération : {str(e)}")

    save_current_conversation()
    st.rerun()

if need_pdf:
    try:
        if st.session_state.last_params and st.session_state.generated_images:
            pdf_path = generate_pdf_report(
                st.session_state.generated_images,
                st.session_state.last_description,
                st.session_state.last_params,
                st.session_state.last_project_info
            )
            st.session_state.pdf_path = pdf_path

            st.session_state.messages = [
                m for m in st.session_state.messages
                if "en cours" not in m.get("content", "")
            ]

            st.session_state.messages.append({
                "role": "agent",
                "content": "✅ Votre rapport PDF est prêt ! Cliquez pour le télécharger.",
                "images": [],
                "pdf_path": pdf_path,
                "id": str(time.time()),
            })
        else:
            st.session_state.messages = [
                m for m in st.session_state.messages
                if "en cours" not in m.get("content", "")
            ]
            add_message("agent", "⚠️ Veuillez d'abord générer les vues. Dites 'génère les vues'.")

    except Exception as e:
        st.session_state.messages = [
            m for m in st.session_state.messages
            if "en cours" not in m.get("content", "")
        ]
        add_message("agent", f"❌ Erreur PDF : {str(e)}")

    save_current_conversation()
    st.rerun()