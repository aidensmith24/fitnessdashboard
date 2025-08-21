import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

dash.register_page(__name__)

layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    className="shadow-lg p-4",
                    style={"maxWidth": "600px", "margin": "50px auto", "borderRadius": "20px"},
                    children=[
                        html.H2("BMI Calculator", className="text-center mb-4 fw-bold"),

                        # Unit selector
                        dbc.RadioItems(
                            id="bmi-units",
                            options=[
                                {"label": "Metric (kg, cm)", "value": "metric"},
                                {"label": "Imperial (lb, ft+in)", "value": "imperial"}
                            ],
                            value="metric",
                            inline=True,
                            className="mb-3",
                        ),

                        # Metric height input
                        dbc.InputGroup(
                            [dbc.InputGroupText("Height (cm)"), dbc.Input(id="bmi-height", type="number", min=0)],
                            id="bmi-height-metric-group",
                            className="mb-3",
                        ),

                        # Imperial height inputs (feet + inches)
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Height:"),
                                dbc.Input(id="bmi-height-ft", type="number", min=0, placeholder="ft"),
                                dbc.InputGroupText("ft"),
                                dbc.Input(id="bmi-height-in", type="number", min=0, placeholder="in"),
                                dbc.InputGroupText("in"),
                            ],
                            id="bmi-height-imperial-group",
                            className="mb-3",
                        ),

                        # Metric weight input
                        dbc.InputGroup(
                            [dbc.InputGroupText("Weight (kg)"), dbc.Input(id="bmi-weight-metric", type="number", min=0)],
                            id="bmi-weight-metric-group",
                            className="mb-3",
                        ),

                        # Imperial weight input
                        dbc.InputGroup(
                            [dbc.InputGroupText("Weight (lb)"), dbc.Input(id="bmi-weight-imperial", type="number", min=0)],
                            id="bmi-weight-imperial-group",
                            className="mb-3",
                        ),

                        # Calculate button
                        dbc.Button("Calculate BMI", id="bmi-calc-btn", color="primary", size="lg", className="w-100 mb-3"),

                        # Result
                        html.Div(id="bmi-result", className="text-center fw-bold fs-4 text-primary"),
                    ],
                )
            )
        )
    ]
)

# Show/hide inputs depending on unit
@dash.callback(
    Output("bmi-height-metric-group", "style"),
    Output("bmi-weight-metric-group", "style"),
    Output("bmi-height-imperial-group", "style"),
    Output("bmi-weight-imperial-group", "style"),
    Input("bmi-units", "value")
)
def toggle_inputs(unit):
    if unit == "metric":
        return {}, {}, {"display": "none"}, {"display": "none"}
    else:
        return {"display": "none"}, {"display": "none"}, {}, {}

# Calculate BMI
@dash.callback(
    Output("bmi-result", "children"),
    Input("bmi-calc-btn", "n_clicks"),
    State("bmi-units", "value"),
    State("bmi-height", "value"),
    State("bmi-weight-metric", "value"),
    State("bmi-height-ft", "value"),
    State("bmi-height-in", "value"),
    State("bmi-weight-imperial", "value"),
    prevent_initial_call=True
)
def calculate_bmi(n_clicks, unit, height_cm, weight_kg, height_ft, height_in, weight_lb):
    if unit == "metric":
        if not height_cm or not weight_kg:
            return "Please enter both height and weight."
        bmi = weight_kg / ((height_cm / 100) ** 2)
    else:
        if not height_ft or height_in is None or not weight_lb:
            return "Please enter weight, feet, and inches."
        total_inches = height_ft * 12 + height_in
        bmi = 703 * weight_lb / (total_inches ** 2)

    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 24.9:
        category = "Normal weight"
    elif 25 <= bmi < 29.9:
        category = "Overweight"
    else:
        category = "Obesity"

    return f"Your BMI is {bmi:.2f} ({category})"
