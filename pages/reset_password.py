import dash
from dash import html, dcc, Input, Output, State
from utils.database_connection import verify_token, update_password

dash.register_page(__name__, path_template="/reset-password/<token>")

def layout(token=None, **kwargs):
    return dbc.Container(
        fluid=True,
        style={"height": "100vh"},  # full screen height
        children=[
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        className="shadow-lg p-4",
                        style={"maxWidth": "500px", "borderRadius": "20px"},
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

                            dcc.Store(id="reset-token", data=token),  # hidden token store
                        ],
                    ),
                    width=12,
                    lg=6,
                ),
                className="d-flex justify-content-center align-items-center",
                style={"height": "100vh"},
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

    update_password(user_id, pw1)
    return "✅ Password has been reset. You can now log in."
