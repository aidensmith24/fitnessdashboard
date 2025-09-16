import dash
from dash import html, dcc, Input, Output, State
from utils.database_connection import create_reset_token
from utils.emailer import send_reset_email
import psycopg2

dash.register_page(__name__, path="/forgot-password")

layout = html.Div([
    html.H2("Forgot Password"),
    dcc.Input(id="reset-email", type="email", placeholder="Enter your email"),
    html.Button("Send reset link", id="send-reset-btn"),
    html.Div(id="reset-msg", className="mt-2")
])

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
