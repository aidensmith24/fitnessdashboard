import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__)

# Login screen
layout = dbc.Container(
    fluid=True,
    className="vh-100 d-flex align-items-center justify-content-center bg-light",
    children=[
        html.Form(
            method="POST",
            children=[
                dbc.Card(
                    className="shadow p-4",
                    style={"width": "100%", "maxWidth": "400px", "borderRadius": "20px"},
                    children=[
                        html.H2("Please Log In", className="text-center mb-4 fw-bold"),

                        # Username input
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("👤"),
                                dcc.Input(
                                    id="uname-box",
                                    name="username",
                                    type="text",
                                    placeholder="Enter your username",
                                    className="form-control"
                                ),
                            ],
                            className="mb-3",
                        ),

                        # Password input
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("🔒"),
                                dcc.Input(
                                    id="pwd-box",
                                    name="password",
                                    type="password",
                                    placeholder="Enter your password",
                                    className="form-control"
                                ),
                            ],
                            className="mb-3",
                        ),

                        # Login button
                        html.Button(
                            "Login",
                            id="login-button",
                            n_clicks=0,
                            type="submit",
                            className="btn btn-primary w-100 mb-3"
                        ),

                        # Output area (e.g., error message)
                        html.Div(id="output-state", className="text-danger text-center mt-2"),
                        html.Div(
                            [
                                html.Span("Don't have an account? ", className="text-muted"),
                                dcc.Link(
                                    "Register here",
                                    href="/registration",  # 👈 your registration route
                                    className="fw-bold text-decoration-none",
                                    style={"color": "#0d6efd"}  # Bootstrap primary blue
                                ),
                            ],
                            className="text-center mt-3"
                        )
                    ],
                )
            ],
        )
    ],
)