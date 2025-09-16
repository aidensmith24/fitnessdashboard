import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from urllib.parse import parse_qs, urlparse

dash.register_page(__name__, path="/login")

def layout(**kwargs):
    # Extract ?error=1 from the URL
    query = kwargs.get("error")

    error_message = ""
    if query:
        error_message = "Invalid username or password."

    return dbc.Container(
        fluid=True,
        className="vh-100 d-flex align-items-center justify-content-center bg-light",
        children=[
            html.Form(
                method="POST",
                action="/login",  # 👈 Flask route
                children=[
                    dbc.Card(
                        className="shadow p-4",
                        style={"width": "100%", "maxWidth": "400px", "borderRadius": "20px"},
                        children=[
                            html.H2("Please Log In", className="text-center mb-4 fw-bold"),

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

                            html.Button(
                                "Login",
                                id="login-button",
                                n_clicks=0,
                                type="submit",
                                className="btn btn-primary w-100 mb-3"
                            ),

                            # Error message from Flask
                            html.Div(
                                error_message,
                                id="output-state",
                                className="text-danger text-center mt-2"
                            ),

                            html.Div(
                                [
                                    html.Span("Don't have an account? ", className="text-muted"),
                                    dcc.Link(
                                        "Register here",
                                        href="/registration",
                                        className="fw-bold text-decoration-none",
                                        style={"color": "#0d6efd"}
                                    ),
                                ],
                                className="text-center mt-3"
                            ),
                            html.Div(
                                [
                                    html.Span("Forgotten password?", className="text-muted"),
                                    dcc.Link(
                                        "Click Here",
                                        href="/forgot-password",
                                        className="fw-bold text-decoration-none",
                                        style={"color": "#0d6efd"}
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
