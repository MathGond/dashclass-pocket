# DashClass Pocket — Controle de Aulas (Streamlit)

## Rodar localmente
1. Instale Python 3.10+.
2. No terminal, dentro desta pasta:
   - `pip install -r requirements.txt`
   - `streamlit run app.py`

## Publicar online (Streamlit Community Cloud)
1. Crie um repositório no GitHub (ex: `dashclass-pocket`).
2. Envie estes arquivos:
   - `app.py`
   - `requirements.txt`
   - pasta `data/` (pode ir vazia; o app cria se não existir)
3. Acesse https://share.streamlit.io e conecte seu GitHub.
4. Selecione o repo e o arquivo principal `app.py`.
5. Deploy ✅

## Dados
- O progresso fica salvo em `data/progress.json`.
- No Streamlit Cloud, isso funciona como armazenamento do app; para backup use os botões de Exportar CSV.
