import json
import os
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="DashClass Pocket", page_icon="✅", layout="wide")

# -----------------------
# Config
# -----------------------
BIMESTRES = ["1º Bim", "2º Bim", "3º Bim", "4º Bim"]
AULAS_POR_BIM = 10

TURMAS = []
# Filosofia 1º1–1º8
for i in range(1, 9):
    TURMAS.append({"turma": f"1º{i}", "disciplina": "Filosofia"})
# Filosofia 2º1–2º6
for i in range(1, 7):
    TURMAS.append({"turma": f"2º{i}", "disciplina": "Filosofia"})
# Ciências Humanas Aplicadas 1º7 e 1º8
for i in [7, 8]:
    TURMAS.append({"turma": f"1º{i}", "disciplina": "Ciências Humanas Aplicadas"})

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DATA_PATH = os.path.join(DATA_DIR, "progress.json")

def default_data():
    data = {}
    for b in BIMESTRES:
        data[b] = {}
        for t in TURMAS:
            key = f"{t['turma']}|{t['disciplina']}"
            data[b][key] = [False]*AULAS_POR_BIM
    return data

def load_data():
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # Backfill any missing keys (in case of future expansions)
            d = default_data()
            for b in BIMESTRES:
                if b not in raw:
                    continue
                for k, v in raw[b].items():
                    if b in d and k in d[b]:
                        # normalize length
                        vv = (v + [False]*AULAS_POR_BIM)[:AULAS_POR_BIM]
                        d[b][k] = vv
            return d
        except Exception:
            return default_data()
    return default_data()

def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# -----------------------
# UI
# -----------------------
st.title("✅ DashClass Pocket — Controle de Aulas")
st.caption("Marque as aulas dadas por turma e por bimestre. Sem login, simples e direto.")

colA, colB, colC, colD = st.columns([1.2, 1.2, 1.2, 1.6])
with colA:
    st.metric("Turmas (linhas)", len(TURMAS))
with colB:
    st.metric("Aulas / Bimestre", AULAS_POR_BIM)
with colC:
    st.metric("Bimestres", len(BIMESTRES))
with colD:
    st.write("")
    st.write("")
    if st.button("💾 Salvar agora", use_container_width=True):
        save_data(data)
        st.success("Salvo!")

st.divider()

tabs = st.tabs(BIMESTRES)

def turma_label(turma, disciplina):
    return f"{turma} — {disciplina}"

for idx, b in enumerate(BIMESTRES):
    with tabs[idx]:
        left, right = st.columns([2.2, 1])
        with left:
            st.subheader(f"{b} (A1–A{AULAS_POR_BIM})")
            st.caption("Dica: use o teclado (Tab/Shift+Tab) pra navegar rápido entre caixas e marcar com Espaço.")
        with right:
            # quick actions
            st.write("")
            st.write("")
            if st.button(f"🧹 Zerar {b}", key=f"reset_{b}", use_container_width=True):
                for t in TURMAS:
                    k = f"{t['turma']}|{t['disciplina']}"
                    data[b][k] = [False]*AULAS_POR_BIM
                save_data(data)
                st.warning(f"{b} zerado.")
            if st.button(f"📤 Exportar {b} (CSV)", key=f"export_{b}", use_container_width=True):
                # build a flat table for export
                rows = []
                for t in TURMAS:
                    k = f"{t['turma']}|{t['disciplina']}"
                    aulas = data[b][k]
                    row = {"Turma": t["turma"], "Disciplina": t["disciplina"]}
                    for a in range(1, AULAS_POR_BIM+1):
                        row[f"Aula {a}"] = "OK" if aulas[a-1] else ""
                    rows.append(row)
                import pandas as pd
                df = pd.DataFrame(rows)
                csv = df.to_csv(index=False).encode("utf-8-sig")
                st.download_button("Baixar CSV", data=csv, file_name=f"dashclass_{b.replace('º','').replace(' ','_')}.csv", mime="text/csv", use_container_width=True)

        st.divider()

        # Group by disciplina
        disciplinas = sorted(list({t["disciplina"] for t in TURMAS}))
        for disc in disciplinas:
            st.markdown(f"### {disc}")
            subset = [t for t in TURMAS if t["disciplina"] == disc]

            # header row
            hdr_cols = st.columns([1.6] + [0.55]*AULAS_POR_BIM)
            hdr_cols[0].markdown("**Turma**")
            for a in range(1, AULAS_POR_BIM+1):
                hdr_cols[a].markdown(f"**A{a}**")

            # rows
            for t in subset:
                row_cols = st.columns([1.6] + [0.55]*AULAS_POR_BIM)
                row_cols[0].write(t["turma"])
                k = f"{t['turma']}|{t['disciplina']}"
                for a in range(1, AULAS_POR_BIM+1):
                    ck_key = f"{b}|{k}|A{a}"
                    current = data[b][k][a-1]
                    new_val = row_cols[a].checkbox("", value=current, key=ck_key)
                    if new_val != current:
                        data[b][k][a-1] = new_val
                        # autosave on change
                        save_data(data)

        st.divider()
        # summary
        total = 0
        done = 0
        for t in TURMAS:
            k = f"{t['turma']}|{t['disciplina']}"
            total += AULAS_POR_BIM
            done += sum(1 for x in data[b][k] if x)
        pct = (done/total*100) if total else 0
        st.info(f"Progresso do {b}: **{done} / {total}** aulas marcadas (**{pct:.1f}%**).")

st.caption(f"Última atualização local: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
