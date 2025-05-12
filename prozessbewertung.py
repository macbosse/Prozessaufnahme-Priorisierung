import streamlit as st
import pandas as pd
import csv
import os

# ✅ Passwortschutz
pw = st.text_input("🔐 Passwort", type="password")
if pw != "pilot":
    st.warning("Zugang nur mit gültigem Passwort.")
    st.stop()

st.set_page_config(page_title="BPMN Prozesspriorisierung", layout="wide")
st.title("🏗️ BPMN 2.0 Prozesspriorisierung")

# Session State für Dropdowns
if "alle_personen" not in st.session_state:
    st.session_state["alle_personen"] = set()
if "alle_systeme" not in st.session_state:
    st.session_state["alle_systeme"] = set()
if "alle_hauptprozesse" not in st.session_state:
    st.session_state["alle_hauptprozesse"] = set()

st.header("🧩 Neue Prozesseingabe")

# CSV-Datei initialisieren
CSV_PATH = "data.csv"
CSV_HEADERS = [
    "Hauptprozess", "Unterprozess", "Struktur", "Fehleranfälligkeit", "Häufigkeit",
    "Ressourcen", "Systemvielfalt", "Komplexitätsfaktor", "Score",
    "Durchlaufzeit (Tage)", "Arbeitszeit (h)", "Aktiv in Veränderung",
    "Systeme", "Pflichtteilnehmende", "Optionale Teilnehmende"
]

if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)

with st.form("prozess_formular"):
    hauptprozesse_liste = sorted(list(st.session_state["alle_hauptprozesse"])) or [""]
    hauptprozess = st.selectbox("Hauptprozess auswählen oder neu eingeben", hauptprozesse_liste)
    neuer_hauptprozess = st.text_input("➕ Neuen Hauptprozess (optional)")
    if neuer_hauptprozess.strip():
        hauptprozess = neuer_hauptprozess.strip()
        st.session_state["alle_hauptprozesse"].add(hauptprozess)

    unterprozess = st.text_input("🔤 Unterprozessname")
    st.caption("Eindeutig benennen, z. B. 'Freigabe Kundenangebot'.")

    def slider(name, **kwargs):
        col1, col2 = st.columns([2, 3])
        with col1:
            val = st.slider(name, **kwargs)
        with col2:
            st.markdown(f"<div style='color: grey; font-size: 0.85em'>{kwargs['help']}</div>", unsafe_allow_html=True)
        return val

    struktur = slider("📐 Strukturierungsgrad", min_value=1, max_value=5, value=1,
                      help="1 = stark strukturiert, 5 = unstrukturiert, viele Ausnahmen")
    fehler = slider("⚠️ Fehleranfälligkeit", min_value=1, max_value=5, value=3,
                    help="1 = seltene, gut erkennbare Fehler; 5 = gravierende Fehler")
    häufigkeit = slider("📈 Häufigkeit & Volumen", min_value=1, max_value=5, value=3,
                        help="1 = täglich, 5 = selten")
    ressourcen = slider("👥 Beteiligte Ressourcen", min_value=1, max_value=5, value=3,
                        help="1 = Einzelperson, 5 = viele synchron Beteiligte")
    systeme_count = slider("💻 Systemvielfalt", min_value=1, max_value=5, value=3,
                           help="1 = 1 Tool mit API, 5 = viele Tools ohne Schnittstellen")

    komplex = st.number_input("🧮 Komplexitätsfaktor (Basis = 1)", 0.5, 10.0, 1.0, step=0.1)
    dauer = st.number_input("⏱️ Durchlaufzeit (Tage)", min_value=0, value=1, step=1)
    arbeitszeit = st.number_input("🕒 Arbeitszeit gesamt (h)", min_value=0, value=1, step=1)
    aktiv = st.radio("📌 Prozess aktuell in Veränderung?", ["Nein", "Ja"])

    neue_systeme = st.multiselect("🖥️ Beteiligte Systeme", sorted(st.session_state["alle_systeme"]) or [""])
    for s in neue_systeme:
        st.session_state["alle_systeme"].add(s)

    pflicht = st.multiselect("👤 Zwingend Beteiligte Personen", sorted(st.session_state["alle_personen"]) or [""], key="pflicht")
    optional = st.multiselect("👥 Wünschenswerte Personen", sorted(st.session_state["alle_personen"]) or [""], key="optional")
    for p in pflicht + optional:
        st.session_state["alle_personen"].add(p)

    submitted = st.form_submit_button("✅ Prozess speichern")

    if submitted and hauptprozess and unterprozess:
        score = ((struktur * 2) + fehler + häufigkeit + ressourcen + systeme_count) * komplex

        # CSV schreiben
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                hauptprozess, unterprozess, struktur, fehler, häufigkeit,
                ressourcen, systeme_count, komplex, round(score, 2), dauer,
                arbeitszeit, aktiv, ", ".join(neue_systeme),
                ", ".join(pflicht), ", ".join(optional)
            ])

        st.success(f"✅ Prozess '{unterprozess}' wurde gespeichert.")

# Zeige Tabelle
if os.path.exists(CSV_PATH):
    st.markdown("## 📊 Erfasste Prozesse")
    df = pd.read_csv(CSV_PATH)
    st.dataframe(df.sort_values(by="Score"), use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Gesamtexport als CSV", data=csv, file_name="prozesspriorisierung.csv", mime="text/csv")