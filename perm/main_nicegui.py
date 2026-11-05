import pandas as pd
import plotly.express as px
from nicegui import ui

from perm.analysis import count_by_orbit

# Chargement des données
df = pd.read_csv("data/gp.csv")

NAME = "Name of Satellite, Alternate Names"
COUNTRY = "Country of Operator/Owner"
OPERATOR = "Operator/Owner"
ORBIT = "Class of Orbit"
PERIGEE = "Perigee (km)"
APOGEE = "Apogee (km)"
INCLINATION = "Inclination (degrees)"
NORAD = "NORAD Number"


def create_interface():
    ui.label("Satellite Explorer").classes("text-3xl font-bold")
    ui.label(
        f"Orbital database until 07/10/26 : 12h23 UTC by PC&MD&GPT — {len(df):,} satellites"
    ).classes("text-gray-600")

    ui.separator()

    # --- Filtres ---
    with ui.row().classes("w-full items-end"):
        search = ui.input(
            label="Search satellite", placeholder="ISS, STARLINK, CALSPHERE..."
        ).classes("w-80")

        orbit = ui.select(
            ["All"] + sorted(df[ORBIT].dropna().unique().tolist()),
            value="All",
            label="Orbit",
        ).classes("w-48")

        ui.button("Search", on_click=lambda: update_table())

    ui.separator()

    # --- Répartition des orbites ---
    orbit_counts = count_by_orbit(df)
    fig = px.bar(
        orbit_counts,
        x="orbit",
        y="count",
        labels={"orbit": "Orbit class", "count": "Number of satellites"},
        title="Satellites by orbit class",
    )
    ui.plotly(fig).classes("w-full h-96")

    ui.separator()

    # --- Tableau ---
    columns = [
        {"name": "name", "label": "Satellite", "field": "name", "sortable": True},
        {"name": "country", "label": "Country", "field": "country", "sortable": True},
        {"name": "orbit", "label": "Orbit", "field": "orbit", "sortable": True},
        {
            "name": "perigee",
            "label": "Perigee (km)",
            "field": "perigee",
            "sortable": True,
        },
        {"name": "apogee", "label": "Apogee (km)", "field": "apogee", "sortable": True},
        {
            "name": "inclination",
            "label": "Inclination (°)",
            "field": "inclination",
            "sortable": True,
        },
        {"name": "norad", "label": "NORAD", "field": "norad", "sortable": True},
    ]

    table = ui.table(columns=columns, rows=[], pagination=15).classes("w-full")

    result_label = ui.label()

    def update_table():
        filtered = df.copy()

        # Recherche par nom
        if search.value:
            filtered = filtered[
                filtered[NAME]
                .fillna("")
                .str.contains(search.value, case=False, regex=False)
            ]

        # Filtre par orbite
        if orbit.value != "All":
            filtered = filtered[filtered[ORBIT] == orbit.value]

        # On limite l'affichage
        display = filtered.head(500)

        table.rows = [
            {
                "name": row[NAME],
                "country": row[COUNTRY],
                "orbit": row[ORBIT],
                "perigee": row[PERIGEE],
                "apogee": row[APOGEE],
                "inclination": row[INCLINATION],
                "norad": row[NORAD],
            }
            for _, row in display.iterrows()
        ]

        table.update()

        result_label.text = f"{len(filtered)} satellites found"

    # Premier affichage
    update_table()


create_interface()

ui.run(
    title="Satellite Explorer",
    reload=False,
)
