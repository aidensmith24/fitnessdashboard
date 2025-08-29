import dash
from dash import html, dcc, Input, Output, State

import dash_bootstrap_components as dbc

from utils.database_connection import save_user_to_db

import re

dash.register_page(__name__)

def is_strong_password(password: str) -> bool:
    """
    Enforce strong password:
    - At least 8 chars
    - At least 1 lowercase
    - At least 1 uppercase
    - At least 1 digit
    - At least 1 special char (anything not alphanumeric)
    """
    if len(password) < 8:
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[^A-Za-z0-9]", password):  # any non-alphanumeric char
        return False
    return True

# Registration screen
layout = dbc.Container(
    fluid=True,
    className="vh-100 d-flex align-items-center justify-content-center bg-light",
    children=[
        dbc.Card(
            className="shadow p-4",
            style={"width": "100%", "maxWidth": "400px", "borderRadius": "20px"},
            children=[
                html.H2("Create Account", className="text-center mb-4 fw-bold"),

                # Email input
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("📧"),
                        dbc.Input(
                            id="email-box",
                            type="email",
                            placeholder="Enter your email",
                        ),
                    ],
                    className="mb-3",
                ),

                # Username input
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("👤"),
                        dbc.Input(
                            id="uname-box",
                            type="text",
                            placeholder="Choose a username",
                        ),
                    ],
                    className="mb-3",
                ),

                # Password input
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("🔒"),
                        dbc.Input(
                            id="pwd-box",
                            type="password",
                            placeholder="Enter password",
                        ),
                    ],
                    className="mb-3",
                ),

                # Confirm Password input
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("🔒"),
                        dbc.Input(
                            id="confirm-pwd-box",
                            type="password",
                            placeholder="Confirm password",
                        ),
                    ],
                    className="mb-3",
                ),

                # Register button
                dbc.Button(
                    "Register",
                    id="register-button",
                    color="success",
                    className="w-100 mb-3",
                    n_clicks=0,
                ),

                # Output message
                html.Div(id="register-output", className="text-center mt-2"),
            ],
        )
    ],
)

# Callback to validate registration
@dash.callback(
    Output("register-output", "children"),
    Output("register-output", "className"),
    Input("register-button", "n_clicks"),
    State("email-box", "value"),
    State("uname-box", "value"),
    State("pwd-box", "value"),
    State("confirm-pwd-box", "value"),
    prevent_initial_call=True,
)
def handle_register(n_clicks, email, username, password, confirm_password):
    if not email or not username or not password or not confirm_password:
        return "⚠️ Please fill out all fields.", "text-danger text-center mt-2"

    if password != confirm_password:
        return "❌ Passwords do not match.", "text-danger text-center mt-2"

    if not is_strong_password(password):
        return "⚠️ Password must be at least 8 characters long, include upper & lowercase letters, a number, and a special character.", "text-danger text-center mt-2"

    response = save_user_to_db(email, username, password)

    return response, "text-success text-center mt-2"
