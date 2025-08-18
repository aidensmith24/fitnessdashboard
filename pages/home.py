import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/")


layout = html.Div(
    [
        dbc.Container(
            fluid=True,
            className="py-5 bg-light text-center",
            children=[
                html.H1("Welcome to FitSync", className="display-4 fw-bold"),
                html.P(
                    "Your personal fitness companion to track workouts, nutrition, and progress.",
                    className="lead"
                ),
                dbc.Button("Get Started", color="dark", size="lg", className="mt-3"),
            ],
        ),

        # FEATURES SECTION
        dbc.Container(
            className="my-5",
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.H4("Track Workouts", className="card-title"),
                                    html.P("Log exercises, sets, and reps to monitor progress."),
                                ])
                            ),
                            md=4,
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.H4("Nutrition Plans", className="card-title"),
                                    html.P("Stay on top of your macros with meal tracking."),
                                ])
                            ),
                            md=4,
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.H4("Progress Charts", className="card-title"),
                                    html.P("Visualize your fitness journey with interactive charts."),
                                ])
                            ),
                            md=4,
                        ),
                    ],
                    className="gy-4",  # spacing between rows for mobile
                )
            ],
        ),
    ]
)