
import math

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from nicegui import ui

from perm.analysis import count_by_orbit


# ============================================================
# 1. CHARGEMENT DES DONNEES
# ============================================================

df = pd.read_csv("data/gp.csv")

NAME = "Name of Satellite, Alternate Names"
COUNTRY = "Country of Operator/Owner"
OPERATOR = "Operator/Owner"
ORBIT = "Class of Orbit"
PERIGEE = "Perigee (km)"
APOGEE = "Apogee (km)"
INCLINATION = "Inclination (degrees)"
PERIOD = "Period (minutes)"
ECCENTRICITY = "Eccentricity"
NORAD = "NORAD Number"

EARTH_RADIUS = 6371  # Rayon moyen de la Terre en km


# ============================================================
# 2. FONCTIONS UTILITAIRES
# ============================================================

def clean_id(value):
    """Convertit un identifiant NORAD en chaîne propre."""
    try:
        number = float(value)
        if number.is_integer():
            return str(int(number))
    except (ValueError, TypeError):
        pass

    return str(value).strip()


def display_value(value, unit=""):
    """Affiche une valeur sans montrer les NaN."""
    if pd.isna(value):
        return "Inconnu"

    if isinstance(value, (int, float, np.integer, np.floating)):
        return f"{value:,.2f} {unit}".strip()

    return str(value)


def get_satellite(norad):
    """Retrouve un satellite grâce à son numéro NORAD."""
    matches = df[
        df[NORAD].apply(clean_id) == clean_id(norad)
    ]

    if matches.empty:
        return None

    return matches.iloc[0]


# ============================================================
# 3. CREATION DU GLOBE 3D ET DE L'ORBITE
# ============================================================
def create_orbit_figure(row):

    # Récupération des informations
    perigee = pd.to_numeric(row[PERIGEE], errors="coerce")
    apogee = pd.to_numeric(row[APOGEE], errors="coerce")
    inclination = pd.to_numeric(row[INCLINATION], errors="coerce")

    if pd.isna(perigee) or pd.isna(apogee) or pd.isna(inclination):
        return None

    # Distances depuis le centre de la Terre
    rp = EARTH_RADIUS + float(perigee)
    ra = EARTH_RADIUS + float(apogee)

    if rp <= 0 or ra <= 0 or ra < rp:
        return None

    # Paramètres de l'ellipse
    a = (rp + ra) / 2
    eccentricity = (ra - rp) / (ra + rp)
    b = a * math.sqrt(1 - eccentricity**2)

    inclination_rad = math.radians(float(inclination))

    fig = go.Figure()

    # ========================================================
    # 1. SPHERE TERRESTRE
    # ========================================================

    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 60)

    x_earth = EARTH_RADIUS * np.outer(np.cos(u), np.sin(v))
    y_earth = EARTH_RADIUS * np.outer(np.sin(u), np.sin(v))
    z_earth = EARTH_RADIUS * np.outer(
        np.ones(np.size(u)), np.cos(v)
    )

    fig.add_trace(go.Surface(
        x=x_earth,
        y=y_earth,
        z=z_earth,
        colorscale=[
            [0, "#061b35"],
            [0.5, "#0879b9"],
            [1, "#55b9e8"],
        ],
        showscale=False,
        opacity=1,
        name="Earth",
        hoverinfo="skip",
        lighting=dict(
            ambient=0.7,
            diffuse=0.8,
            specular=0.4,
            roughness=0.7,
        ),
    ))

    # ========================================================
    # 2. EQUATEUR
    # ========================================================

    equator_angle = np.linspace(0, 2 * np.pi, 200)

    fig.add_trace(go.Scatter3d(
        x=EARTH_RADIUS * 1.008 * np.cos(equator_angle),
        y=EARTH_RADIUS * 1.008 * np.sin(equator_angle),
        z=np.zeros_like(equator_angle),
        mode="lines",
        line=dict(
            color="#ffffff",
            width=3,
            dash="dash",
        ),
        name="Equator",
        hoverinfo="skip",
    ))

    # ========================================================
    # 3. AXE TERRESTRE
    # ========================================================

    axis_extension = EARTH_RADIUS * 1.18

    fig.add_trace(go.Scatter3d(
        x=[0, 0],
        y=[0, 0],
        z=[-axis_extension, axis_extension],
        mode="lines",
        line=dict(
            color="#ffffff",
            width=5,
        ),
        name="Earth axis",
        hoverinfo="skip",
    ))

    # ========================================================
    # 4. POLE NORD
    # ========================================================

    north_position = EARTH_RADIUS * 1.015

    fig.add_trace(go.Scatter3d(
        x=[0],
        y=[0],
        z=[north_position],
        mode="markers+text",
        marker=dict(
            size=9,
            color="#00ccff",
            line=dict(
                color="white",
                width=2,
            ),
        ),
        text=["NORTH POLE"],
        textposition="top center",
        textfont=dict(
            color="#00ccff",
            size=14,
        ),
        name="North Pole",
        hovertemplate="North Pole<extra></extra>",
    ))

    # ========================================================
    # 5. POLE SUD
    # ========================================================

    fig.add_trace(go.Scatter3d(
        x=[0],
        y=[0],
        z=[-north_position],
        mode="markers+text",
        marker=dict(
            size=9,
            color="#ff5555",
            line=dict(
                color="white",
                width=2,
            ),
        ),
        text=["SOUTH POLE"],
        textposition="bottom center",
        textfont=dict(
            color="#ff5555",
            size=14,
        ),
        name="South Pole",
        hovertemplate="South Pole<extra></extra>",
    ))

    # ========================================================
    # 6. ORBITE ELLIPTIQUE
    # ========================================================

    angle = np.linspace(0, 2 * np.pi, 400)

    x_orbit = a * (np.cos(angle) - eccentricity)
    y_orbit = b * np.sin(angle)

    # Inclinaison du plan orbital
    x_rotated = x_orbit
    y_rotated = y_orbit * np.cos(inclination_rad)
    z_rotated = y_orbit * np.sin(inclination_rad)

    fig.add_trace(go.Scatter3d(
        x=x_rotated,
        y=y_rotated,
        z=z_rotated,
        mode="lines",
        line=dict(
            color="#ffcc00",
            width=6,
        ),
        name="Satellite orbit",
        hoverinfo="skip",
    ))

    # ========================================================
    # 7. PERIGEE
    # ========================================================

    fig.add_trace(go.Scatter3d(
        x=[rp],
        y=[0],
        z=[0],
        mode="markers+text",
        marker=dict(
            size=6,
            color="#00ff88",
        ),
        text=["Perigee"],
        textposition="top center",
        name="Perigee",
        hovertemplate=(
            f"Perigee<br>Altitude: {float(perigee):.1f} km"
            "<extra></extra>"
        ),
    ))

    # ========================================================
    # 8. APOGEE
    # ========================================================

    fig.add_trace(go.Scatter3d(
        x=[-ra],
        y=[0],
        z=[0],
        mode="markers+text",
        marker=dict(
            size=6,
            color="#ff5555",
        ),
        text=["Apogee"],
        textposition="top center",
        name="Apogee",
        hovertemplate=(
            f"Apogee<br>Altitude: {float(apogee):.1f} km"
            "<extra></extra>"
        ),
    ))

    # ========================================================
    # 9. POSITION ILLUSTRATIVE DU SATELLITE
    # ========================================================

    satellite_angle = np.pi / 3

    sx = a * (np.cos(satellite_angle) - eccentricity)
    sy = b * np.sin(satellite_angle)

    sy_rotated = sy * np.cos(inclination_rad)
    sz_rotated = sy * np.sin(inclination_rad)

    fig.add_trace(go.Scatter3d(
        x=[sx],
        y=[sy_rotated],
        z=[sz_rotated],
        mode="markers+text",
        marker=dict(
            size=8,
            color="white",
            symbol="diamond",
        ),
        text=["Satellite"],
        textposition="top center",
        name="Satellite (illustrative position)",
        hovertemplate=(
            "Illustrative satellite position"
            "<extra></extra>"
        ),
    ))

    # ========================================================
    # 10. MISE EN FORME
    # ========================================================

    limit = max(ra * 1.15, axis_extension * 1.1)

    fig.update_layout(
        title="3D Satellite Orbit Visualization",
        height=750,
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor="#101820",
        font=dict(color="white"),
        legend=dict(
            bgcolor="rgba(0,0,0,0.4)",
            orientation="h",
            y=1.02,
        ),
        scene=dict(
            bgcolor="#101820",
            xaxis=dict(
                visible=False,
                range=[-limit, limit],
            ),
            yaxis=dict(
                visible=False,
                range=[-limit, limit],
            ),
            zaxis=dict(
                visible=False,
                range=[-limit, limit],
            ),
            aspectmode="cube",
            camera=dict(
                eye=dict(x=1.6, y=1.6, z=1.2)
            ),
        ),
    )

    return fig, {
        "semi_major_axis": a,
        "eccentricity": eccentricity,
        "semi_minor_axis": b,
    }

# ============================================================
# 4. PAGE DETAILLEE D'UN SATELLITE
# ============================================================

@ui.page("/satellite/{norad}")
def satellite_page(norad: str):

    row = get_satellite(norad)

    if row is None:
        ui.label("Satellite introuvable").classes(
            "text-2xl text-red-500"
        )
        ui.button(
            "Retour",
            on_click=lambda: ui.navigate.to("/")
        )
        return

    # En-tête
    with ui.row().classes("w-full items-center"):
        ui.button(
            "← Retour",
            on_click=lambda: ui.navigate.to("/")
        ).props("flat")

        ui.label("SATELLITE EXPLORER").classes(
            "text-sm text-gray-500 font-bold"
        )

    ui.separator()

    ui.label(str(row[NAME])).classes(
        "text-3xl font-bold"
    )

    ui.label(
        f"NORAD ID : {clean_id(row[NORAD])}"
    ).classes("text-gray-500")

    ui.separator()

    # --------------------------------------------------------
    # INFORMATIONS PRINCIPALES
    # --------------------------------------------------------

    ui.label("Satellite information").classes(
        "text-2xl font-bold"
    )

    with ui.grid(columns=2).classes("w-full"):

        with ui.card().classes("w-full"):
            ui.label("ORBIT CLASS").classes("text-gray-500")
            ui.label(str(row[ORBIT])).classes(
                "text-xl font-bold"
            )

        with ui.card().classes("w-full"):
            ui.label("OPERATOR").classes("text-gray-500")
            ui.label(
                str(row[OPERATOR])
            ).classes("text-xl font-bold")

        with ui.card().classes("w-full"):
            ui.label("COUNTRY").classes("text-gray-500")
            ui.label(
                str(row[COUNTRY])
            ).classes("text-xl font-bold")

        with ui.card().classes("w-full"):
            ui.label("STATUS").classes("text-gray-500")
            status = row.get("Operational Status (OrbitalWiki)")
            ui.label(
                display_value(status)
            ).classes("text-xl font-bold")

    ui.separator()

    # --------------------------------------------------------
    # DONNEES ORBITALES
    # --------------------------------------------------------

    ui.label("Orbital parameters").classes(
        "text-2xl font-bold"
    )

    with ui.grid(columns=2).classes("w-full"):

        with ui.card().classes("w-full"):
            ui.label("PERIGEE").classes("text-gray-500")
            ui.label(
                display_value(row[PERIGEE], "km")
            ).classes("text-2xl font-bold")

        with ui.card().classes("w-full"):
            ui.label("APOGEE").classes("text-gray-500")
            ui.label(
                display_value(row[APOGEE], "km")
            ).classes("text-2xl font-bold")

        with ui.card().classes("w-full"):
            ui.label("INCLINATION").classes("text-gray-500")
            ui.label(
                display_value(row[INCLINATION], "°")
            ).classes("text-2xl font-bold")

        with ui.card().classes("w-full"):
            ui.label("ORBITAL PERIOD").classes("text-gray-500")
            ui.label(
                display_value(row[PERIOD], "minutes")
            ).classes("text-2xl font-bold")

        with ui.card().classes("w-full"):
            ui.label("ECCENTRICITY (CSV)").classes("text-gray-500")
            ui.label(
                display_value(row[ECCENTRICITY])
            ).classes("text-2xl font-bold")

    ui.separator()

    # --------------------------------------------------------
    # GLOBE 3D
    # --------------------------------------------------------

    ui.label("3D Orbital visualization").classes(
        "text-2xl font-bold"
    )

    ui.label(
        "Explorez le globe en faisant glisser la souris. "
        "Vous pouvez zoomer et tourner autour de la Terre."
    ).classes("text-gray-500")

    result = create_orbit_figure(row)

    if result is None:

        ui.label(
            "Impossible de dessiner l'orbite : "
            "les données d'apogée, de périgée ou d'inclinaison "
            "sont manquantes ou invalides."
        ).classes("text-red-500")

    else:

        fig, parameters = result

        ui.plotly(fig).classes("w-full")

        ui.label("Calculated orbital parameters").classes(
            "text-xl font-bold"
        )

        with ui.grid(columns=2).classes("w-full"):

            with ui.card():
                ui.label("SEMI-MAJOR AXIS")
                ui.label(
                    f"{parameters['semi_major_axis']:,.1f} km"
                ).classes("text-xl font-bold")

            with ui.card():
                ui.label("SEMI-MINOR AXIS")
                ui.label(
                    f"{parameters['semi_minor_axis']:,.1f} km"
                ).classes("text-xl font-bold")

            with ui.card():
                ui.label("ECCENTRICITY (CALCULATED)")
                ui.label(
                    f"{parameters['eccentricity']:.5f}"
                ).classes("text-xl font-bold")

    ui.separator()

    ui.label("About this visualization").classes(
        "text-xl font-bold"
    )

    ui.label(
        "The orbit is reconstructed from the perigee, apogee "
        "and inclination available in the database. "
        "Its orientation around the Earth is illustrative "
        "because the database does not provide the RAAN "
        "or the argument of perigee. The satellite marker "
        "does not represent its real-time position."
    ).classes("text-gray-500")


# ============================================================
# 5. PAGE PRINCIPALE
# ============================================================

@ui.page("/")
def create_interface():

    ui.label("Satellite Explorer").classes(
        "text-3xl font-bold"
    )

    ui.label(
        f"Orbital database — {len(df):,} satellites"
    ).classes("text-gray-600")

    ui.separator()

    # --------------------------------------------------------
    # FILTRES
    # --------------------------------------------------------

    with ui.row().classes("w-full items-end"):

        search = ui.input(
            label="Search satellite",
            placeholder="ISS, STARLINK, CALSPHERE..."
        ).classes("w-80")

        orbit = ui.select(
            ["All"] + sorted(
                df[ORBIT].dropna().unique().tolist()
            ),
            value="All",
            label="Orbit",
        ).classes("w-48")

        ui.button(
            "Search",
            on_click=lambda: update_table()
        )

    ui.separator()

    # --------------------------------------------------------
    # REPARTITION DES ORBITES
    # --------------------------------------------------------

    orbit_counts = count_by_orbit(df)

    fig = px.bar(
        orbit_counts,
        x="orbit",
        y="count",
        labels={
            "orbit": "Orbit class",
            "count": "Number of satellites",
        },
        title="Satellites by orbit class",
    )

    ui.plotly(fig).classes("w-full h-96")

    ui.separator()

    # --------------------------------------------------------
    # TABLEAU DES SATELLITES
    # --------------------------------------------------------

    ui.label(
        "Satellite database — Click on a row to open its page"
    ).classes("text-xl font-bold")

    columns = [
        {
            "name": "name",
            "label": "Satellite",
            "field": "name",
            "sortable": True,
        },
        {
            "name": "country",
            "label": "Country",
            "field": "country",
            "sortable": True,
        },
        {
            "name": "orbit",
            "label": "Orbit",
            "field": "orbit",
            "sortable": True,
        },
        {
            "name": "perigee",
            "label": "Perigee (km)",
            "field": "perigee",
            "sortable": True,
        },
        {
            "name": "apogee",
            "label": "Apogee (km)",
            "field": "apogee",
            "sortable": True,
        },
        {
            "name": "inclination",
            "label": "Inclination (°)",
            "field": "inclination",
            "sortable": True,
        },
        {
            "name": "norad",
            "label": "NORAD",
            "field": "norad",
            "sortable": True,
        },
    ]

    # --------------------------------------------------------
    # CLIC SUR UNE LIGNE
    # --------------------------------------------------------

    def open_satellite(event):

        if not event.selection:
            return

        selected = event.selection[0]
        norad = selected["norad"]

        ui.navigate.to(f"/satellite/{norad}")

    table = ui.table(
        columns=columns,
        rows=[],
        row_key="norad",
        pagination=15,
        selection="single",
        on_select=open_satellite,
    ).classes("w-full")

    result_label = ui.label()

    # --------------------------------------------------------
    # MISE A JOUR DU TABLEAU
    # --------------------------------------------------------

    def update_table():

        filtered = df.copy()

        # Recherche par nom
        if search.value:

            filtered = filtered[
                filtered[NAME]
                .fillna("")
                .astype(str)
                .str.contains(
                    search.value,
                    case=False,
                    regex=False,
                )
            ]

        # Filtre par orbite
        if orbit.value != "All":

            filtered = filtered[
                filtered[ORBIT] == orbit.value
            ]

        # Limitation à 500 résultats
        display = filtered.head(500)

        table.rows = [
            {
                "name": str(row[NAME]),
                "country": str(row[COUNTRY]),
                "orbit": str(row[ORBIT]),
                "perigee": row[PERIGEE],
                "apogee": row[APOGEE],
                "inclination": row[INCLINATION],
                "norad": clean_id(row[NORAD]),
            }
            for _, row in display.iterrows()
        ]

        table.update()

        result_label.text = (
            f"{len(filtered)} satellites found"
        )

    # Premier affichage
    update_table()


# ============================================================
# 6. LANCEMENT DE L'APPLICATION
# ============================================================

ui.run(
    title="Satellite Explorer",
    reload=False,
)
