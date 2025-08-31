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
from dash import ctx
import plotly.graph_objects as go

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
                className="p-3",
                children=[
                    dbc.Card(
                        className="shadow-sm p-3 mb-4",
                        children=[
                            html.H3("Add Weight", className="mb-3 text-center fw-bold"),
                            dbc.Row([
                                dbc.Col(
                                    dbc.InputGroup([
                                        dbc.InputGroupText("⚖️"),
                                        dbc.Input(id="weight-input", type="number", placeholder="Enter weight"),
                                    ]),
                                    xs=12, md=6, className="mb-2"
                                ),
                                dbc.Col(
                                    dcc.Dropdown(
                                        id="unit-select",
                                        options=[
                                            {"label": "Kilograms (kg)", "value": "kg"},
                                            {"label": "Pounds (lbs)", "value": "lbs"}
                                        ],
                                        value="kg",
                                        clearable=False,
                                    ),
                                    xs=12, md=4, className="mb-2"
                                ),
                                dbc.Col(
                                    dbc.Button("Add", id="add-weight-btn", color="primary", className="w-100"),
                                    xs=12, md=2, className="mb-2"
                                ),
                            ]),
                            html.Div(id="weight-output", className="text-success text-center mt-2"),
                        ]
                    ),

                    dbc.Card(
                        className="shadow-sm p-3 mb-4",
                        children=[
                            html.H3("Bulk Upload", className="mb-3 text-center fw-bold"),
                            dcc.Upload(
                                id="upload-data",
                                children=html.Div(["📤 Drag & Drop or ", html.A("Select Files")]),
                                style={
                                    "width": "100%", "height": "80px",
                                    "lineHeight": "80px", "borderWidth": "1px",
                                    "borderStyle": "dashed", "borderRadius": "12px",
                                    "textAlign": "center",
                                },
                                multiple=False
                            ),
                            html.Div(id="upload-output", className="text-info text-center mt-2"),
                        ]
                    ),

                    dbc.Card(
                        className="shadow-sm p-3 mb-4",
                        children=[
                            html.H3("Weight History", className="mb-3 text-center fw-bold"),
                            dcc.Dropdown(
                                id="history-unit-select",
                                options=[
                                    {"label": "Kilograms (kg)", "value": "kg"},
                                    {"label": "Pounds (lbs)", "value": "lbs"}
                                ],
                                value="kg",
                                clearable=False,
                                className="mb-3"
                            ),
                            dbc.RadioItems(
                                id="graph-view-mode",
                                options=[
                                    {"label": "Daily Average", "value": "avg"},
                                    {"label": "All Entries", "value": "all"}
                                ],
                                value="avg",
                                inline=True,
                                className="mb-3"
                            ),
                            dcc.Graph(
                                id="weight-graph",
                                config={"displayModeBar": False},
                                style={"height": "300px", "width": "100%"},
                            ),
                            dash_table.DataTable(
                                id="weight-table",
                                columns=[
                                    {"name": "Date", "id": "Date"},
                                    {"name": "Weight", "id": "Weight"},
                                ],
                                style_table={"overflowX": "auto"},
                                style_cell={
                                    "textAlign": "center",
                                    "padding": "8px",
                                    "minWidth": "80px",
                                    "whiteSpace": "normal"
                                },
                            ),
                        ]
                    ),
                ]
            )


def convert_weights(weights, unit):
    """Convert weight list from kg to preferred unit for display."""
    converted = []
    for w in weights:
        if unit == "lbs":
            converted.append({
                "Date": w["Date"],
                "Weight": round(w["Weight"] * 2.20462, 2)
            })
        else:
            converted.append({
                "Date": w["Date"],
                "Weight": round(w["Weight"], 2)
            })
    return converted

def convert_to_kg(weight):
    return round(weight / 2.20462, 2)


@dash.callback(
    Output("weight-output", "children"),
    Output("upload-output", "children"),
    Output("weight-table", "data"),
    Output("weight-graph", "figure"),
    Input("add-weight-btn", "n_clicks"),
    State("weight-input", "value"),
    State("unit-select", "value"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    Input("history-unit-select", "value"),
    Input("graph-view-mode", "value")
    )
def update_page(n_clicks, weight, unit, uploaded_contents, filename, display_unit, view_mode):
    msg = ""
    upload_msg = ""

    # Add weight manually
    if n_clicks and weight:
        if unit == 'lbs':
            weight = convert_to_kg(weight)
        add_weight_to_db(weight)  # hardcoded user_id=1
        msg = "✅ Weight added!"

    # Handle bulk upload
    if uploaded_contents:
        content_type, content_string = uploaded_contents.split(",")
        decoded = base64.b64decode(content_string)
        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            else:
                df = pd.read_excel(io.BytesIO(decoded))

            for _, row in df.iterrows():
                add_weight_to_db(row.get("Unit", "kg"))
            upload_msg = "✅ Bulk upload successful!"
        except Exception as e:
            upload_msg = f"❌ Upload failed: {e}"

    # Get all weights from DB
    data = convert_weights(get_user_weights(), display_unit)
    data = sorted(data, key=lambda row: row["Date"])

    # Build graph
    fig = go.Figure()
    if data:
        if view_mode == "avg":
            df = pd.DataFrame(data)
            # Ensure datetime
            df["Date"] = pd.to_datetime(df['Date']).dt.date
            # Strip time, group by day
            daily_avg = df.groupby('Date').mean().reset_index()
            # Convert dates to strings for categorical x-axis
            daily_avg["Date"] = daily_avg["Date"].astype(str)

            fig.add_trace(
                go.Scatter(
                    x=daily_avg["Date"],
                    y=daily_avg["Weight"],
                    mode="lines+markers",
                    line=dict(shape="spline", smoothing=1.3, width=3),
                    marker=dict(size=6)
                )
            )
            fig.update_layout(
                xaxis_type='category',
                xaxis_title="Date",
                yaxis_title=f"Weight ({display_unit})",
                margin=dict(l=20, r=20, t=30, b=20),
                template="simple_white"
            )

        else:
            fig.add_trace(
                go.Scatter(
                    x=[row["Date"] for row in data],
                    y=[row["Weight"] for row in data],
                    mode="lines+markers",
                    line=dict(shape="spline", smoothing=1.3, width=3),
                    marker=dict(size=6)
                )
            )

        fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis_title="Date",
            yaxis_title=f"Weight ({display_unit})",
            template="simple_white",
        )

    return msg, upload_msg, data, fig


layout = serve_layout