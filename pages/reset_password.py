import dash
from dash import html, dcc, Input, Output, State
from utils.database_connection import verify_token, update_password
import dash_bootstrap_components as dbc
import re

dash.register_page(__name__, path_template="/reset-password/<token>")

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

def layout(token=None, **kwargs):
    return dbc.Container(
        fluid=True,
        className="d-flex justify-content-center align-items-center",  # flex centering
        style={"height": "100vh"},  # full viewport height
        children=[
            dbc.Card(
                className="shadow-lg p-4",
                style={"maxWidth": "500px", "width": "100%", "borderRadius": "20px"},
                children=[
                    html.H2("Reset Your Password", className="text-center mb-4 fw-bold"),

                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("🔒"),
                            dbc.Input(
                                id="new-pass1",
                                type="password",
                                placeholder="Enter new password",
                                required=True,
                            ),
                        ],
                        className="mb-3"
                    ),

                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("🔒"),
                            dbc.Input(
                                id="new-pass2",
                                type="password",
                                placeholder="Confirm new password",
                                required=True,
                            ),
                        ],
                        className="mb-3"
                    ),

                    dbc.Button(
                        "Reset Password",
                        id="do-reset-btn",
                        color="primary",
                        size="lg",
                        className="w-100 mb-3"
                    ),

                    html.Div(id="reset-done", className="text-center fw-bold mt-2"),

                    # hidden token storage
                    dcc.Store(id="reset-token", data=token),
                ],
            )
        ]
    )

@dash.callback(
    Output("reset-done", "children"),
    Input("do-reset-btn", "n_clicks"),
    State("new-pass1", "value"),
    State("new-pass2", "value"),
    State("reset-token", "data"),
    prevent_initial_call=True
)
def do_reset(n, pw1, pw2, token):
    if pw1 != pw2:
        return "❌ Passwords do not match."

    user_id = verify_token(token)
    if not user_id:
        return "❌ Reset link invalid or expired."

    if not is_strong_password(pw1):
        return "⚠️ Password must be at least 8 characters long, include upper & lowercase letters, a number, and a special character.", "text-danger text-center mt-2"


    update_password(user_id, pw1)
    return "✅ Password has been reset. You can now log in."
