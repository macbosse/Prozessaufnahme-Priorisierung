import streamlit as st
import pandas as pd

st.set_page_config(page_title="BPMN Prozesspriorisierung", layout="wide")
st.title("🏗️ BPMN 2.0 Prozesspriorisierungstool")

# Session init
if "prozesse" not in st.session_state:
    st.session_state["prozesse"] = []
if "alle_personen" not in st.session_state:
    st.session_state["alle_personen"] = set()
if "alle_systeme" not in st.session_state:
    st.session_state["alle_systeme"] = set()
if "alle_hauptprozesse" not in st.session_state:
    st.session_state["alle_hauptprozesse"] = set()

with st.form("prozess_formular"):
    st.header("🧩 Prozessstruktur")
    hauptprozesse_liste = sorted(list(st.session_state["alle_hauptprozesse"])) or [""]
    hauptprozess = st.selectbox("Hauptprozess auswählen oder neu eingeben", hauptprozesse_liste, index=0)
    neuer_hauptprozess = st.text_input("➕ Neuen Hauptprozess eintragen (optional)", "")

    if neuer_hauptprozess.strip():
        hauptprozess = neuer_hauptprozess.strip()
        st.session_state["alle_hauptprozesse"].add(hauptprozess)

    unterprozess = st.text_input("🔤 Unterprozessname")
    st.caption("Bitte eindeutig benennen, z. B. 'Freigabe Kundenangebot'.")

    st.markdown("---")

    def slider_with_help(label, slider_kwargs, help_texts):
        col1, col2 = st.columns([2, 3])
        with col1:
            value = st.slider(label, **slider_kwargs)
        with col2:
            st.markdown(
                f"<div style='color: grey; font-size: 0.85em; line-height: 1.4;'>{help_texts}</div>",
                unsafe_allow_html=True
            )
        return value

    struktur = slider_with_help(
        "📐 Strukturierungsgrad",
        {"min_value": 1, "max_value": 5, "value": 1},
        """
        <strong>Bewertung:</strong><br>
        1 = Stark strukturiert: klare Abläufe, wenige Ausnahmen, hohe Regelklarheit<br>
        2 = Gut strukturiert mit kleineren Varianten<br>
        3 = Teilweise strukturiert, einige implizite Regeln<br>
        4 = Schwach strukturiert, viele Ausnahmen<br>
        5 = Unstrukturiert, individuell, kaum definierte Regeln
        """
    )

    fehler = slider_with_help(
        "⚠️ Fehleranfälligkeit",
        {"min_value": 1, "max_value": 5, "value": 3},
        """
        <strong>Bewertung:</strong><br>
        1 = Fehler sind selten, sofort sichtbar, leicht korrigierbar<br>
        2 = Kleinere Fehler möglich, gut kontrollierbar<br>
        3 = Regelmäßige Fehler, mit Aufwand behebbar<br>
        4 = Fehler haben große Tragweite, oft systemisch<br>
        5 = Hohe Fehleranfälligkeit mit gravierenden Folgen
        """
    )

    häufigkeit = slider_with_help(
        "📈 Häufigkeit & Volumen",
        {"min_value": 1, "max_value": 5, "value": 3},
        """
        <strong>Bewertung:</strong><br>
        1 = Sehr häufig (täglich, viele Durchläufe), konstant<br>
        2 = Häufig mit saisonalen Spitzen<br>
        3 = Wöchentlich oder mäßiges Volumen<br>
        4 = Monatlich oder unregelmäßig<br>
        5 = Selten oder nur bei Bedarf
        """
    )

    ressourcen = slider_with_help(
        "👥 Beteiligte Ressourcen",
        {"min_value": 1, "max_value": 5, "value": 3},
        """
        <strong>Bewertung:</strong><br>
        1 = Einzelperson oder klar sequenziell<br>
        2 = Zwei Beteiligte, einfache Übergaben<br>
        3 = 3–5 Personen, gelegentliche Abstimmung<br>
        4 = >5 Personen, paralleles Arbeiten mit Reibung<br>
        5 = Viele Beteiligte, hohe Abstimmungsnotwendigkeit
        """
    )

    systeme_count = slider_with_help(
        "💻 Systemvielfalt",
        {"min_value": 1, "max_value": 5, "value": 3},
        """
        <strong>Bewertung:</strong><br>
        1 = Ein Tool, voll digitalisiert mit API<br>
        2 = Zwei Systeme, gut integrierbar<br>
        3 = 3–4 Tools, teilweise Medienbrüche<br>
        4 = Viele Tools, manuelle Übergaben<br>
        5 = Keine digitalen Tools, rein manuell
        """
    )

    st.markdown("---")

    komplex = st.number_input("🧮 Komplexitätsfaktor vs. Gehaltsprozess", 0.5, 10.0, 1.0, step=0.1,
        help="1.0 entspricht dem Basisprozess 'Gehaltscheck'")
    dauer = st.number_input("⏱️ Durchlaufzeit (Tage)", min_value=0, value=1, step=1,
        help="Gesamtdauer vom Start bis Abschluss eines Prozessdurchlaufs")
    arbeitszeit = st.number_input("🕒 Menschliche Arbeitszeit (Stunden)", min_value=0, value=1, step=1,
        help="Manuelle Zeit aller Beteiligten in Summe (geschätzt)")

    aktiv_veraenderung = st.radio("📌 Ist der Prozess aktuell in Veränderung?", ["Nein", "Ja"],
        help="Ist der Prozess gerade in Überarbeitung oder wird er neu gedacht?")

    neue_systeme = st.multiselect(
        "🖥️ Beteiligte Systeme",
        options=sorted(list(st.session_state["alle_systeme"])) or [""],
        help="Bestehende auswählen oder neue Systeme eintippen und bestätigen"
    )
    for s in neue_systeme:
        st.session_state["alle_systeme"].add(s)

    pflicht = st.multiselect(
        "👤 Zwingend Beteiligte Personen",
        options=sorted(list(st.session_state["alle_personen"])) or [""],
        help="Personen, die bei der Prozessaufnahme unbedingt anwesend sein müssen",
        key="pflicht"
    )
    for p in pflicht:
        st.session_state["alle_personen"].add(p)

    optional = st.multiselect(
        "👥 Wünschenswerte Beteiligte Personen",
        options=sorted(list(st.session_state["alle_personen"])) or [""],
        help="Personen, die wünschenswert wären, aber nicht zwingend erforderlich sind",
        key="optional"
    )
    for o in optional:
        st.session_state["alle_personen"].add(o)

    submitted = st.form_submit_button("✅ Prozess speichern")

    if submitted and hauptprozess.strip() and unterprozess.strip():
        score = ((struktur * 2) + fehler + häufigkeit + ressourcen + systeme_count) * komplex
        st.session_state.prozesse.append({
            "Hauptprozess": hauptprozess,
            "Unterprozess": unterprozess,
            "Struktur": struktur,
            "Fehleranfälligkeit": fehler,
            "Häufigkeit": häufigkeit,
            "Ressourcen": ressourcen,
            "Systemvielfalt": systeme_count,
            "Komplexitätsfaktor": komplex,
            "Score": round(score, 2),
            "Durchlaufzeit (Tage)": dauer,
            "Arbeitszeit (h)": arbeitszeit,
            "Aktiv in Veränderung": aktiv_veraenderung,
            "Systeme": ", ".join(neue_systeme),
            "Pflichtteilnehmende": ", ".join(pflicht),
            "Optionale Teilnehmende": ", ".join(optional)
        })
        st.success(f"✅ Prozess '{unterprozess}' gespeichert unter '{hauptprozess}'.")

# Ergebnisanzeige
if st.session_state.prozesse:
    st.header("📊 Übersicht & Priorisierung")
    df = pd.DataFrame(st.session_state.prozesse)
    df_sorted = df.sort_values(by="Score", ascending=True).reset_index(drop=True)
    st.dataframe(df_sorted, use_container_width=True)

    csv = df_sorted.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Export als CSV", data=csv, file_name="prozesspriorisierung.csv", mime="text/csv")