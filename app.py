import os
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, jsonify, make_response
from flask.sessions import NullSession
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import MethodNotAllowed, default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from helpers import apology, login_required, lookup, usd
import argparse
import os
import requests
from serpapi import GoogleSearch
from cs50 import SQL

api_keyy = os.environ.get("api_keyy")
params = {
  "api_key": api_keyy,
  "engine": "google",
  "q": "premier league results",
  "location": "Austin, Texas, United States",
  "google_domain": "google.com",
  "gl": "au",
  "hl": "en"
}


search = GoogleSearch(params)
results = search.get_dict()


# parser = argparse.ArgumentParser(description='Sample V4')
# parser.add_argument('--api-key', type=str, default='')
# args = parser.parse_args()

api_key = os.environ.get("api_key")

SPORT = 'soccer_epl' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports

REGIONS = 'au' # uk | us | eu | au. Multiple can be specified if comma delimited

MARKETS = 'h2h' # h2h | spreads | totals. Multiple can be specified if comma delimited

ODDS_FORMAT = 'decimal' # decimal | american

DATE_FORMAT = 'iso' # iso | unix


sports_response = requests.get('https://api.the-odds-api.com/v4/sports', params={
    'api_key': api_key
})


'''if sports_response.status_code != 200:
    print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')

else:
    print('List of in season sports:', sports_response.json())
'''

odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds', params={
    'api_key': api_key,
    'regions': REGIONS,
    'markets': MARKETS,
    'oddsFormat': ODDS_FORMAT,
    'dateFormat': DATE_FORMAT,
})


# if odds_response.status_code != 200:
#     print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')

# else:
#     odds_json = odds_response.json()
#     print('Number of events:', len(odds_json))

#     # Check the usage quota
#     print('Remaining requests', odds_response.headers['x-requests-remaining'])
#     print('Used requests', odds_response.headers['x-requests-used'])



app = Flask(__name__)

app.jinja_env.filters["usd"] = usd

app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

conn = SQL(os.environ.get("DATABASE_URL")) 


''' -------------------- THIS IS THE ODDS API'S GAMES INSERTING INTO THE DATABASE --------------------'''
team_map = {
    "Everton": "Everton",
    "Chelsea": "Chelsea",
    "Liverpool": "Liverpool",
    "Brentford": "Brentford",
    "Leicester City": "Leicester City",
    "Aston Villa": "Aston Villa",
    "Arsenal": "Arsenal",
    "Crystal Palace": "Crystal Palace",
    "Southampton": "Southampton",
    "Watford" : "Watford",
    "Leeds United": "Leeds United",
    "Burnley": "Burnley",
    "Norwich City": "Norwich City",
    "Wolverhampton Wanderers": "Wolves",
    "Manchester United": "Man United",
    "Brighton and Hove Albion": "Brighton",
    "Newcastle United": "Newcastle",
    "West Ham United": "West Ham",
    "Tottenham Hotspur": "Tottenham",
    "Manchester City": "Man City",
    "Draw": "Draw"
}

matches = []
for game in odds_response.json():
    for bookmaker in game["bookmakers"]:
        if bookmaker['key'] == 'sportsbet':
            for i in range(len(bookmaker["markets"][0]["outcomes"])):
                bad_name = bookmaker["markets"][0]["outcomes"][i]["name"]
                good_name = team_map[bad_name]
                bookmaker["markets"][0]["outcomes"][i]["name"] = good_name
                
            matches.append([{"start_date": game["commence_time"].split("T")[0]}, bookmaker["markets"][0]["outcomes"]])

for match in matches:
    rows = conn.execute("SELECT id FROM games WHERE home_team = ? AND away_team = ? AND date = ?", match[1][0]["name"], match[1][1]["name"], match[0]["start_date"])
    
    conn.execute("UPDATE games SET home_team_odds = ? WHERE home_team = ? AND away_team = ? AND date = ?", match[1][0]["price"], match[1][0]["name"], match[1][1]["name"], match[0]["start_date"])
    conn.execute("UPDATE games SET away_team_odds = ? WHERE home_team = ? AND away_team = ? AND date = ?", match[1][1]["price"], match[1][0]["name"], match[1][1]["name"], match[0]["start_date"])
    conn.execute("UPDATE games SET draw_odds = ? WHERE home_team = ? AND away_team = ? AND date = ?", match[1][2]["price"], match[1][0]["name"], match[1][1]["name"], match[0]["start_date"])

    match[1][:-1].sort(key=lambda team: team["name"])
    
    values = (match[1][0]["name"], match[1][1]["name"], match[1][2]["name"], match[1][0]["price"], match[1][1]["price"], match[1][2]["price"], match[0]["start_date"])

    if len(rows) == 0:
        conn.execute("INSERT INTO games (home_team, away_team, draw, home_team_odds, away_team_odds, draw_odds, date) VALUES(?, ?, ?, ?, ?, ?, ?)", (values))

''' -------------------- THIS IS THE SERPAPI'S RESULTS INSERTING INTO THE DATABASE --------------------'''
results_matches = []
for outcomes in results["sports_results"]["games"]:
    if outcomes["status"] == "FT":
        input_date = outcomes["date"]
        input_with_year = f"{input_date} {datetime.today().year}"
        input_format = "%a, %d %b %Y"

        try: 
            date = datetime.strptime(input_with_year, input_format).date()
        except ValueError:
            input_with_year = f"{input_date} {datetime.today().year}"
            if input_with_year[:5] == "Today":
                date = datetime.today().date()
            elif input_with_year[:9] == "Yesterday":
                today = datetime.today().date()
                date = today - timedelta(days=1)
            else:
                date = datetime.strptime(input_with_year, input_format).date()

        for outcome in outcomes['teams']:
            if outcome.get("thumbnail"):
                del outcome['thumbnail']

        results_matches.append([{"begin_date": date.isoformat()}, outcomes["teams"]])


games_rows = conn.execute("SELECT home_team, away_team, date, id FROM games")

for game_row in games_rows:

    for results_outcome in results_matches:
        status = False
        f = "%Y-%m-%d"
        a = datetime.strptime(results_outcome[0]["begin_date"], f)  #datetime
        b = timedelta(days=1)

        results_outcome[1].sort(key=lambda team: team["name"])
       

        results_teams = (results_outcome[1][0]["name"], results_outcome[1][1]["name"])
        games_teams = (game_row[0], game_row[1])

        #print(games_teams,game_row[2], results_teams, results_outcome[0]["begin_date"])

        if set(games_teams) == set(results_teams) and game_row[2] == results_outcome[0]["begin_date"] or set(games_teams) == set(results_teams) and game_row[2] == ((a+b).strftime(f)) or set(games_teams) == set(results_teams) and game_row[2] == ((a-b).strftime(f)):
            print("FOUND")

            results_date_compare = conn.execute("SELECT home_team_results, away_team_results, home_team_score, away_team_score FROM results WHERE home_team_results = ? AND away_team_results = ? AND home_team_score = ? AND away_team_score = ?", (results_outcome[1][0]["name"], results_outcome[1][1]["name"], results_outcome[1][0]["score"], results_outcome[1][1]["score"]))
            comparison = (results_outcome[1][0]["name"], results_outcome[1][1]["name"], int(results_outcome[1][0]["score"]), int(results_outcome[1][1]["score"]))
            
            
            results_days_compare = conn.execute("SELECT results_date FROM results WHERE home_team_results = ? AND away_team_results = ? AND home_team_score = ? AND away_team_score = ? ", (results_outcome[1][0]["name"], results_outcome[1][1]["name"], results_outcome[1][0]["score"], results_outcome[1][1]["score"]))
            if results_days_compare:
                days_before = datetime.strptime(results_days_compare[0][0], f)
                days_after = timedelta(days=15)

            
            results_rows = conn.execute("SELECT id FROM results WHERE home_team_results = ? AND away_team_results = ? AND results_date = ?", (results_outcome[1][0]["name"], results_outcome[1][1]["name"], results_outcome[0]["begin_date"]))
            results_values = (results_outcome[1][0]["name"], results_outcome[1][1]["name"], results_outcome[1][0]["score"], results_outcome[1][1]["score"], results_outcome[0]["begin_date"], game_row[3], status)

            if len(results_rows) == 0:
                if comparison in results_date_compare and days_before.date() > days_before.date() + days_after or comparison not in results_date_compare:
                    print("inserted")
                    conn.execute("INSERT INTO results (home_team_results, away_team_results, home_team_score, away_team_score, results_date, game_id, status) VALUES(?, ?, ?, ?, ?, ?, ?)", (results_values))

@app.route("/index")
@login_required
def index():
    # conn = SQL(os.environ.get("DATABASE_URL")) 

    # Display User Cash and Username on the Navbar
    
    layout_user = conn.execute("SELECT username FROM users WHERE id = ?", (session["user_id"], ))
    session["username"] = layout_user[0]

    
    layout_balance = conn.execute("SELECT cash FROM users WHERE id = ?", (session["user_id"],))
    session["balance"] = layout_balance[0]
    
    
    history_rows_index = conn.execute("SELECT bet_name, bet_amount, transaction_date, odds, potential_payout, home_team_history, away_team_history, match_date, winner, h_results_id, id FROM history WHERE username_id = ?", (session["user_id"],))

    
    history_rows = conn.execute("SELECT bet_name, bet_amount, transaction_date, odds, potential_payout, home_team_history, away_team_history, match_date, winner, r.home_team_results, r.away_team_results, r.home_team_score, away_team_score, status, h.id FROM history h JOIN results r ON r.id = h.h_results_id and h.username_id = ?", (session["user_id"],))
    
    pending_bet = True
    winner = False
 
    
    balance = conn.execute("SELECT cash FROM users WHERE id = ?", (session["user_id"],))
    total = 0
    for history in history_rows:
        if history[8] == 0:
            if history[0] == history[9]:
                if history[11] > history[12]:
                    print(f"THE PAYOUT IS {history[4]}")
                    print(history[11], history[12])
                    total += history[4]
                    print(f"THIS IS THE TOTAL {total} FOR HOME")
                    winner = True
                    pending_bet = False
                    total_balance = total + balance[0][0]
                    conn.execute("UPDATE users SET cash = ? WHERE id = ?", (round(total_balance, 2), session["user_id"]))
                    
                    conn.execute("UPDATE history SET winner = 1 WHERE winner = 0 AND home_team_history = ? AND away_team_history = ? AND match_date = ? AND potential_payout = ? AND id = ? AND username_id = ?", (history[5], history[6], history[7], history[4], history[14], session["user_id"]))
                    
                    conn.execute("UPDATE results SET status = 1 WHERE status = 0 AND home_team_results = ? AND away_team_results = ? AND results_date = ?", (history[9], history[10], history[7]))
                    
 
            elif history[0] == history[10]:
 
                if history[12] > history[11]:
                    print(f"THE PAYOUT IS {history[4]}")
                    print(history[11], history[12])
                    total += history[4]
                    print(f"THIS IS THE TOTAL {total} FOR AWAY")
                    winner = True
                    pending_bet = False
                    total_balance = total + balance[0][0]
                    conn.execute("UPDATE users SET cash = ? WHERE id = ?", (round(total_balance, 2), session["user_id"]))

                    conn.execute("UPDATE history SET winner = 1 WHERE winner = 0 AND home_team_history = ? AND away_team_history = ? AND match_date = ? AND potential_payout = ? AND id = ? AND username_id = ?", (history[5], history[6], history[7], history[4], history[14], session["user_id"]))

                    conn.execute("UPDATE results SET status = 1 WHERE status = 0 AND home_team_results = ? AND away_team_results = ? AND results_date = ?", (history[9], history[10], history[7]))
 
            elif history[0] == "Draw":
 
                if history[11] == history[12]:
                    print(f"THE PAYOUT IS {history[4]}")
                    print(history[11], history[12])
                    print("PASSED")
                    print(balance[0][0], history[4])
                    total += history[4]
                    print(f"THIS IS THE TOTAL {total} FOR DRAW")
                    winner = True
                    pending_bet = False
                    total_balance = total + balance[0][0]
                    conn.execute("UPDATE users SET cash = ? WHERE id = ?", (round(total_balance, 2), session["user_id"]))
                   
                    conn.execute("UPDATE history SET winner = 1 WHERE winner = 0 AND home_team_history = ? AND away_team_history = ? AND match_date = ? AND potential_payout = ? AND id = ? AND username_id = ?", (history[5], history[6], history[7], history[4], history[14], session["user_id"]))
                    
                    conn.execute("UPDATE results SET status = 1 WHERE status = 0 AND home_team_results = ? AND away_team_results = ? AND results_date = ?", (history[9], history[10], history[7]))
                    
            # run calculation for every user that participated in that match's betting pool
    
        else:
            print("Not found")
            winner = False
            pending_bet = True
            # you already have the result for this match for this user.

    
    history_data = conn.execute("SELECT h.home_team_history, h.away_team_history, h.match_date, r.id, r.home_team_results, r.away_team_results, r.results_date FROM history h LEFT OUTER JOIN results r ON h.h_results_id = r.id WHERE r.id IS NULL")
    
    
    history_results = conn.execute("SELECT id, home_team_results, away_team_results, results_date FROM results")
    
    results_id = 0
    for j in history_data:
        for k in history_results:
            f_results = "%Y-%m-%d"
            a_results = datetime.strptime(k[3], f)  #datetime
            b_results = timedelta(days=1)
            c_results = a_results.date() - b_results

            history_results_team = (k[1], k[2])
            history_matches_team = (j[0], j[1])
            #print(set(history_results_team), k[3], set(history_matches_team), j[2])
            
            if set(history_results_team) == set(history_matches_team) and k[3] == j[2] or set(history_results_team) == set(history_matches_team) and str(c_results) == j[2]:
                results_id = k[0]
                print(results_id)
                print("RESULTS ID HAVE BEEN FOUND")
                conn.execute("UPDATE history SET h_results_id = ? WHERE home_team_history = ? AND away_team_history = ? AND match_date = ? AND username_id = ?", (results_id, j[0], j[1], j[2], session["user_id"]))
                
    return render_template("index.html", balance=balance, history_rows=history_rows, history_rows_index=history_rows_index, pending_bet=pending_bet, winner=winner)


@app.route("/")
def homepage():
    return render_template("homepage.html")



@app.route("/soccer", methods=["GET", "POST"])
@login_required
def soccer():

    matches_list = []

    # conn = SQL(os.environ.get("DATABASE_URL")) 

    
    matches_games_db = conn.execute("SELECT g.home_team, g.away_team, g.draw, g.date, g.home_team_odds, g.away_team_odds, g.draw_odds, g.id, r.home_team_results, r.away_team_results, r.results_date FROM games g LEFT OUTER JOIN results r ON g.id = r.game_id WHERE r.id is null;")

    
    matches_home = conn.execute("SELECT g.home_team, g.away_team, g.date, g.home_team_odds FROM games g LEFT OUTER JOIN results r ON g.id = r.game_id WHERE r.id is null;")
    
    matches_away = conn.execute("SELECT g.away_team, g.home_team, g.date, g.away_team_odds FROM games g LEFT OUTER JOIN results r ON g.id = r.game_id WHERE r.id is null;")
    
    matches_draw = conn.execute("SELECT g.draw, g.home_team, g.away_team, g.date, g.draw_odds FROM games g LEFT OUTER JOIN results r ON g.id = r.game_id WHERE r.id is null;")

    for i in matches_games_db:
        for j in matches:
            values_soccer_api = (j[1][0]["name"], j[1][1]["name"], j[0]["start_date"])
            values_soccer = (i[0], i[1], i[3])

            if values_soccer_api == values_soccer:
                matches_list.append(i)


    home = request.form.get("home")
    draw = request.form.get("draw")
    away = request.form.get("away")

    session["home"] = home
    session["draw"] = draw
    session["away"] = away

    if request.method == "POST":
        
        listing_home = []
        listing_draw = []
        listing_away = []

        if home:
            listing_home.append(home.split("|")[:])
            matches_home = [tuple(str(i) for i in j) for j in matches_home]

            if tuple(listing_home[0]) not in matches_home:
                flash("Data altered...Please try again!", "error")
                return redirect("/soccer")
                
        if draw:
            listing_draw.append(draw.split("|")[:])
            matches_draw = [tuple(str(i) for i in j) for j in matches_draw]

            if tuple(listing_draw[0]) not in matches_draw:
                flash("Data altered...Please try again!", "error")
                return redirect("/soccer")

        if away:
            listing_away.append(away.split("|")[:])
            matches_away = [tuple(str(i) for i in j) for j in matches_away]

            if tuple(listing_away[0]) not in matches_away:
                flash("Data altered...Please try again!", "error")
                return redirect("/soccer")


        return redirect("/checkout")
    else:
        return render_template("soccer.html", matches_list=matches_list)



@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    
    won = False

    matches_list_checkout = []

    # conn = SQL(os.environ.get("DATABASE_URL")) 

    
    matches_checkout = conn.execute("SELECT g.home_team, g.away_team, g.draw, g.date, g.home_team_odds, g.away_team_odds, g.draw_odds, g.id, r.home_team_results, r.away_team_results, r.results_date FROM games g LEFT OUTER JOIN results r ON g.id = r.game_id WHERE r.id is null;")

    for i in matches_checkout:
        matches_list_checkout.append(i)

    home_data = session["home"]
    draw_data = session["draw"]
    away_data = session["away"]

    odds_only = ""
    chosen_bet = ""
    home_team = ""
    away_team = ""
    match_date = ""

    if home_data:
        chosen_bet = chosen_bet.join(home_data.split("|")[0])
        home_team = home_team.join(home_data.split("|")[0])
        away_team = away_team.join(home_data.split("|")[1])
        match_date = match_date.join(home_data.split("|")[2])
        odds_only = home_data.split("|")[3]
        

    elif draw_data:
        chosen_bet = chosen_bet.join(draw_data.split("|")[0])
        home_team = home_team.join(draw_data.split("|")[1])
        away_team = away_team.join(draw_data.split("|")[2])
        match_date = match_date.join(draw_data.split("|")[3])
        odds_only = draw_data.split("|")[4]

    elif away_data:
        chosen_bet = chosen_bet.join(away_data.split("|")[0])
        home_team = home_team.join(away_data.split("|")[0])
        away_team = away_team.join(away_data.split("|")[1])
        match_date = match_date.join(away_data.split("|")[2])
        odds_only = away_data.split("|")[3]
    
    id = 0
    h = ""
    a = ""
    d = ""

    for event in matches_list_checkout:
        event_teams = (event[0], event[1], event[3])

        if home_data:
            h = (home_data.split("|")[0], home_data.split("|")[1],  home_data.split("|")[2])
            if set(event_teams) == set(h):
                print("FOUND")
                id = event[7]

        if draw_data:
            d = (draw_data.split("|")[1], draw_data.split("|")[2], draw_data.split("|")[3])
            if set(event_teams) == set(d):
                print("FOUND")
                id = event[7]

        if away_data:
            a = (away_data.split("|")[0], away_data.split("|")[1],  away_data.split("|")[2])            
            if set(event_teams) == set(a):
                print("FOUND")
                id = event[7]

    
    if request.method == "POST":
        
        game_id = request.form.get("hiddenval")
        
        amount = request.form.get("amount")
        
        
        rows = conn.execute("SELECT cash FROM users WHERE id = ?", (session["user_id"],))
        if rows[0][0] >= float(amount):
            place_bet = rows[0][0] - float(amount)
            conn.execute("UPDATE users SET cash = ? WHERE id = ?", (round(place_bet, 2), session["user_id"]))


            conn.execute("INSERT INTO history (bet_name, bet_amount, transaction_date, odds, potential_payout, home_team_history, away_team_history, match_date, winner, games_id, username_id) VALUES(?, ?, DATETIME('now', '-1 hours'), ?, ?, ?, ?, ?, ?, ?, ?)",
            (chosen_bet, float(amount), odds_only, float(amount) * float(odds_only), home_team, away_team, match_date, won, game_id, session["user_id"]))

            flash(f"Bet Successfully Placed on {chosen_bet} with {odds_only} odds!", "success")
            return redirect("/index")
        else:
            flash(f"Error while trying to place a bet! Current balance is {usd(rows[0][0])}!", "error")
            return redirect("/soccer")

    else:
        return render_template("checkout.html", id=id, matches=matches, chosen_bet=chosen_bet, home_data=home_data, draw_data=draw_data, away_data=away_data, odds_only=odds_only)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # conn = SQL(os.environ.get("DATABASE_URL")) 

        username = request.form.get("username")

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username!", "error")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password!", "error")
            return render_template("login.html")
            
        # Query database for username
        
        rows = conn.execute("SELECT * FROM users WHERE username = ?", (username,))

        r = []
        for row in rows:
            r.append({'id': row[0], 'username': row[1], 'hash': row[2], 'cash': row[3]})

        # Ensure username exists and password is correct
        if len(r) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            flash("Invalid username and/or password!", "error")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0][0]
        
        user = conn.execute("SELECT username FROM users WHERE id = ?", (session["user_id"],))
        # Redirect user to home page
        flash(f"Welcome, {user[0]}!", "success")
        return redirect("/index")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    username = request.form.get("username")
    password = request.form.get("password")
    
    if request.method == "POST":

        # conn = SQL(os.environ.get("DATABASE_URL")) 

        if not username:
            flash("Must provide username!", "error")
            return render_template("register.html")
        
        elif not password:
            flash("Must provide password!", "error")
            return render_template("register.html")
            
        elif password != request.form.get("confirmation"):
            flash("Password does not match!", "error")
            return render_template("register.html")
            

        rows = conn.execute("SELECT username FROM users")

        r = []
        for row in rows.fetchall():
            for i in row:
                r.append(i)

        if username not in r:

            conn.execute("INSERT INTO users (username, hash) VALUES(?, ?)", (username, generate_password_hash(password)))

        else:
            flash("Username taken!", "error")
            return render_template("register.html")
        flash("You have successfully registered!", "success")
        login()
        return redirect("/index")
    else:
        return render_template("register.html")


@app.route("/password", methods=["GET", "POST"])
def password():
    # conn = SQL(os.environ.get("DATABASE_URL")) 

    if request.method == "POST":

        np =  request.form.get("npassword")
        np_username = request.form.get("username")

        if not np_username:
            flash("Username Field Empty!", "error")
            return redirect("/password")

        if not request.form.get("cpassword"):
            flash("Password Field Empty!", "error")
            return redirect("/password")
        
        if not np:
            flash("New Password Field Empty!", "error")
            return redirect("/password")
        
        if not request.form.get("confirmation"):
            flash("Confirmation Field Empty!", "error")
            return redirect("/password")
        
        
        username_rows = conn.execute("SELECT username FROM users WHERE username = ?", (np_username,))
        
        password_rows = conn.execute("SELECT hash FROM users WHERE username = ?", (np_username,))

        if len(username_rows) != 1 or check_password_hash(password_rows[0], request.form.get("cpassword")) != True:
            flash("Invalid Username and/or Password!", "error")
            return redirect("/password")
        else:
            conn.execute("UPDATE users SET hash = ? WHERE username = ?", (generate_password_hash(np), np_username))
        
        flash("Password changed successfully!", "success")
        return redirect("/")

    return render_template("password.html")


@app.route("/leaderboard")
@login_required
def leaderboard():
    # conn = SQL(os.environ.get("DATABASE_URL")) 

    
    leaderboard_users = conn.execute("SELECT username, cash FROM users ORDER BY cash DESC")

    
    leaderboard_history = conn.execute("SELECT bet_name, bet_amount, transaction_date, odds, potential_payout, home_team_history, away_team_history, match_date, winner, h_results_id, id FROM history WHERE username_id = ?", (session["user_id"],))
    
    return render_template("leaderboard.html", leaderboard_history=leaderboard_history, leaderboard_users=leaderboard_users)

@app.route("/results")
@login_required
def results():
    # conn = SQL(os.environ.get("DATABASE_URL")) 

    
    results_html = conn.execute("SELECT home_team_results, away_team_results, home_team_score, away_team_score, results_date FROM results ORDER BY results_date DESC")

    return render_template("results.html", results_html=results_html)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

