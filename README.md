# ULTIMATE RANKINGS
Ultimate Rankings- a Python project designed to determine the statistically best NBA players ever.

## Table of contents
- [General info](#general-info)
- [Technologies](#technologies)
- [Requirements](#requirements)
- [Setup](#setup)
- [Status](#status)

## General info
It's a website containing 6 different tables, each with a different method of evaluating the players. 

Player's are ranked by their Overall in all 4 ultimate tables, and by Points/Min in top scorers tables. Only those who played at least 10 minutes a game are considered.

Overall is counted using a player's career per minute stats, from both regular seasons and playoffs. It is a result of adding a player's positive stats multiplied by their weights, and subtracting the negative ones, also multiplied by their weights:
* OVRL = UPTS * WEIGHT + DREB * WEIGHT + OREB * WEIGHT + AST * WEIGHT + STL * WEIGHT + BLK * WEIGHT - PF * WEIGHT - TOV * WEIGHT
* OVRL - Overall
* DREB - Defensive Rebounds
* OREB - Offensive Rebounds
* AST - Assists
* STL - Steals
* BLK - Blocks
* PF - Personal Fouls
* TOV - Turnovers
* UPTS - Ultimate Points (explained below, takes all scoring stats into account)

If the player's Offensive and Defensive Rebounds don't match the Total Rebounds- total rebounds are used instead. Such errors could take place when a player started his career before 1973-74 season, when the NBA started tracking rebounds separately.

Ultimate Points are Points times True Shooting Percentage, an accuracy rating taking into account all types of shots (3p, 2p, 1p) as well as the fact that sometimes a player only shoots 1 Free Throw, and sometimes 2 (the 0.44 multiplier):
* UPTS = PTS * TS%
* PTS - Points
* TS% - True Shooting Percentage
* TS% = PTS / (2 * (FGA + 0.44 * FTA))
* FGA - Field Goal Attempts
* FTA - Free Throw Attempts

Now the weights. Winning a championship is assumed as the ultimate goal of participation in any sports league. So for each season, each champions' stat was compared to the league average- the better the winners were at something than the rest- the more important it was in succeeding and the bigger this stat's weight. And vice versa, the poorer the victors scored in something than the rest- the less significant it was in their success and the smaller this stat's weight:
#### POSITIVE STATS:
* WEIGHT = CHAMPIONS' STAT / LEAGUE AVERAGE
#### NEGATIVE STATS:
* WEIGHT = LEAGUE AVERAGE / CHAMPIONS' STAT

Final weight of each stat is the average value from all seasons.

Simpler Version rankings are basically the same, only they take less stats into account. Namely Steals, Turnovers and Blocks are removed from the formula, and Total Rebounds are used instead of Defensive and Offensive separately- all the removed stats weren't tracked untill 1973-74 season.

Finally, the Height Adjusted rankings- In Top Scorers Lists all stats are divided by the player's height. In Ultimate Players Lists Overall is divided by the player's height.

Please bear in mind that statistics are representative only of the actually quantifiable input a player has in their team's success. They do not take into account plenty of the game's nuances.

But they're a pretty good indicator nonetheless.

The same description can be found on the page, under tab 'Math'.

There are 2 files containing all the logic behind analyzing the statistics:
1. ultimaterankings/ultimaterankings/home/stats.py
2. ultimaterankings/ultimaterankings/home/topscorers.py

I was able to fetch all the necessary data from nba.com using nba_api (https://github.com/swar/nba_api, https://pypi.org/project/nba-api/). The framework I chose to make it all work is Django.

## Technologies
- Python
- nba_api
- Pandas
- PostgreSQL
- SQLAlchemy
- Django
- HTML

## Requirements
To run this project on your computer you need to have installed:
- Python 3
- An IDE (preferably VS Code- other editors might not support all the necessary libraries)
- Additional packages- instruction in the 'Setup' section
- Postgres (if you want to run stats.py or topscorers.py)


## Setup
To run the website on a local server do the following:
- Download a zip file of the project (under green tab 'code') and unpack it
- Open the project in an IDE
- Open up a terminal
- Change directory to ultimaterankings- in the terminal type 'cd ultimaterankings' and press Enter
- Now the path should look like: PS C:\Users\...\ultimaterankings_local\ultimaterankings> 
- Install all the required packages- in the terminal type 'pip install -r requirements.txt' and press Enter
- Run the local server- in the terminal type 'python manage.py runserver' and press Enter
- Now the page can be viewed in your internet browser at http://127.0.0.1:8000/


## Status
The project in its current form is ready and operational, but there will be further modifications.
Next step will be to host the website somewhere, so no programs other than a browser are necessary to view it.
Once it's done I'll also automate the rankings to update themselves with fresh stats every week during NBA seasons.
I also have some new ideas on playing with the data, for example calculating when and in what conditions is it worth to foul the opposing team's shooter. Something like, if you're down by 13 with 2.5 minutes remaining in the 4th quarter, and the attacker shoots free throws at 78%, is it worth fouling him if he has an open layup, is it worth if he's shooting from mid-range (naturally field goal percentages from different areas of the court also need to be included), etc. And the same thing for any input you can think of.





