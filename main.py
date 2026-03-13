import streamlit as st
import pandas as pd
from whatstk import df_from_whatsapp
import plotly.express as px
import user_manager as um
import os
import unicodedata
import re

# --- Page Config ---
st.set_page_config(page_title="WhatsApp Insights", layout="wide", initial_sidebar_state="expanded")

# --- Premium CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .card-container {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        margin-top: 10px;
    }
    
    .user-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 30px;
        width: 100%;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 20px;
        text-align: center;
    }
    
    .user-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        background: rgba(255, 255, 255, 1);
    }
    
    .user-name {
        font-weight: 700;
        font-size: 1.4rem;
        color: #111827;
        margin-bottom: 8px;
        word-break: break-word;
    }
    
    .user-count {
        font-size: 1.1rem;
        color: #4b5563;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    
    .status-dot {
        height: 10px;
        width: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }
    
    .dot-green { background-color: #10b981; }
    .dot-orange { background-color: #f59e0b; }
    .dot-red { background-color: #ef4444; }
    
    .category-header {
        margin-top: 25px;
        padding-bottom: 8px;
        border-bottom: 2px solid;
    }
    
    .cat-green { color: #065f46; border-color: #10b981; }
    .cat-orange { color: #92400e; border-color: #f59e0b; }
    .cat-red { color: #991b1b; border-color: #ef4444; }
    </style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def normalize_name(name):
    """Normalize name for robust matching: NFC, lowercase, no emojis, stripped."""
    if not name:
        return ""
    # NFC Normalization to handle characters like 'á' consistently
    name = unicodedata.normalize('NFC', str(name))
    # Remove emojis and special symbols (keeping tildes and standard chars)
    name = re.sub(r'[^\w\s\~]', '', name)
    # Handle the various tilde+space combinations (standard space, narrow no-break space, etc.)
    name = re.sub(r'^\~\s*', '~ ', name)
    return name.lower().strip()

def render_user_card(name, count, color, medal=""):
    display_name = f"{medal} {name}" if medal else name
    dot_class = f"dot-{color}"
    st.markdown(f"""
        <div class="user-card">
            <div class="user-name" title="{display_name}">{display_name}</div>
            <div class="user-count">
                <span class="status-dot {dot_class}"></span>
                {count} mensajes
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- Session State ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'users_to_track' not in st.session_state:
    st.session_state.users_to_track = um.load_users()

# --- Login Logic ---
def login_page():
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.title("🔐 Acceso")
    
    with st.form("login_form"):
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Entrar", width="stretch")
        
        if submit:
            if user == "nico" and password == "nico":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
    
    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.authenticated:
    login_page()
    st.stop()

# --- Title ---
st.title("🚀 WhatsApp Insights Platform")

# --- Sidebar ---
st.sidebar.header("📁 Configuración")
uploaded_file = st.sidebar.file_uploader("Arrastra tu chat (.txt)", type=["txt"])

if uploaded_file:
    with open("temp_chat.txt", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    try:
        df = df_from_whatsapp("temp_chat.txt")
        # Ensure date is datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Date Filter
        min_date = df['date'].min().date()
        max_date = df['date'].max().date()
        
        st.sidebar.subheader("📅 Rango Temporal")
        date_range = st.sidebar.date_input("Filtrar por fecha", [min_date, max_date], min_value=min_date, max_value=max_date)
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
            filtered_df = df.loc[mask]
        else:
            filtered_df = df

        # --- User Management ---
        st.sidebar.subheader("👤 Gestión de Lista")
        new_user = st.sidebar.text_input("Añadir usuario")
        if st.sidebar.button("Añadir") and new_user:
            if new_user not in st.session_state.users_to_track:
                um.add_user(new_user)
                st.session_state.users_to_track = um.load_users()
                st.rerun()

        user_to_remove = st.sidebar.selectbox("Eliminar de la lista", [""] + st.session_state.users_to_track)
        if st.sidebar.button("Eliminar") and user_to_remove:
            um.remove_user(user_to_remove)
            st.session_state.users_to_track = um.load_users()
            st.rerun()

        # --- Dashboard ---
        # 1. Ranking Histórico (Todo el chat)
        full_chat_stats = df['username'].value_counts()
        hist_norm_counts = {}
        for u, c in full_chat_stats.items():
            nu = normalize_name(u)
            hist_norm_counts[nu] = hist_norm_counts.get(nu, 0) + c
        
        top_3_norm = sorted(hist_norm_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        medals_map = {}
        if len(top_3_norm) > 0:
            medals_map[top_3_norm[0][0]] = "🥇"
        if len(top_3_norm) > 1:
            medals_map[top_3_norm[1][0]] = "🥈"
        if len(top_3_norm) > 2:
            medals_map[top_3_norm[2][0]] = "🥉"

        # 2. Usuarios a vigilar
        tracked_users = st.session_state.users_to_track
        norm_tracked = {normalize_name(u): u for u in tracked_users}
        
        # 3. Stats filtradas
        chat_stats_filtered = filtered_df['username'].value_counts().reset_index()
        chat_stats_filtered.columns = ['raw_name', 'messages']
        
        aggregated_stats = {u: 0 for u in tracked_users}
        for _, row in chat_stats_filtered.iterrows():
            norm_raw = normalize_name(row['raw_name'])
            if norm_raw in norm_tracked:
                aggregated_stats[norm_tracked[norm_raw]] += row['messages']
        
        stats = pd.DataFrame(list(aggregated_stats.items()), columns=['username', 'messages'])
        stats = stats.sort_values(by='messages', ascending=False)
        max_msgs = stats['messages'].max() if not stats.empty else 1

        # Clasificación
        green_users = stats[stats['messages'] >= max_msgs * 0.4]
        orange_users = stats[(stats['messages'] < max_msgs * 0.4) & (stats['messages'] > 0)]
        red_users = stats[stats['messages'] == 0]

        tab_summary, tab_details = st.tabs(["📊 Resumen de Actividad", "💬 Mensajes Detallados"])

        with tab_summary:
            def render_group(users, color_key):
                if not users.empty:
                    cols = st.columns(3)
                    for i, (_, row) in enumerate(users.iterrows()):
                        medal = medals_map.get(normalize_name(row['username']), "")
                        with cols[i % 3]:
                            render_user_card(row['username'], row['messages'], color_key, medal)
                else:
                    st.write("Sin usuarios en esta categoría.")

            st.markdown('<h3 class="category-header cat-green">🟢 Alta Actividad</h3>', unsafe_allow_html=True)
            render_group(green_users, "green")

            st.markdown('<h3 class="category-header cat-orange">🟠 Actividad Moderada</h3>', unsafe_allow_html=True)
            render_group(orange_users, "orange")

            st.markdown('<h3 class="category-header cat-red">🔴 Inactividad Detectada</h3>', unsafe_allow_html=True)
            render_group(red_users, "red")

            # Graph
            st.markdown("### 📈 Tendencia General")
            fig = px.bar(stats, x='username', y='messages', color='messages', 
                         color_continuous_scale=['#ef4444', '#f59e0b', '#10b981'],
                         template="plotly_white")
            st.plotly_chart(fig, width='stretch')

        with tab_details:
            st.subheader("🔍 Buscador de Mensajes")
            col_sel, col_info = st.columns([1, 1])
            selected_user = col_sel.selectbox("Seleccionar Usuario", stats['username'].unique())
            
            if selected_user:
                # Normalize for matching
                norm_selected = normalize_name(selected_user)
                user_mask_full = df['username'].apply(lambda x: normalize_name(x) == norm_selected)
                user_messages_all = df[user_mask_full].sort_values(by='date', ascending=False)
                
                # Filtered messages for the dataframe
                u_msgs_filtered = filtered_df[filtered_df['username'].apply(lambda x: normalize_name(x) == norm_selected)][['date', 'message']]
                
                # Get message count from stats
                msg_count = stats[stats['username'] == selected_user]['messages'].values[0]

                from datetime import datetime
                if not user_messages_all.empty:
                    last_msg_date = user_messages_all['date'].max()
                    days_diff = (datetime.now() - last_msg_date).days
                    
                    with col_info:
                        st.markdown(f"""
                            <div style="background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1); text-align: center;">
                                <div style="font-size: 1.6em; font-weight: bold; color: {'#ff4b4b' if days_diff > 30 else '#ffa500' if days_diff > 7 else '#4bff4b'};">
                                    {msg_count} mensajes — {days_diff} días sin hablar
                                </div>
                                <div style="font-size: 0.8em; opacity: 0.5;">Última actividad: {last_msg_date.strftime('%d/%m/%Y')}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    col_info.info("Sin registros históricos.")

                if not u_msgs_filtered.empty:
                    st.dataframe(u_msgs_filtered, width='stretch', height=600)
                else:
                    st.warning("Sin mensajes en el rango de fechas seleccionado.")

    except Exception as e:
        st.error(f"Error de procesamiento: {e}")
    finally:
        if os.path.exists("temp_chat.txt"):
            os.remove("temp_chat.txt")

else:
    st.info("👋 Sube un archivo de WhatsApp para empezar el análisis.")
