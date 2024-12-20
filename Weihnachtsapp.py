import streamlit as st
import json
from datetime import datetime, timedelta

# Datei für Speicherung
DATA_FILE = "freundschafts_counter.json"

# Funktionen zur Datenverwaltung
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
            # Konvertiere gespeicherte Strings in datetime-Objekte (falls vorhanden)
            data["last_contact"]["M"] = (
                datetime.strptime(data["last_contact"]["M"], "%Y-%m-%d").date()
                if data["last_contact"]["M"]
                else None
            )
            data["last_contact"]["E"] = (
                datetime.strptime(data["last_contact"]["E"], "%Y-%m-%d").date()
                if data["last_contact"]["E"]
                else None
            )
            return data
    except FileNotFoundError:
        return {
            "M_points": 0,
            "E_points": 0,
            "last_contact": {"M": None, "E": None},
            "history": [],
        }

def save_data(data):
    # Konvertiere datetime-Objekte in Strings, bevor sie gespeichert werden
    data["last_contact"]["M"] = (
        data["last_contact"]["M"].strftime("%Y-%m-%d")
        if data["last_contact"]["M"]
        else None
    )
    data["last_contact"]["E"] = (
        data["last_contact"]["E"].strftime("%Y-%m-%d")
        if data["last_contact"]["E"]
        else None
    )
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def reset_data():
    data = {
        "M_points": 0,
        "E_points": 0,
        "last_contact": {"M": None, "E": None},
        "history": [],
    }
    save_data(data)
    return data

# Daten laden
data = load_data()

# Initiale Werte aus Datei
st.session_state.M_points = data["M_points"]
st.session_state.E_points = data["E_points"]
st.session_state.last_contact = data["last_contact"]
st.session_state.history = data["history"]

# Geburtstage
M_BIRTHDAY = datetime(2024, 8, 23).date()
E_BIRTHDAY = datetime(2024, 10, 27).date()

# Hauptbereich
st.title("🎄 Freundschafts-Counter 🎄")

# Punktestand anzeigen
st.header("Punktestand")
st.metric(label="M 🎅", value=f"{st.session_state.M_points} Punkte")
st.metric(label="E 🎄", value=f"{st.session_state.E_points} Punkte")

# Meldung eintragen
st.header("Meldung eintragen")
with st.form("contact_form"):
    person = st.selectbox("Wer hat sich gemeldet?", ["M 🎅", "E 🎄"])
    date = st.date_input("Wann hat sich die Person gemeldet?", value=datetime.now())
    submit = st.form_submit_button("Eintragen")

# Funktionen
def calculate_days_since(last_date, current_date):
    if not last_date:
        return 0
    return (current_date - last_date).days

def add_points(person, date):
    # Übersetze die Auswahl von "M 🎅" und "E 🎄" zu "M" und "E"
    person = "M" if person == "M 🎅" else "E"

    is_birthday = (person == "M" and date == M_BIRTHDAY) or \
                  (person == "E" and date == E_BIRTHDAY)
    days_since_last_contact = calculate_days_since(
        st.session_state.last_contact[person],
        date
    )
    points = days_since_last_contact + (10 if is_birthday else 0)

    if person == "M":
        st.session_state.M_points += points
    else:
        st.session_state.E_points += points

    st.session_state.last_contact[person] = date

    # Event zur Historie hinzufügen
    st.session_state.history.append({
        "person": person,
        "date": date.strftime("%Y-%m-%d"),
        "points": points,
        "is_birthday": is_birthday
    })

# Eintragung verarbeiten
if submit:
    add_points(person, date)
    # Daten speichern
    save_data({
        "M_points": st.session_state.M_points,
        "E_points": st.session_state.E_points,
        "last_contact": st.session_state.last_contact,
        "history": st.session_state.history
    })
    st.success(f"Punkte für {person} wurden erfolgreich aktualisiert!")
    st.experimental_rerun()

# Historie anzeigen
st.header("Historie")
if st.session_state.history:
    for event in st.session_state.history:
        person = "M 🎅" if event["person"] == "M" else "E 🎄"
        st.write(f"- **{event['date']}**: {person} hat sich gemeldet und **{event['points']} Punkte** erhalten {'🎂 (Geburtstag!)' if event['is_birthday'] else ''}.")
else:
    st.info("Noch keine Meldungen in der Historie.")

# Reset-Funktion
if st.button("🔄 App zurücksetzen"):
    reset_data()
    st.session_state.M_points = 0
    st.session_state.E_points = 0
    st.session_state.last_contact = {"M": None, "E": None}
    st.session_state.history = []
    st.success("App wurde zurückgesetzt!")
    st.experimental_rerun()

# Tipp
st.info("💡 Tipp: Geburtstage bringen Extra-Punkte!")
