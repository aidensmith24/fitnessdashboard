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
import requests
from utils.usda_query import query_usda_info


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
                    dcc.Store(id="food-search-store", data=[]),
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
                        [
                            html.H2("Food Search", className="mb-4"),
                            
                            dbc.InputGroup(
                                [
                                    dbc.Input(id="food-query", placeholder="Search for a food (e.g., chicken breast)", type="text"),
                                    dbc.Button("Search", id="search-btn", color="primary"),
                                ],
                                className="mb-3"
                            ),
                            
                            html.Div(id="food-results")
                        ],
                        className="p-4"
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

@dash.callback(
    Output("meal-output", "children"),
    Output("meals-table", "data"),
    Output("daily-calories-graph", "figure"),
    Input("add-meal-btn", "n_clicks"),
    Input({"type": "log-btn", "index": dash.ALL}, "n_clicks"),
    State("meal-name-input", "value"),
    State("calories-input", "value"),
    State({"type": "weight-input", "index": dash.ALL}, "value"),
    State("food-search-store", "data"),
)
def handle_meals(manual_clicks, search_clicks, meal_name, calories, weights, search_data):
    msg = ""

    # Manual entry
    if manual_clicks and meal_name and calories is not None:
        save_meal(current_user.id, meal_name, calories)
        msg = f"✅ Meal added: {meal_name} ({calories} kcal)"

    # Search + weight logging
    if search_clicks and any(search_clicks):
        idx = [i for i, n in enumerate(search_clicks) if n][-1]
        weight = weights[idx]
        food = search_data[idx]

        food_name = food["description"]
        kcal_per_100g = next(
            (nutr["value"] for nutr in food.get("foodNutrients", []) if nutr["nutrientName"] == "Energy"), 0
        )
        total_kcal = round(kcal_per_100g * weight / 100, 1)
        save_meal(current_user.id, food_name, total_kcal)
        msg = f"✅ Logged {weight}g of {food_name} ({total_kcal} kcal)"

    # Fetch meals + build table/graph (same as before)
    data = get_user_meals()
    data_sorted = sorted(data, key=lambda row: row["Date"])
    
    import plotly.graph_objects as go
    import pandas as pd
    
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
            xaxis_type="category",
            xaxis_title="Date",
            yaxis_title="Calories",
            margin=dict(l=20, r=20, t=30, b=20),
            template="simple_white"
        )
    else:
        fig = go.Figure()

    return msg, data_sorted, fig


@dash.callback(
    Output("food-search-store", "data"),
    Output("food-results", "children"),
    Input("search-btn", "n_clicks"),
    State("food-query", "value"),
    prevent_initial_call=True
)
def search_food(n_clicks, query):
    if not query:
        return [], dbc.Alert("Please enter a food name", color="warning")
    
    resp = query_usda_info(query)
    if resp.status_code != 200:
        return [], dbc.Alert("Error fetching data", color="danger")
    
    foods = resp.json().get("foods", [])
    if not foods:
        return [], dbc.Alert("No results found", color="info")
    
    # Build cards with weight input + log button
    cards = []
    for idx, food in enumerate(foods):
        desc = food.get("description", "Unknown")
        kcal = next((nutr["value"] for nutr in food.get("foodNutrients", [])
                    if nutr["nutrientName"] == "Energy"), 0)
        cards.append(
            dbc.Card(
                dbc.CardBody([
                    html.H5(desc, className="card-title"),
                    html.P(f"Calories (per 100g): {kcal}", className="card-text"),
                    dbc.InputGroup([
                        dbc.Input(id={"type": "weight-input", "index": idx}, type="number", placeholder="Weight (g)"),
                        dbc.Button("Log food", id={"type": "log-btn", "index": idx}, color="success"),
                    ]),
                    html.Div(id={"type": "log-output", "index": idx})
                ]),
                className="mb-2"
            )
        )
    return foods, dbc.Row([dbc.Col(c, width=12) for c in cards])

layout = serve_layout