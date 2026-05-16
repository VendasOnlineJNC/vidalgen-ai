# VidalGen AI - Batch Video Generator

Este é um gerador de vídeos cinematográficos movido por IA (Stable Video Diffusion), desenvolvido para processamento em lote.

## 🚀 Como Executar Localmente

1. **Clone o repositório:**
   ```bash
   git clone <seu-repositorio>
   cd <pasta-do-projeto>
   ```

2. **Crie um ambiente virtual (recomendado):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as credenciais:**
   - Renomeie `.env.example` para `.env`
   - Adicione seu `REPLICATE_API_TOKEN` (Obtenha em [replicate.com](https://replicate.com/account))

5. **Execute o app:**
   ```bash
   streamlit run app.py
   ```

## ☁️ Deploy no Streamlit Cloud

1. Suba este código para um repositório no seu **GitHub**.
2. Acesse [share.streamlit.io](https://share.streamlit.io).
3. Conecte seu repositório.
4. **IMPORTANTE:** Vá em "Settings" > "Secrets" e adicione sua chave:
   ```toml
   REPLICATE_API_TOKEN = "sua_chave_aqui"
   ```
5. Clique em **Deploy**!

## 🛠️ Tecnologias
- [Streamlit](https://streamlit.io/) - Interface Frontend
- [Replicate](https://replicate.com/) - Processamento de IA (SVD)
- [Pillow](https://python-pillow.org/) - Compressão de Imagens

---
© 2024 VidalGen AI. Powered by Replicate & Streamlit
