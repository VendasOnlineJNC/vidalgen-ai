import streamlit as st
import replicate
import os
import requests
import base64
import time
import zipfile
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="VidalGen AI - Batch Video Generator",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS for VidalGen Branding (Navy + Orange)
st.markdown("""
<style>
    .main {
        background-color: #020617;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #F97316;
        color: white;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #EA580C;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
    }
    .stTextInput>div>div>input {
        background-color: #1E293B;
        color: white;
        border: 1px solid #334155;
    }
    .img-preview-card {
        background-color: #1E293B;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        border: 1px solid #334155;
    }
    .status-text {
        font-size: 0.85em;
        font-weight: 500;
    }
    .footer {
        text-align: center;
        padding: 20px;
        color: #94A3B8;
        font-size: 0.8em;
        margin-top: 50px;
        border-top: 1px solid #1E293B;
    }
</style>
""", unsafe_allow_html=True)

# Helper: Individual Image Compression
def process_and_compress(image_source):
    """
    Compresses image to ensure it stays below 400KB final size.
    Targets ~300KB file size to account for Base64 overhead.
    """
    try:
        img = Image.open(image_source)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        # SVD works best with 768px or 1024px
        img.thumbnail((768, 768), Image.Resampling.LANCZOS)
        
        quality = 80
        while True:
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=quality, optimize=True)
            size_kb = len(buffer.getvalue()) / 1024
            if size_kb <= 300 or quality <= 15:
                break
            quality -= 5
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return None

def to_base64_uri(image_bytes):
    return f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}"

# --- STATE MANAGEMENT ---
if 'batch_images' not in st.session_state:
    st.session_state.batch_images = []

def add_to_batch(data, name):
    if len(st.session_state.batch_images) >= 5:
        st.toast("⚠️ Limite de 5 imagens atingido!", icon="🚫")
        return False
    st.session_state.batch_images.append({
        "id": f"{time.time()}_{name}",
        "data": data, # Base64 or URL
        "name": name,
        "status": "Aguardando",
        "result": None,
        "error": None
    })
    return True

# --- LAYOUT: HEADER ---
st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="color: #F8FAFC; margin-bottom: 0;">🎬 Gerador de Vídeo IA</h1>
    <p style="color: #94A3B8; font-size: 1.2em; margin-top: 10px;">
        Transforme suas imagens estáticas em obras de arte cinematográficas em minutos.
    </p>
</div>
""", unsafe_allow_html=True)

# --- LAYOUT: SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configurações")
    replicate_token = st.text_input("Replicate API Token", type="password", value=os.getenv("REPLICATE_API_TOKEN", ""))
    
    st.divider()
    aspect_ratio = st.selectbox("Formato do Vídeo", ["1:1 (Quadrado)", "9:16 (Stories/Reels)"])
    video_duration = st.selectbox("Duração", ["14 Frames (Padrão)", "25 Frames (Extendido)"])
    
    st.divider()
    if st.button("🗑️ Limpar Galeria"):
        st.session_state.batch_images = []
        st.rerun()

# --- LAYOUT: MAIN CONTENT ---
col_upload, col_generation = st.columns([1, 1], gap="large")

with col_upload:
    st.markdown("### 1. Seleção de Imagens (2 a 5)")
    
    tab_files, tab_urls = st.tabs(["📁 Arquivos Locais", "🔗 URLs Externas"])
    
    with tab_files:
        files = st.file_uploader("Upload de Imagens (JPG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        if files:
            for f in files:
                if not any(img['name'] == f.name for img in st.session_state.batch_images):
                    with st.spinner(f"Processando {f.name}..."):
                        c_bytes = process_and_compress(f)
                        if c_bytes:
                            add_to_batch(to_base64_uri(c_bytes), f.name)
            st.success(f"Galeria atualizada com sucesso.")

    with tab_urls:
        with st.form("add_url_form", clear_on_submit=True):
            u_input = st.text_input("URL da Imagem")
            u_name = st.text_input("Apelido da Imagem (Opcional)")
            if st.form_submit_button("➕ Adicionar à Lista"):
                if u_input:
                    add_to_batch(u_input, u_name or f"URL_{len(st.session_state.batch_images)+1}")
                    st.rerun()

    # REVIEW LIST
    if st.session_state.batch_images:
        st.markdown(f"#### 🖼️ Lista de Produção ({len(st.session_state.batch_images)}/5)")
        for idx, item in enumerate(st.session_state.batch_images):
            with st.container():
                st.markdown(f'<div class="img-preview-card">', unsafe_allow_html=True)
                p_col1, p_col2, p_col3 = st.columns([1, 4, 1])
                with p_col1:
                    st.image(item['data'], width=60)
                with p_col2:
                    st.write(f"**{item['name']}**")
                    status_color = "#94A3B8"
                    if item['result']: status_color = "#10B981"
                    elif "Erro" in item['status']: status_color = "#EF4444"
                    st.markdown(f'<span class="status-text" style="color:{status_color}">● {item["status"]}</span>', unsafe_allow_html=True)
                with p_col3:
                    if st.button("✕", key=f"del_{item['id']}"):
                        st.session_state.batch_images.pop(idx)
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Nenhuma imagem selecionada. Faça o upload ou adicione URLs à esquerda.")

with col_generation:
    st.markdown("### 2. Gerar Vídeos")
    instructions = st.text_area("Instruções de Movimento (Opcional)", placeholder="Ex: slow motion zoom, side panning camera...")
    
    st.divider()
    
    batch_ready = [i for i in st.session_state.batch_images if not i['result']]
    run_btn = st.button("🚀 GERAR VÍDEOS EM LOTE", disabled=(len(st.session_state.batch_images) == 0 or len(batch_ready) == 0))
    
    if run_btn:
        if not replicate_token:
            st.error("Token do Replicate é obrigatório na barra lateral.")
        else:
            try:
                os.environ["REPLICATE_API_TOKEN"] = replicate_token
                
                # Model Settings
                v_len = "25_frames_with_svd_xt" if "25" in video_duration else "14_frames_with_svd"
                sizing = "crop_to_9_16" if "9:16" in aspect_ratio else "maintain_aspect_ratio"
                
                prog_bar = st.progress(0)
                master_status = st.empty()
                
                for i, img_obj in enumerate(st.session_state.batch_images):
                    if img_obj['result']: continue # Skip already done
                    
                    master_status.info(f"Produzindo: {img_obj['name']} ({i+1}/{len(st.session_state.batch_images)})")
                    st.session_state.batch_images[i]['status'] = "Enviando..."
                    
                    # Call API
                    prediction = replicate.predictions.create(
                        version="3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
                        input={
                            "input_image": img_obj['data'],
                            "video_length": v_len,
                            "sizing_strategy": sizing,
                            "motion_bucket_id": 127,
                            "cond_aug": 0.02,
                            "frames_per_second": 6
                        }
                    )
                    
                    # Polling
                    while prediction.status not in ["succeeded", "failed", "canceled"]:
                        time.sleep(4)
                        prediction.reload()
                        st.session_state.batch_images[i]['status'] = f"Processando ({prediction.status})..."
                        
                    if prediction.status == "succeeded":
                        video_url = prediction.output[0] if isinstance(prediction.output, list) else prediction.output
                        st.session_state.batch_images[i]['result'] = video_url
                        st.session_state.batch_images[i]['status'] = "Concluído"
                    else:
                        st.session_state.batch_images[i]['status'] = "Erro na Geração"
                        st.session_state.batch_images[i]['error'] = prediction.error
                    
                    prog_bar.progress((i+1) / len(st.session_state.batch_images))
                
                master_status.success("✨ Lote Finalizado!")
                st.rerun()
                
            except Exception as e:
                st.error(f"Falha na conexão com Replicate: {str(e)}")

    # --- RESULTS GALLERY ---
    results_list = [i for i in st.session_state.batch_images if i['result']]
    if results_list:
        st.divider()
        st.markdown(f"### 📥 Galeria de Vídeos ({len(results_list)})")
        
        # Batch Download ZIP
        if len(results_list) > 1:
            zip_mem = BytesIO()
            with zipfile.ZipFile(zip_mem, 'w') as zf:
                for idx, res in enumerate(results_list):
                    content = requests.get(res['result']).content
                    zf.writestr(f"vidalgen_video_{idx+1}.mp4", content)
            
            st.download_button(
                "📦 BAIXAR TODOS OS VÍDEOS (ZIP)",
                data=zip_mem.getvalue(),
                file_name="vidalgen_batch_videos.zip",
                mime="application/zip",
                use_container_width=True
            )
        
        # Individual results
        for idx, res in enumerate(results_list):
            with st.expander(f"Vídeo de: {res['name']}", expanded=True):
                st.video(res['result'])
                st.download_button(
                    label="Baixar Vídeo",
                    data=requests.get(res['result']).content,
                    file_name=f"vidalgen_{idx+1}.mp4",
                    mime="video/mp4",
                    key=f"dl_single_{res['id']}"
                )

# FOOTER
st.markdown("""
<div class="footer">
    © 2024 VidalGen AI. Powered by Replicate & Streamlit<br>
    Batch Video Generator Engine v1.0
</div>
""", unsafe_allow_html=True)
