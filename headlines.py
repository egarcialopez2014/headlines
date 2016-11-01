from flask import Flask
from flask import render_template
from flask import request
import feedparser
import json
import urllib.parse
import requests


app = Flask(__name__)

weather_API="bb187d4e324cbc5eb963d0e085b26fdc"
DEFAULTS = {"publication":"bbc", "city":"London,UK"}

RSS_FEEDS = {'bbc': "http://feeds.bbci.co.uk/news/rss.xml", 'cnn': "http://rss.cnn.com/rss/edition.rss",
             "fox": "http://feeds.foxnews.com/foxnews/latest"}




@app.route("/")
#@app.route("/<publication>")
def home():
    publication = request.args.get("publication")
    if not publication:
        publication = DEFAULTS["publication"]
    articles = get_news(publication)

    city = request.args.get("city")
    if not city:
        city = DEFAULTS["city"]
    weather = get_weather(city)

    return render_template("home.html", articles=articles, weather=weather)



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
