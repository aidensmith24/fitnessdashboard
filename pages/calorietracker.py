import dash
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import psycopg2
import base64, io
from utils.database_connection import get_db_connection
from utils.login_handler import require_login
from flask_login import current_user


dash.register_page(__name__)
require_login(__name__)

def save_meal(username, meal_name, calories):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO calories_table (username, meal_name, calories, date) VALUES (%s, %s, %s, %s)",
        (username, meal_name, calories, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    conn.commit()
    cur.close()
    conn.close()

def get_user_meals():
    if not (hasattr(current_user, "is_authenticated") and current_user.is_authenticated):
        return []
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT date, meal_name, calories FROM calories_table WHERE username = %s ORDER BY date ASC",
        (current_user.id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"Date": row[0].strftime('%Y-%m-%d %H:%M:%S'), "Meal": row[1], "Calories": row[2]} for row in rows]


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
                    # Manual Entry
                    dbc.Card(
                        className="shadow-sm p-3 mb-4",
                        children=[
                            html.H3("Add Meal", className="mb-3 text-center fw-bold"),
                            dbc.Row([
                                dbc.Col(dbc.Input(id="meal-name-input", placeholder="Meal name"), xs=12, md=6, className="mb-2"),
                                dbc.Col(dbc.Input(id="calories-input", type="number", placeholder="Calories"), xs=12, md=4, className="mb-2"),
                                dbc.Col(dbc.Button("Add Meal", id="add-meal-btn", color="primary", className="w-100"), xs=12, md=2, className="mb-2"),
                            ]),
                            html.Div(id="meal-output", className="text-success text-center mt-2"),
                        ]
                    ),

                    # Bulk Upload
                    dbc.Card(
                        className="shadow-sm p-3 mb-4",
                        children=[
                            html.H3("Bulk Upload", className="mb-3 text-center fw-bold"),
                            dcc.Upload(
                                id="upload-meals",
                                children=html.Div(["📤 Drag & Drop or ", html.A("Select CSV/Excel")]),
                                style={
                                    "width": "100%", "height": "80px",
                                    "lineHeight": "80px", "borderWidth": "1px",
                                    "borderStyle": "dashed", "borderRadius": "12px",
                                    "textAlign": "center",
                                },
                                multiple=False
                            ),
                            html.Div(id="upload-output-calories", className="text-info text-center mt-2"),
                        ]
                    ),
                    # History + Daily Total Graph
                    dbc.Card(
                        className="shadow-sm p-3 mb-4",
                        children=[
                            html.H3("Meal History", className="mb-3 text-center fw-bold"),
                            dcc.Graph(
                                id="daily-calories-graph",
                                config={"displayModeBar": False},
                                style={"height": "300px", "width": "100%"},
                            ),
                            dash_table.DataTable(
                                id="meals-table",
                                columns=[
                                    {"name": "Date", "id": "Date"},
                                    {"name": "Meal", "id": "Meal"},
                                    {"name": "Calories", "id": "Calories"},
                                ],
                                style_table={"overflowX": "auto"},
                                style_cell={"textAlign": "center", "padding": "8px", "minWidth": "80px", "whiteSpace": "normal"},
                            ),
                        ]
                    ),
                ]
            )

# -------------------------------
# Unified Callback
# -------------------------------
@dash.callback(
    Output("meal-output", "children"),
    Output("upload-output-calories", "children"),
    Output("meals-table", "data"),
    Output("daily-calories-graph", "figure"),
    Input("add-meal-btn", "n_clicks"),
    State("meal-name-input", "value"),
    State("calories-input", "value"),
    Input("upload-meals", "contents"),
    State("upload-meals", "filename"),
)
def handle_meals(n_clicks, meal_name, calories, contents, filename):
    msg = ""
    upload_msg = ""

    # Add single meal
    if n_clicks and meal_name and calories is not None:
        save_meal(current_user.id, meal_name, calories)
        msg = "✅ Meal added!"

    # Bulk upload
    if contents:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            else:
                df = pd.read_excel(io.BytesIO(decoded))
            for _, row in df.iterrows():
                save_meal(current_user.id, row["Meal"], row["Calories"])
            upload_msg = "✅ Bulk upload successful!"
        except Exception as e:
            upload_msg = f"❌ Upload failed: {e}"

    # Fetch all meals
    data = get_user_meals()
    data_sorted = sorted(data, key=lambda row: row["Date"])

    # Build daily calories graph
    df = pd.DataFrame(data_sorted)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"]).dt.date.astype(str)
        daily_totals = df.groupby("Date")["Calories"].sum().reset_index()
        daily_totals["Date"] = pd.to_datetime(daily_totals["Date"]).dt.date.astype(str)

        fig = go.Figure(go.Scatter(
            x=daily_totals["Date"],
            y=daily_totals["Calories"],
            mode="lines+markers",
            line=dict(shape="spline", smoothing=1.3, width=3),
            marker=dict(size=6)
        ))
        fig.update_layout(
            xaxis_type='category',
            xaxis_title="Date",
            yaxis_title="Calories",
            yaxis=dict(tickformat="d"),
            margin=dict(l=20, r=20, t=30, b=20),
            template="simple_white"
        )
    else:
        fig = go.Figure()

    return msg, upload_msg, data_sorted, fig

layout = serve_layout