from flask import Flask
from flask import render_template
from flask import request
from flask import make_response
import feedparser
import urllib.parse
import requests
import datetime



app = Flask(__name__)

weather_API="bb187d4e324cbc5eb963d0e085b26fdc"
DEFAULTS = {"publication":"bbc", "city":"London,UK"}

RSS_FEEDS = {'bbc': "http://feeds.bbci.co.uk/news/rss.xml", 'cnn': "http://rss.cnn.com/rss/edition.rss",
             "fox": "http://feeds.foxnews.com/foxnews/latest"}

def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    else:
        return DEFAULTS[key]


@app.route("/")
#@app.route("/<publication>")
def home():
    publication = get_value_with_fallback("publication")
    articles = get_news(publication)

    city = get_value_with_fallback("city")
    weather = get_weather(city)

    response = make_response(render_template("home.html", articles=articles, weather=weather))
    expires = datetime.datetime.now()+datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires = expires)
    response.set_cookie("city", city, expires = expires)
    return response



def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS["publication"]
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed["entries"]

def get_weather(query):
    query = urllib.parse.quote(query)
    api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=" + weather_API
    url = api_url.format(query)
    r = requests.get(url)
    parsed = r.json()
    weather = None
    if parsed.get("weather"):
        weather = {"description": parsed["weather"][0]["description"], "temperature":parsed["main"]["temp"],
                   "city":parsed["name"], "country":parsed["sys"]["country"]}
    return weather

if __name__ == '__main__':
    app.run(port=5000, debug=True)
