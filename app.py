import os
from flask import Flask, request, redirect, session
from flask_login import login_user, LoginManager, UserMixin, logout_user, current_user

import dash
from dash import dcc, html, Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from utils.login_handler import restricted_page
import dash_bootstrap_components as dbc
from utils.database_connection import get_db_connection
import bcrypt

import sqlite3

# Exposing the Flask Server to enable configuring it for logging in
server = Flask(__name__)

@server.route('/login', methods=['POST'])
def login_button_click():
    if request.form:
        username = request.form['username']
        password = request.form['password']


        if check_login(username, password) is None:
            return """invalid username and/or password <a href='/login'>login here</a>"""
        if check_login(username, password):
            login_user(User(username))
            if 'url' in session:
                if session['url']:
                    url = session['url']
                    session['url'] = None
                    return redirect(url) ## redirect to target url
            return redirect('/') ## redirect to home
        return """invalid username and/or password <a href='/login'>login here</a>"""


def check_login(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT username, password FROM users WHERE username = %s",
        (username,)
    )
    user = cur.fetchone()
    conn.commit()
    conn.close()

    if bcrypt.checkpw(password.encode("utf-8"), user[1].encode("utf-8")):
        return user
    else:
        return None

app = dash.Dash(
    __name__, server=server, use_pages=True, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# Updating the Flask Server configuration with Secret Key to encrypt the user session cookie
server.config.update(SECRET_KEY="igjiogjreigjre")

# Login manager object will be used to login / logout users
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"


class User(UserMixin):
    # User data model. It has to have at least self.id as a minimum
    def __init__(self, username):
        self.id = username


@login_manager.user_loader
def load_user(username):
    """This function loads the user by user id. Typically this looks up the user from a user database.
    We won't be registering or looking up users in this example, since we'll just login using LDAP server.
    So we'll simply return a User object with the passed in username.
    """
    return User(username)


app.layout = html.Div(
    [
        dcc.Location(id="url"),
        dbc.NavbarSimple([ 
            dbc.DropdownMenu(
                    label="Calculators",
                    nav=True,
                    in_navbar=True,
                    children=[
                        dbc.DropdownMenuItem("BMR", href="/basal-metabolic-rate"),
                        dbc.DropdownMenuItem("BMI", href = '/bmi'),
                        dbc.DropdownMenuItem("One Rep Max", href = '/one-rep-max')
                    ],
            ),
            dbc.DropdownMenu(
                label = "Input",
                nav = True,
                in_navbar = True,
                children = [
                    dbc.DropdownMenuItem("Weight Input", href = "/weight-input"),
                    dbc.DropdownMenuItem("Calorie Tracker", href = '/calorietracker'),
                    dbc.DropdownMenuItem("Macros Tracker", href = '/macros')
                ]
            ),
            dbc.NavItem(dbc.NavLink(id="user-status-header")),
        ],
            brand="FitSync",
            brand_href="/",
            color="black",
            dark=True,
            fixed = 'top'),
        html.Hr(),
        dash.page_container,
    ]
)


@app.callback(
    Output("user-status-header", "children"),
    Output("user-status-header", "href"),
    Output('url','pathname'),
    Input("url", "pathname"),
    Input({'index': ALL, 'type':'redirect'}, 'n_intervals')
)
def update_authentication_status(path, n):
    ### logout redirect
    if n:
        if not n[0]:
            return '', '', dash.no_update
        else:
            return '', '', '/login'

    ### test if user is logged in
    if current_user.is_authenticated:
        if path == '/login':
            return dcc.Link("logout", href="/logout"), '/'
        return "Logout", "/logout", dash.no_update
    else:
        ### if page is restricted, redirect to login and save path
        if path in restricted_page:
            session['url'] = path
            return "Login", "/login", '/login'

    ### if path not login and logout display login link
    if current_user and path not in ['/login', '/logout']:
        return "Login", "/login", dash.no_update

    ### if path login and logout hide links
    if path in ['/login', '/logout']:
        return '', '', dash.no_update



if __name__ == "__main__":
    app.run(debug=True)

