import dash
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import psycopg2
from utils.database_connection import get_db_connection
from utils.login_handler import require_login
from flask_login import current_user
from dash import ctx
import plotly.express as px


dash.register_page(__name__)
require_login(__name__)

def save_meal(username, meal_name, protein, carbs, fat):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO macros_table (username, meal_name, protein, carbs, fats, date) VALUES (%s, %s, %s, %s, %s, %s)",
        (username, meal_name, protein, carbs, fat, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
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
        "SELECT date, meal_name, protein, carbs, fats FROM macros_table WHERE username = %s ORDER BY date ASC",
        (current_user.id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"Date": row[0].strftime('%Y-%m-%d %H:%M:%S'), "Meal": row[1], "Protein": row[2], "Carbs": row[3], "Fat": row[4]} for row in rows]

# -------------------
# Layout
# -------------------
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
        # --- Add Meal Section ---
        dbc.Card(
            dbc.CardBody([
                html.H3("Add Meal Macros", className="mb-3 text-center fw-bold"),
                dbc.Row([
                    dbc.Col(dbc.Input(id="macro-meal-name", placeholder="Meal name"), xs=12, md=4, className="mb-2"),
                    dbc.Col(dbc.Input(id="macro-protein", type="number", placeholder="Protein (g)"), xs=12, md=2, className="mb-2"),
                    dbc.Col(dbc.Input(id="macro-carbs", type="number", placeholder="Carbs (g)"), xs=12, md=2, className="mb-2"),
                    dbc.Col(dbc.Input(id="macro-fat", type="number", placeholder="Fat (g)"), xs=12, md=2, className="mb-2"),
                    dbc.Col(dbc.Button("Add Meal", id="add-macro-btn", color="primary", className="w-100"), xs=12, md=2, className="mb-2"),
                ]),
                html.Div(id="macro-add-output", className="text-success text-center mt-2"),
            ]),
            className="shadow-sm p-3 mb-4"
        ),

        # --- Charts ---
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Macros Breakdown", className="text-center mb-3"),
                        dcc.DatePickerSingle(
                            id="macro-date-picker",
                            date=datetime.today(),  # default to today
                            display_format="YYYY-MM-DD",
                            style={"width": "100%"}
                        ),
                        html.Div(id="macro-pie-chart"),
                    ])
                ),

                xs=12, md=6, className="mb-3"
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Macros History", className="text-center mb-3"),
                        dcc.Graph(id="macro-line-chart", config={"displayModeBar": False}, style={"height": "300px"}),
                    ])
                ),
                xs=12, md=6, className="mb-3"
            ),
        ]),

        # --- Meals Table ---
        dbc.Card(
            dbc.CardBody([
                html.H5("Logged Meals", className="text-center mb-3"),
                dash_table.DataTable(
                    id="macro-table",
                    columns=[
                        {"name": "Date", "id": "Date"},
                        {"name": "Meal", "id": "Meal"},
                        {"name": "Protein (g)", "id": "Protein"},
                        {"name": "Carbs (g)", "id": "Carbs"},
                        {"name": "Fat (g)", "id": "Fat"}
                    ],
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "center", "minWidth": "80px"},
                ),
            ]),
            className="shadow-sm p-3"
        ),

        # --- Error Modal ---
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("⚠️ Missing Fields")),
                dbc.ModalBody("Please fill out all macro fields before submitting."),
                dbc.ModalFooter(dbc.Button("Close", id="close-macro-modal", className="ms-auto")),
            ],
            id="macro-modal",
            is_open=False,
        ),
    ]
)


# ===================== Callbacks =====================
@dash.callback(
    Output("macro-add-output", "children"),
    Output("macro-table", "data"),
    Output("macro-pie-chart", "children"),
    Output("macro-line-chart", "figure"),
    Output("macro-modal", "is_open"),
    Input("add-macro-btn", "n_clicks"),
    Input("macro-date-picker", "date"),
    State("macro-meal-name", "value"),
    State("macro-protein", "value"),
    State("macro-carbs", "value"),
    State("macro-fat", "value"),
    State("macro-modal", "is_open"),
)
def update_macros(n_clicks, selected_date, meal, protein, carbs, fat, modal_open):
    triggered = ctx.triggered_id
    msg = dash.no_update

    # Fetch meals
    meals = get_user_meals()
    df = pd.DataFrame(meals)

    # Add meal if button pressed
    if triggered == "add-macro-btn":
        if not meal or protein is None or carbs is None or fat is None:
            return msg, dash.no_update, dash.no_update, dash.no_update, True

        save_meal(current_user.id, meal, protein, carbs, fat)
        msg = f"✅ Added {meal}"
        meals = get_user_meals()
        df = pd.DataFrame(meals)

    if df.empty:
        return msg, [], None, {}, False

    # Normalize date column
    df["Day"] = pd.to_datetime(df["Date"]).dt.date

    # Pie chart for selected date
    pie_chart = None
    if selected_date:
        sel_date = pd.to_datetime(selected_date).date()
        day_df = df[df["Day"] == sel_date]
        if not day_df.empty:
            totals = day_df[["Protein", "Carbs", "Fat"]].sum()
            pie = px.pie(
                names=totals.index, values=totals.values,
                title=f"Macros for {sel_date}"
            )
            pie.update_traces(textinfo="percent+label")
            pie_chart = dcc.Graph(figure=pie, config={"displayModeBar": False})

    # Line chart (all days)
    daily = df.groupby("Day", as_index=False)[["Protein", "Carbs", "Fat"]].sum()
    line_chart = px.line(
        daily,
        x="Day",
        y=["Protein", "Carbs", "Fat"],
        title="Daily Macros Over Time"
    )
    line_chart.update_layout(yaxis_title="Grams")
    line_chart.update_layout(
        xaxis=dict(
            tickformat="%Y-%m-%d",  # show only date
            dtick="D1"               # one day between ticks
        )
    )


    return msg, df.to_dict("records"), pie_chart, line_chart, False


# --- Close Modal Helper ---
@dash.callback(
    Output("macro-modal", "is_open", allow_duplicate=True),
    Input("close-macro-modal", "n_clicks"),
    State("macro-modal", "is_open"),
    prevent_initial_call=True
)
def close_modal(n, modal_open):
    return not modal_open if n else modal_open
layout = serve_layout