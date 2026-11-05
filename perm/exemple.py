import numpy as np
import pandas as pd
import plotly.express as px
from nicegui import ui


def update_figure(plot: ui.plotly, phase=0, amplitude=1):
    X = np.linspace(0, 3, 100)

    df_sin = pd.DataFrame(
        {"x": X, "y": amplitude * np.sin(X + phase), "function": "sin"}
    )

    df_cos = pd.DataFrame(
        {"x": X, "y": amplitude * np.cos(X + phase), "function": "cos"}
    )

    df = pd.concat([df_sin, df_cos])

    plot.update_figure(px.line(df, x="x", y="y", color="function"))


def app():
    ui.colors(
        base_100="oklch(100% 0 0)",
        base_200="oklch(93% 0 0)",
        base_300="oklch(86% 0 0)",
    )

    ui.query(".nicegui-content").style("padding: 0; overflow: hidden;")

    with ui.element("div").classes("flex flex-col w-full h-screen"):
        # Header
        with ui.element("header").classes("min-h-[4%] bg-base-300 p-4"):
            ui.label("The sinusoid exercice").classes("text-xl")

        # Main
        with ui.element("div").classes("flex grow"):
            with ui.element("div").classes("w-[30%] max-w-xs bg-base-200 p-4"):
                ui.label("Options").classes("text-xl")

                ui.label("Phase")
                phase = ui.slider(min=0, max=6, value=0, step=0.1)

                ui.label("Amplitude")
                amplitude = ui.slider(min=0, max=3, value=1, step=0.1)

                ui.button("Update").on_click(
                    lambda: update_figure(plot, phase.value, amplitude.value)
                )

            # Content
            with ui.element("div").classes("grow bg-base-100 p-4"):
                X = np.linspace(0, 3, 100)

                df_sin = pd.DataFrame({"x": X, "y": np.sin(X), "function": "sin"})

                df_cos = pd.DataFrame({"x": X, "y": np.cos(X), "function": "cos"})

                df = pd.concat([df_sin, df_cos])

                fig = px.line(df, x="x", y="y", color="function")

                plot = ui.plotly(fig).classes("w-full h-full")

        # Footer
        with ui.element("footer").classes("min-h-[4%] bg-base-300 p-4"):
            with ui.row().classes("items-center text-xl"):
                ui.label("Parameter info")


app()
from nicegui import ui
import pandas as pd
import numpy as np

with ui.card(align_items="center"):
    with ui.row().classes("items-center"):
        ui.label("Style:")
        ui.separator().props("vertical")
        ui.select(["Fusion", "Other"], value="Fusion")
        ui.checkbox("Use standard palette")
        ui.checkbox("Disable widgets")
    ui.separator()
    with ui.grid(columns=2):
        with ui.column():
            ui.label("Box 1")
            ui.radio(["Radio button 1"])
            ui.radio(["Radio button 2"])
            ui.radio(["Radio button 3"])
            ui.checkbox("Tri-state check box")
        with ui.column():
            ui.label("Box 2")
            my_button = ui.button("Default button")
            ui.button("Flat button").props("flat")
            ui.button("Disabled button").disable()
        with ui.column():
            with ui.tabs().classes("w-full") as tabs:
                one = ui.tab("One")
                two = ui.tab("Two")
            with ui.tab_panels(tabs, value=two).classes("w-full"):
                with ui.tab_panel(one):
                    ui.label("Table")
                    ui.table.from_pandas(pd.DataFrame(np.random.randint(0, 5, (4, 4))))
                with ui.tab_panel(two):
                    ui.label("Text edit")
                    ui.textarea()
        with ui.row():
            ui.slider(min=0, max=50, value=25).props("vertical")
            with ui.column():
                ui.checkbox("Group 3")
                ui.input("password", password=True)
                ui.slider(min=0, max=50, value=0)
                with ui.input("Date") as date:
                    with ui.menu().props("no-parent-event") as menu:
                        with ui.date().bind_value(date):
                            with ui.row().classes("justify-end"):
                                ui.button("Close", on_click=menu.close).props("flat")
                    with date.add_slot("append"):
                        ui.icon("edit_calendar").on("click", menu.open).classes(
                            "cursor-pointer"
                        )
                ui.knob(0.5, min=0.1, max=0.9, show_value=True)
    ui.linear_progress(0.5)


ui.run(title="Styles")
