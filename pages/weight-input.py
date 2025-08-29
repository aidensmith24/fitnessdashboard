import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import io
import base64
from datetime import datetime
from utils.login_handler import require_login
from flask_login import current_user

dash.register_page(__name__)
require_login(__name__)

# Temporary in-memory store (replace with DB later)
weights_data = []

def set_layout():
    from flask_login import current_user  # ensure we import within request
    if not (hasattr(current_user, "is_authenticated") and current_user.is_authenticated):
        return html.Div(["Please ", dcc.Link("login", href="/login"), " to continue"])

    return dbc.Container(
        fluid=True,
        className="p-4",
        children=[
            dbc.Row(
                [
                    # Manual entry card
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

                    # Bulk upload card
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
                                data=[],
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
def add_weight(n_clicks, weight, unit):
    if not weight:
        return "⚠️ Please enter a weight.", weights_data

    # Convert to kg if lbs selected
    if unit == "lbs":
        weight = round(weight * 0.453592, 2)

    weights_data.append(
        {"Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Weight": weight}
    )

    return "✅ Weight added successfully!", weights_data


@dash.callback(
    Output("upload-output", "children"),
    Output("weight-table", "data", allow_duplicate=True),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def upload_file(contents, filename):
    if contents is None:
        return "⚠️ No file uploaded.", weights_data

    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return (
                "❌ Unsupported file format. Please upload CSV or Excel.",
                weights_data,
            )

        if "Weight" not in df.columns:
            return "⚠️ File must have a 'Weight' column.", weights_data

        # Handle optional Unit column
        for i, row in df.iterrows():
            weight = row["Weight"]
            unit = str(row["Unit"]).lower() if "Unit" in df.columns else "kg"

            if unit == "lbs":
                weight = round(weight * 0.453592, 2)

            weights_data.append(
                {"Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Weight": weight}
            )

        return f"✅ Successfully uploaded {len(df)} records!", weights_data

    except Exception as e:
        return f"❌ Error processing file: {e}", weights_data


layout = set_layout
