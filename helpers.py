import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code
    
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://api.the-odds-api.com/v4/sports/rugbyleague_nrl/odds?regions=au&oddsFormat=decimal&apiKey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        print(response.json())
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "commence_time": quote["commence_time"],
            "home_team": quote["home_team"],
            "away_team": quote["away_team"],
            "name": quote["name"],
            "price": float(quote["price"])
        }
    except (KeyError, TypeError, ValueError):
        return None

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"