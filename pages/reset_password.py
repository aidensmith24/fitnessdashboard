import dash
from dash import html, dcc, Input, Output, State
from utils.database_connection import verify_token, update_password

dash.register_page(__name__, path_template="/reset-password/<token>")

def layout(token=None, **kwargs):
    return html.Div([
        html.H2("Reset Your Password"),
        dcc.Input(id="new-pass1", type="password", placeholder="New password"),
        dcc.Input(id="new-pass2", type="password", placeholder="Confirm password"),
        html.Button("Reset Password", id="do-reset-btn"),
        html.Div(id="reset-done", className="mt-2"),
        dcc.Store(id="reset-token", data=token)
    ])

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

    update_password(user_id, pw1)
    return "✅ Password has been reset. You can now log in."
