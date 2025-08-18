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
                            id="units",
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
                            [dbc.InputGroupText("Age (years)"), dbc.Input(id="age", type="number", min=0)],
                            className="mb-3"
                        ),

                        # Height input (dynamic)
                        html.Div(id="height-container", className="mb-3"),

                        # Weight input (dynamic)
                        html.Div(id="weight-container", className="mb-3"),

                        # Gender
                        dbc.RadioItems(
                            id="gender",
                            options=[{"label": "Male", "value": "male"}, {"label": "Female", "value": "female"}],
                            value="male",
                            inline=True,
                            className="mb-3",
                        ),

                        # Activity level
                        dbc.Select(
                            id="activity",
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

                        dbc.Button("Calculate", id="calc-btn", color="primary", size="lg", className="w-100 mb-3"),

                        html.Div(id="result", className="text-center fw-bold fs-4 text-primary"),
                    ],
                )
            )
        )
    ]
)

# ------------------ DYNAMIC INPUTS BASED ON UNITS ------------------
@dash.callback(
    Output("height-container", "children"),
    Output("weight-container", "children"),
    Input("units", "value")
)
def update_inputs(units):
    if units == "metric":
        height_input = dbc.InputGroup(
            [dbc.InputGroupText("Height (cm)"), dbc.Input(id="height", type="number", min=0)],
        )
        weight_input = dbc.InputGroup(
            [dbc.InputGroupText("Weight (kg)"), dbc.Input(id="weight", type="number", min=0)],
        )
    else:  # imperial
        height_input = dbc.Row(
            [
                dbc.Col(dbc.InputGroup(
                    [dbc.InputGroupText("Feet"), dbc.Input(id="height-feet", type="number", min=0)],
                    className="mb-2"
                )),
                dbc.Col(dbc.InputGroup(
                    [dbc.InputGroupText("Inches"), dbc.Input(id="height-inches", type="number", min=0)],
                    className="mb-2"
                )),
            ]
        )
        weight_input = dbc.InputGroup(
            [dbc.InputGroupText("Weight (lbs)"), dbc.Input(id="weight", type="number", min=0)],
        )
    return height_input, weight_input

# ------------------ BMR CALCULATION ------------------
@dash.callback(
    Output("result", "children"),
    Input("calc-btn", "n_clicks"),
    State("units", "value"),
    State("gender", "value"),
    State("age", "value"),
    State("height", "value"),
    State("height-feet", "value"),
    State("height-inches", "value"),
    State("weight", "value"),
    State("activity", "value"),
    prevent_initial_call=True
)
def calculate_bmr(n, units, gender, age, h_cm, h_feet, h_inches, weight, activity):
    if not age or not weight or (units=="metric" and not h_cm) or (units=="imperial" and (not h_feet and not h_inches)):
        return "⚠️ Please fill in all fields."

    # Convert height to cm if imperial
    if units == "imperial":
        h_cm = (h_feet*12 + h_inches) * 2.54

    # Convert weight to kg if imperial
    if units == "imperial":
        weight = weight * 0.453592

    # BMR calculation
    if gender == "male":
        bmr = 10 * weight + 6.25 * h_cm - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * h_cm - 5 * age - 161

    tdee = bmr * float(activity)

    return f"Your BMR is {bmr:.0f} kcal/day • Estimated TDEE: {tdee:.0f} kcal/day"
