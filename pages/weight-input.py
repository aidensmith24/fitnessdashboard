import dash
from dash import html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import io
import base64
from datetime import datetime
import psycopg2
from flask_login import current_user
from utils.database_connection import get_db_connection
from utils.login_handler import require_login

dash.register_page(__name__)
require_login(__name__)

def add_weight_to_db(weight_kg):
    """Add a single weight entry for the current user."""
    if not (hasattr(current_user, "is_authenticated") and current_user.is_authenticated):
        return False, "User not authenticated."

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO bodyweight (username, weight_kg) VALUES (%s, %s)",
            (current_user.id, weight_kg),
        )
        conn.commit()
        return True, "✅ Weight added successfully!"
    except Exception as e:
        conn.rollback()
        return False, f"❌ Database error: {e}"
    finally:
        cur.close()
        conn.close()

def get_user_weights():
    """Fetch all weight entries for the current user."""
    if not (hasattr(current_user, "is_authenticated") and current_user.is_authenticated):
        return []

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT created_at, weight_kg FROM bodyweight WHERE username = %s ORDER BY created_at DESC",
            (current_user.id,),
        )
        rows = cur.fetchall()
        return [{"Date": r[0].strftime("%Y-%m-%d %H:%M"), "Weight": float(r[1])} for r in rows]
    finally:
        cur.close()
        conn.close()

# --- Dash App ---

def serve_layout():
    if not (hasattr(current_user, "is_authenticated") and current_user.is_authenticated):
        return html.Div([
            "Please ",
            dcc.Link("login", href="/login"),
            " to continue"
        ])
    else:
        return dbc.Container(
            fluid=True,
            className="p-4",
            children=[
                dbc.Row(
                    [
                        # Manual entry
                        dbc.Col(
                            dbc.Card(
                                className="shadow p-4 mb-4",
                                children=[
                                    html.H4("Add Weight", className="fw-bold mb-3"),
                                    dbc.InputGroup(
                                        [
                                            dbc.InputGroupText("⚖️"),
                                            dbc.Input(
                                                id="weight-input",
                                                type="number",
                                                placeholder="Enter weight",
                                            ),
                                            dbc.Select(
                                                id="unit-select",
                                                options=[
                                                    {"label": "kg", "value": "kg"},
                                                    {"label": "lbs", "value": "lbs"},
                                                ],
                                                value="kg",
                                                style={"maxWidth": "80px"},
                                            ),
                                        ],
                                        className="mb-3",
                                    ),
                                    dbc.Button(
                                        "Add Weight",
                                        id="add-weight-btn",
                                        color="primary",
                                        className="w-100",
                                        n_clicks=0,
                                    ),
                                    html.Div(id="weight-output", className="text-center mt-3"),
                                ],
                            ),
                            md=6,
                        ),

                        # Bulk upload
                        dbc.Col(
                            dbc.Card(
                                className="shadow p-4 mb-4",
                                children=[
                                    html.H4("Upload Bulk Weights", className="fw-bold mb-3"),
                                    dcc.Upload(
                                        id="upload-data",
                                        children=html.Div(
                                            ["📂 Drag and Drop or ", html.A("Select a File")]
                                        ),
                                        style={
                                            "width": "100%",
                                            "height": "100px",
                                            "lineHeight": "100px",
                                            "borderWidth": "2px",
                                            "borderStyle": "dashed",
                                            "borderRadius": "15px",
                                            "textAlign": "center",
                                            "cursor": "pointer",
                                            "backgroundColor": "#f8f9fa",
                                        },
                                        multiple=False,
                                    ),
                                    html.Div(id="upload-output", className="mt-3"),
                                ],
                            ),
                            md=6,
                        ),
                    ]
                ),

                # Weight history table
                dbc.Row(
                    dbc.Col(
                        dbc.Card(
                            className="shadow p-4",
                            children=[
                                html.H4("Weight History", className="fw-bold mb-3"),
                                dash_table.DataTable(
                                    id="weight-table",
                                    columns=[
                                        {"name": "Date", "id": "Date"},
                                        {"name": "Weight (kg)", "id": "Weight"},
                                    ],
                                    data=get_user_weights(),
                                    style_table={"overflowX": "auto"},
                                    style_cell={"textAlign": "center"},
                                    page_size=10,
                                ),
                            ],
                        ),
                        width=12,
                    )
                ),
            ],
        )


# --- Callbacks ---

@dash.callback(
    Output("weight-output", "children"),
    Output("weight-table", "data", allow_duplicate=True),
    Input("add-weight-btn", "n_clicks"),
    State("weight-input", "value"),
    State("unit-select", "value"),
    prevent_initial_call=True,
)
def add_weight_callback(n_clicks, weight, unit):
    if not weight:
        return "⚠️ Please enter a weight.", get_user_weights()
    if unit == "lbs":
        weight = round(weight * 0.453592, 2)
    success, msg = add_weight_to_db(weight)
    return msg, get_user_weights()


@dash.callback(
    Output("upload-output", "children"),
    Output("weight-table", "data"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def upload_file_callback(contents, filename):
    if contents is None:
        return "⚠️ No file uploaded.", get_user_weights()

    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return "❌ Unsupported file format.", get_user_weights()

        if "Weight" not in df.columns:
            return "⚠️ File must have a 'Weight' column.", get_user_weights()

        count = 0
        for i, row in df.iterrows():
            weight = row["Weight"]
            unit = str(row["Unit"]).lower() if "Unit" in df.columns else "kg"
            if unit == "lbs":
                weight = round(weight * 0.453592, 2)
            success, _ = add_weight_to_db(weight)
            if success:
                count += 1

        return f"✅ Successfully uploaded {count} records!", get_user_weights()

    except Exception as e:
        return f"❌ Error processing file: {e}", get_user_weights()

layout = serve_layout