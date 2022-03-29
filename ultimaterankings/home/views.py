
from django.shortcuts import render
import pandas as pd






top_scorers = pd.read_csv("top_scorers.csv")
pd.set_option('max_colwidth', 5)
top_scorers.index = range(1, len(top_scorers) + 1)
top_scorers = top_scorers.to_html(col_space=1)
text_file = open("templates/topscorers.html", "r+")
text_file.truncate()
text_file.write('<body bgcolor="f85f18">{% block content %}<center><h1>The Top 50 NBA Scorers of All Time</h1>' + top_scorers + '</center>{% endblock %}')
text_file.close()

top_scorers_ha = pd.read_csv("top_scorers_ha.csv")
pd.set_option('max_colwidth', 5)
top_scorers_ha.index = range(1, len(top_scorers_ha) + 1)
top_scorers_ha = top_scorers_ha.to_html(col_space=1)
text_file = open("templates/topscorersha.html", "r+")
text_file.truncate()
text_file.write('<body bgcolor="f85f18">{% block content %}<center><h1>The Top 50 NBA Scorers of All Time, Adjusted by Height</h1>' + top_scorers_ha + '</center>{% endblock %}')
text_file.close()



ultimate_players = pd.read_csv("ultimate_players.csv")
pd.set_option('max_colwidth', 5)
ultimate_players.index = range(1, len(ultimate_players) + 1)
ultimate_players = ultimate_players.to_html(col_space=1)
text_file = open("templates/ultimateplayers.html", "r+")
text_file.truncate()
text_file.write('<body bgcolor="f85f18">{% block content %}<center><h1>The Ultimate 50 Best NBA Players of All Time</h1>' + ultimate_players + '</center>{% endblock %}')
text_file.close()



ultimate_players_ha = pd.read_csv("ultimate_players_ha.csv")
pd.set_option('max_colwidth', 5)
ultimate_players_ha.index = range(1, len(ultimate_players_ha) + 1)
ultimate_players_ha = ultimate_players_ha.to_html(col_space=1)
text_file = open("templates/ultimateplayersha.html", "r+")
text_file.truncate()
text_file.write('<body bgcolor="f85f18">{% block content %}<center><h1>The Ultimate 50 Best NBA Players of All Time, Adjusted by Height</h1>' + ultimate_players_ha + '</center>{% endblock %}')
text_file.close()



ultimate_players_oa = pd.read_csv("ultimate_players_oa.csv")
pd.set_option('max_colwidth', 5)
ultimate_players_oa.index = range(1, len(ultimate_players_oa) + 1)
ultimate_players_oa = ultimate_players_oa.to_html(col_space=1)
text_file = open("templates/ultimateplayersoa.html", "r+")
text_file.truncate()
text_file.write('<body bgcolor="f85f18">{% block content %}<center><h1>The Ultimate 50 Best NBA Players of All Time Simpler Formula</h1>' + ultimate_players_oa + '</center>{% endblock %}')
text_file.close()



ultimate_players_oa_ha = pd.read_csv("ultimate_players_oa_ha.csv")
pd.set_option('max_colwidth', 5)
ultimate_players_oa_ha.index = range(1, len(ultimate_players_oa_ha) + 1)
ultimate_players_oa_ha = ultimate_players_oa_ha.to_html(col_space=1)
text_file = open("templates/ultimateplayersoaha.html", "r+")
text_file.truncate()
text_file.write('<body bgcolor="f85f18">{% block content %}<center><h1>The Ultimate 50 Best NBA Players of All Time Adjusted by Height Simpler Formula</h1>' + ultimate_players_oa_ha + '</center>{% endblock %}')
text_file.close()
# reading data from csv files, turning it into dataframes, and then into html



def home(request):
    return render(request, 'index.html')


def topscorers(request):
    return render(request, 'topscorers.html', {'top_scorers' : top_scorers})


def topscorersha(request):
    return render(request, 'topscorersha.html', {'top_scorers_ha' : top_scorers_ha})


def ultimateplayers(request):
    return render(request, 'ultimateplayers.html', {'ultimate_players' : ultimate_players})


def ultimateplayersha(request):
    return render(request, 'ultimateplayersha.html', {'ultimate_players_ha' : ultimate_players_ha})


def ultimateplayersoa(request):
    return render(request, 'ultimateplayersoa.html', {'ultimate_players_oa' : ultimate_players_oa})


def ultimateplayersoaha(request):
    return render(request, 'ultimateplayersoaha.html', {'ultimate_players_oa_ha' : ultimate_players_oa_ha})


def math(request):
    return render(request, 'math.html')

# rendering the html pages
