import streamlit as st
import requests
import time
import base64
import io
from PIL import Image

# --- 🚀 INSTRUÇÕES DE DEPLOY NO STREAMLIT CLOUD ---
# 1. Crie um repositório no GitHub e envie este arquivo como 'streamlit_app.py'.
# 2. Crie um arquivo 'requirements.txt' com: streamlit, requests, Pillow
# 3. No dashboard do Streamlit Cloud, em 'Advanced Settings' > 'Secrets', adicione:
#    FAL_API_KEY = "sua_chave_fal_ai_aqui"
# ------------------------------------------------

# Configuração da Página
st.set_page_config(
    page_title="VidalGen AI - Powered by Fal.ai",
    page_icon="🎬",
    layout="wide"
)

# Estilização PRECIFICA+ (Dark Mode Professional)
st.markdown("""
<style>
    /* Cores Principais */
    :root {
        --main-bg: #10141d;
        --card-bg: #1a1f2e;
        --accent-primary: #FF6B35; /* Laranja */
        --accent-secondary: #00D4FF; /* Azul Elétrico */
        --accent-special: #8B5CF6; /* Roxo */
    }

    .stApp {
        background-color: var(--main-bg);
        color: #ffffff;
    }

    /* Esconder menu padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Cards Personalizados */
    .precifica-card {
        background-color: var(--card-bg);
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    /* Botão Primário (Laranja) */
    div.stButton > button:first-child {
        background-color: var(--accent-primary);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 800;
        text-transform: uppercase;
        font-style: italic;
        width: 100%;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        filter: brightness(1.2);
        box-shadow: 0 0 20px rgba(255, 107, 53, 0.4);
        transform: translateY(-2px);
    }

    /* Botão de Download (Roxo) */
    div.stDownloadButton > button:first-child {
        background-color: var(--accent-special);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 800;
        text-transform: uppercase;
        font-style: italic;
        width: 100%;
    }
    
    /* Inputs */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: rgba(255,255,255,0.05) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# Título Principal
st.markdown("<h1 style='text-align: center; font-weight: 900; font-style: italic; text-transform: uppercase; letter-spacing: -2px; font-size: 3rem;'>🎬 VidalGen AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; font-size: 1.1rem; margin-bottom: 3rem;'>Transforme imagens em vídeos cinematográficos com o poder do <b>Fal.ai + Pika</b>.</p>", unsafe_allow_html=True)

# Verificação de API Key
if "FAL_API_KEY" not in st.secrets:
    st.error("⚠️ Chave de API `FAL_API_KEY` não encontrada nas configurações do Streamlit Cloud.")
    st.stop()

FAL_API_KEY = st.secrets["FAL_API_KEY"]
FAL_API_URL = "https://fal.run/fal-ai/pika/v1.0/image-to-video"

def get_image_base64(image_file):
    """Converte o arquivo de imagem em uma string base64 para o Fal.ai"""
    encoded_string = base64.b64encode(image_file.getvalue()).decode()
    mime_type = image_file.type
    return f"data:{mime_type};base64,{encoded_string}"

# Layout em Colunas
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("<div class='precifica-card'>", unsafe_allow_html=True)
    st.subheader("🖼️ Upload da Imagem")
    upload_file = st.file_uploader("Arraste ou selecione sua imagem (PNG/JPG)", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    
    if upload_file:
        st.image(upload_file, caption="Preview da Imagem", use_container_width=True)
        
        st.subheader("⚙️ Configurações")
        duracao = st.selectbox("Duração do Vídeo", ["15 segundos", "30 segundos"])
        prompt_custom = st.text_input("Prompt de Movimento", "smooth cinematic camera movement, high detail, realistic")
        
        if st.button("🚀 Criar Vídeo Agora"):
            # Lógica de Geração
            with col2:
                with st.status("🔮 Inteligência Artificial processando...", expanded=True) as status:
                    try:
                        st.write("Preparando imagem e enviando para Fal.ai...")
                        img_base64 = get_image_base64(upload_file)
                        
                        headers = {
                            "Authorization": f"Key {FAL_API_KEY}",
                            "Content-Type": "application/json"
                        }
                        
                        payload = {
                            "image_url": img_base64,
                            "prompt": prompt_custom
                        }
                        
                        # Chamada para Fal.ai (Endpoint .run é geralmente síncrono para tarefas curtas)
                        response = requests.post(FAL_API_URL, json=payload, headers=headers, timeout=300)
                        
                        if response.status_code == 200:
                            data = response.json()
                            video_url = data.get("video", {}).get("url")
                            
                            if video_url:
                                status.update(label="✅ Vídeo Gerado com Sucesso!", state="complete")
                                st.video(video_url)
                                
                                # Botão de Download
                                video_bytes = requests.get(video_url).content
                                st.download_button(
                                    label="⬇️ Baixar Vídeo MP4",
                                    data=video_bytes,
                                    file_name="video_vidalgen_ai.mp4",
                                    mime="video/mp4"
                                )
                            else:
                                st.error("A API não retornou uma URL de vídeo válida.")
                        else:
                            st.error(f"Erro na API ({response.status_code}): {response.text}")
                            
                    except Exception as e:
                        st.error(f"Falha na comunicação com Fal.ai: {str(e)}")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if not upload_file:
        st.markdown("<div class='precifica-card' style='height: 400px; display: flex; align-items: center; justify-content: center; border-style: dashed; opacity: 0.5;'>", unsafe_allow_html=True)
        st.write("Aguardando upload da imagem para iniciar a magia...")
        st.markdown("</div>", unsafe_allow_html=True)
    elif "video_url" not in locals():
        st.markdown("<div class='precifica-card' style='height: 400px; display: flex; align-items: center; justify-content: center; opacity: 0.3;'>", unsafe_allow_html=True)
        st.write("Pressione o botão para gerar o resultado.")
        st.markdown("</div>", unsafe_allow_html=True)

# Rodapé
st.markdown("---")
st.markdown("<p style='text-align: center; color: #555; font-size: 0.8rem;'>DESIGN BY PRECIFICA+ STYLE | POWERED BY FAL.AI PIKA</p>", unsafe_allow_html=True)
