import streamlit as st
import pandas as pd
import csv
import os

st.set_page_config(page_title="BPMN Prozesspriorisierung", layout="wide")

# Passwortschutz
pw = st.text_input("🔐 Passwort", type="password")
if pw != "pilot":
    st.warning("Zugang nur mit gültigem Passwort.")
    st.stop()

st.title("🏗️ BPMN 2.0 Prozesspriorisierung")

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

# Bestehende Daten laden
df_existing = pd.read_csv(CSV_PATH) if os.path.exists(CSV_PATH) else pd.DataFrame(columns=CSV_HEADERS)

def extract_unique(column):
    return sorted(set(x.strip() for cell in df_existing[column].dropna() for x in str(cell).split(",") if x.strip()))

# Initial Dropdown-Werte
alle_hauptprozesse = sorted(set(df_existing["Hauptprozess"].dropna().unique()))
alle_systeme = extract_unique("Systeme")
alle_personen = sorted(set(extract_unique("Pflichtteilnehmende") + extract_unique("Optionale Teilnehmende")))

st.header("🧩 Neue Prozesseingabe")

with st.form("prozess_formular"):
    hauptprozess = st.selectbox("Hauptprozess auswählen oder neu eingeben", options=[*alle_hauptprozesse, ""])
    neuer_hauptprozess = st.text_input("➕ Neuen Hauptprozess (optional)")
    if neuer_hauptprozess.strip():
        hauptprozess = neuer_hauptprozess.strip()

    unterprozess = st.text_input("🔤 Unterprozessname")
    st.caption("Eindeutig benennen, z. B. 'Freigabe Kundenangebot'.")

    def slider(name, **kwargs):
        col1, col2 = st.columns([2, 3])
        with col1:
            val = st.slider(name, **kwargs)
        with col2:
            st.markdown(f"<div style='color: grey; font-size: 0.85em'>{kwargs['help']}</div>", unsafe_allow_html=True)
        return val
        struktur = slider("📐 Strukturierungsgrad & Entscheidungslogik", min_value=1, max_value=5, value=1,
        help="""
        <b>1</b>: Stark strukturiert, klare Abläufe, hohe Regelklarheit<br>
        <b>2</b>: Gut strukturiert mit kleinen Varianten<br>
        <b>3</b>: Mischform, Regelwerk teils implizit<br>
        <b>4</b>: Schwach strukturiert, viele Varianten<br>
        <b>5</b>: Unstrukturiert, viele manuelle Entscheidungen
        """)

    fehler = slider("⚠️ Fehleranfälligkeit", min_value=1, max_value=5, value=3,
        help="""
        <b>1</b>: Kaum Fehler, leicht erkennbar<br>
        <b>2</b>: Vereinzelte Fehler, gut kontrollierbar<br>
        <b>3</b>: Fehler regelmäßig, Korrektur aufwändig<br>
        <b>4</b>: Größere Tragweite, systemisch<br>
        <b>5</b>: Hohe Fehleranfälligkeit mit Ketteneffekten
        """)

    häufigkeit = slider("📈 Häufigkeit & Volumen", min_value=1, max_value=5, value=3,
        help="""
        <b>1</b>: Täglich, gleichmäßig verteilt<br>
        <b>2</b>: Häufig, mit saisonalen Peaks<br>
        <b>3</b>: Wöchentlich, moderates Volumen<br>
        <b>4</b>: Monatlich oder punktuell<br>
        <b>5</b>: Sehr selten oder Sonderfall
        """)

    ressourcen = slider("👥 Personale Ressourcen & Kollaboration", min_value=1, max_value=5, value=3,
        help="""
        <b>1</b>: Einzelperson, kein Abstimmungsbedarf<br>
        <b>2</b>: Zwei Beteiligte, einfache Übergabe<br>
        <b>3</b>: 3–5 Personen, gelegentlich Abstimmung<br>
        <b>4</b>: >5 Personen, hohe Synchronisation nötig<br>
        <b>5</b>: Viele Stakeholder, hoher Abstimmungsaufwand
        """)

    systeme_count = slider("💻 Systeme & Tools im Prozess", min_value=1, max_value=5, value=3,
        help="""
        <b>1</b>: 1 Tool, voll digital<br>
        <b>2</b>: 2 Tools, gut integrierbar<br>
        <b>3</b>: 3–4 Tools, teilweise Medienbrüche<br>
        <b>4</b>: >4 Tools oder fehlende Schnittstellen<br>
        <b>5</b>: Nur manuell, z. B. Excel, E-Mail
        """)

    komplex = st.number_input("🧮 Komplexitätsfaktor (Basis = 1)", 0.5, 10.0, 1.0, step=0.1)
    dauer = st.number_input("⏱️ Durchlaufzeit (Tage)", min_value=0, value=1, step=1)
    arbeitszeit = st.number_input("🕒 Arbeitszeit gesamt (h)", min_value=0, value=1, step=1)
    aktiv = st.radio("📌 Prozess aktuell in Veränderung?", ["Nein", "Ja"])

    neue_systeme = st.multiselect("🖥️ Beteiligte Systeme", options=alle_systeme, help="Neue oder vorhandene Systeme eingeben")
    neue_personen = st.multiselect("👤 Zwingend Beteiligte Personen", options=alle_personen, help="Personen eingeben oder auswählen", key="pflicht")
    optionale_personen = st.multiselect("👥 Wünschenswerte Personen", options=alle_personen, help="Personen eingeben oder auswählen", key="optional")

    submitted = st.form_submit_button("✅ Prozess speichern")

    if submitted and hauptprozess and unterprozess:
        score = ((struktur * 2) + fehler + häufigkeit + ressourcen + systeme_count) * komplex

        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                hauptprozess, unterprozess, struktur, fehler, häufigkeit,
                ressourcen, systeme_count, komplex, round(score, 2), dauer,
                arbeitszeit, aktiv,
                ", ".join(neue_systeme),
                ", ".join(neue_personen),
                ", ".join(optionale_personen)
            ])

        st.success(f"✅ Prozess '{unterprozess}' wurde gespeichert.")

# Tabelle anzeigen
if os.path.exists(CSV_PATH):
    st.markdown("## 📊 Erfasste Prozesse")
    df = pd.read_csv(CSV_PATH)
    st.dataframe(df.sort_values(by="Score"), use_container_width=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Gesamtexport als CSV", data=csv, file_name="prozesspriorisierung.csv", mime="text/csv")