import dash
from dash import html, Input, Output, State
import dash_bootstrap_components as dbc

dash.register_page(__name__)

layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    className="shadow-lg p-4",
                    style={"maxWidth": "500px", "margin": "50px auto", "borderRadius": "20px"},
                    children=[
                        html.H2("One-Rep Max Calculator", className="text-center mb-4 fw-bold"),

                        # Exercise selector
                        dbc.Select(
                            id="orm-exercise",
                            options=[
                                {"label": "Bench Press", "value": "bench"},
                                {"label": "Squat", "value": "squat"},
                                {"label": "Deadlift", "value": "deadlift"},
                            ],
                            value="bench",
                            className="mb-3",
                        ),

                        # Unit selector
                        dbc.RadioItems(
                            id="orm-units",
                            options=[
                                {"label": "Metric (kg)", "value": "metric"},
                                {"label": "Imperial (lbs)", "value": "imperial"},
                            ],
                            value="metric",
                            inline=True,
                            className="mb-3",
                        ),

                        # Weight input
                        dbc.InputGroup(
                            [dbc.InputGroupText("Weight"), dbc.Input(id="orm-weight", type="number", min=0)],
                            className="mb-3",
                        ),

                        # Reps input
                        dbc.InputGroup(
                            [dbc.InputGroupText("Reps"), dbc.Input(id="orm-reps", type="number", min=1)],
                            className="mb-3",
                        ),

                        dbc.Button("Calculate 1RM", id="orm-calc-btn", color="primary", size="lg", className="w-100 mb-3"),

                        html.Div(id="orm-result", className="text-center fw-bold fs-4 text-primary"),
                    ],
                )
            )
        )
    ]
)

# 1RM calculation callback
@dash.callback(
    Output("orm-result", "children"),
    Input("orm-calc-btn", "n_clicks"),
    State("orm-exercise", "value"),
    State("orm-units", "value"),
    State("orm-weight", "value"),
    State("orm-reps", "value"),
    prevent_initial_call=True
)
def calculate_1rm(n, exercise, units, weight, reps):
    if not weight or not reps:
        return "⚠️ Please enter both weight and reps."

    # Epley formula
    one_rm = weight * (1 + reps / 30)

    unit_label = "kg" if units == "metric" else "lbs"

    exercise_name = {"bench": "Bench Press", "squat": "Squat", "deadlift": "Deadlift"}[exercise]

    return f"{exercise_name} estimated 1RM: {one_rm:.1f} {unit_label}"
