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
                        html.H2("Basal Metabolic Rate Calculator", className="text-center mb-4 fw-bold"),

                        # Unit selector
                        dbc.RadioItems(
                            id="bmr-units",
                            options=[
                                {"label": "Metric", "value": "metric"},
                                {"label": "Imperial", "value": "imperial"}
                            ],
                            value="metric",
                            inline=True,
                            className="mb-3",
                        ),

                        # Age input
                        dbc.InputGroup(
                            [dbc.InputGroupText("Age (years)"), dbc.Input(id="bmr-age", type="number", min=0)],
                            className="mb-3"
                        ),

                        # Metric height input
                        dbc.InputGroup(
                            [dbc.InputGroupText("Height (cm)"), dbc.Input(id="bmr-height-cm", type="number", min=0)],
                            id="bmr-height-metric-group",
                            className="mb-3",
                        ),

                        # Imperial height input (feet + inches)
                        dbc.Row(
                            [
                                dbc.Col(dbc.InputGroup(
                                    [dbc.InputGroupText("Feet"), dbc.Input(id="bmr-height-ft", type="number", min=0)],
                                    className="mb-2"
                                )),
                                dbc.Col(dbc.InputGroup(
                                    [dbc.InputGroupText("Inches"), dbc.Input(id="bmr-height-in", type="number", min=0)],
                                    className="mb-2"
                                )),
                            ],
                            id="bmr-height-imperial-group",
                            className="mb-3",
                        ),

                        # Metric weight input
                        dbc.InputGroup(
                            [dbc.InputGroupText("Weight (kg)"), dbc.Input(id="bmr-weight-kg", type="number", min=0)],
                            id="bmr-weight-metric-group",
                            className="mb-3",
                        ),

                        # Imperial weight input
                        dbc.InputGroup(
                            [dbc.InputGroupText("Weight (lb)"), dbc.Input(id="bmr-weight-lb", type="number", min=0)],
                            id="bmr-weight-imperial-group",
                            className="mb-3",
                        ),

                        # Gender
                        dbc.RadioItems(
                            id="bmr-gender",
                            options=[{"label": "Male", "value": "male"}, {"label": "Female", "value": "female"}],
                            value="male",
                            inline=True,
                            className="mb-3",
                        ),

                        # Activity level
                        dbc.Select(
                            id="bmr-activity",
                            options=[
                                {"label": "Sedentary (little or no exercise)", "value": 1.2},
                                {"label": "Lightly active (1-3 days/week)", "value": 1.375},
                                {"label": "Moderately active (3-5 days/week)", "value": 1.55},
                                {"label": "Very active (6-7 days/week)", "value": 1.725},
                                {"label": "Super active (athlete/physical job)", "value": 1.9},
                            ],
                            value=1.2,
                            className="mb-3",
                        ),

                        dbc.Button("Calculate", id="bmr-calc-btn", color="primary", size="lg", className="w-100 mb-3"),

                        html.Div(id="bmr-result", className="text-center fw-bold fs-4 text-primary"),
                    ],
                )
            )
        )
    ]
)

# ---------------- Show/hide inputs depending on unit ----------------
@dash.callback(
    Output("bmr-height-metric-group", "style"),
    Output("bmr-weight-metric-group", "style"),
    Output("bmr-height-imperial-group", "style"),
    Output("bmr-weight-imperial-group", "style"),
    Input("bmr-units", "value")
)
def toggle_inputs(unit):
    if unit == "metric":
        return {}, {}, {"display": "none"}, {"display": "none"}
    else:
        return {"display": "none"}, {"display": "none"}, {}, {}

# ---------------- BMR calculation ----------------
@dash.callback(
    Output("bmr-result", "children"),
    Input("bmr-calc-btn", "n_clicks"),
    State("bmr-units", "value"),
    State("bmr-gender", "value"),
    State("bmr-age", "value"),
    State("bmr-height-cm", "value"),
    State("bmr-height-ft", "value"),
    State("bmr-height-in", "value"),
    State("bmr-weight-kg", "value"),
    State("bmr-weight-lb", "value"),
    State("bmr-activity", "value"),
    prevent_initial_call=True
)
def calculate_bmr(n, units, gender, age, h_cm, h_ft, h_in, w_kg, w_lb, activity):
    if not age or (units=="metric" and (not h_cm or not w_kg)) or (units=="imperial" and (not h_ft and not h_in or not w_lb)):
        return "⚠️ Please fill in all fields."

    # Convert height to cm if imperial
    if units == "imperial":
        h_cm = (h_ft*12 + h_in) * 2.54

    # Convert weight to kg if imperial
    weight = w_kg if units=="metric" else w_lb * 0.453592

    # BMR calculation
    if gender == "male":
        bmr = 10 * weight + 6.25 * h_cm - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * h_cm - 5 * age - 161

    tdee = bmr * float(activity)

    return f"Your BMR is {bmr:.0f} kcal/day • Estimated TDEE: {tdee:.0f} kcal/day"
