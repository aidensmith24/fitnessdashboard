import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from utils.database_connection import create_reset_token
from utils.emailer import send_reset_email
import psycopg2

dash.register_page(__name__, path="/forgot-password")

layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    className="shadow-lg p-4",
                    style={"maxWidth": "500px", "margin": "80px auto", "borderRadius": "20px"},
                    children=[
                        html.H2("Forgot Password", className="text-center mb-4 fw-bold"),

                        html.P(
                            "Enter your email address below and we’ll send you a link to reset your password.",
                            className="text-center text-muted mb-4"
                        ),

                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("📧"),
                                dbc.Input(
                                    id="reset-email",
                                    type="email",
                                    placeholder="Enter your email",
                                    required=True,
                                ),
                            ],
                            className="mb-3"
                        ),

                        dbc.Button(
                            "Send Reset Link",
                            id="send-reset-btn",
                            color="primary",
                            size="lg",
                            className="w-100 mb-3"
                        ),

                        html.Div(id="reset-msg", className="text-center text-success fw-bold mt-2"),
                    ],
                ),
                width=12,
                lg=6,
            ), className = "d-flex justify-content-center align-items-center"
        )
    ]
)

@dash.callback(
    Output("reset-msg", "children"),
    Input("send-reset-btn", "n_clicks"),
    State("reset-email", "value"),
    prevent_initial_call=True
)
def handle_reset_request(n, email):
    from utils.database_connection import get_db_connection

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        token = create_reset_token(user[0])
        send_reset_email(email, token)

    return "✅ If that email exists, a reset link has been sent."
