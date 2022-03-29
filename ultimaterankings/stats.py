"""
Here I'm fetching all teams' stats from all seasons, and apply the formula to figure out their weights.
Then I'm saving the results in the database. The sleepers are here to avoid timeouts that might occur.
"""

import time

import pandas as pd
from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamyearbyyearstats
from sqlalchemy import create_engine
from haslo import haslo_postgres


custom_headers = {'Host': 'stats.nba.com', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0', 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate, br', 'x-nba-stats-origin': 'stats', 'x-nba-stats-token': 'true', 'Connection': 'keep-alive', 'Referer': 'https://stats.nba.com/', 'Pragma': 'no-cache', 'Cache-Control': 'no-cache'}

all_teams = teams.get_teams()
time.sleep(2)

all_seasons = []
# creating an empty list to fill with all seasons

boston_stats = teamyearbyyearstats.TeamYearByYearStats(team_id = 1610612738)
boston_stats = boston_stats.get_dict()
time.sleep(2)
# obtaining a dict of Boston's yearbyyear reg season stats to get a list of all seasons ever
# Boston played every single season from the beginning so it's reliable
for rowset in boston_stats['resultSets'][0]['rowSet']:
    all_seasons.append(rowset[3])
    # adding every season to all_seasons list

all_seasons.reverse()

stats_weights = {}
# creating an empty dict to fill with stats' weights
for season in all_seasons:
    season_average_stats = {}
    season_champion_stats = {}
    # creating empty dicts for seaon's average and champion stats, to later compare them
    stats_weights[season] = {}
    # creating an empty dict within the stats_weights dict, to store that season's each stat's weight in

    a = 0
    # creating a counter to keep track of how many teams participated in the season
    for team in all_teams:
        team_stats = teamyearbyyearstats.TeamYearByYearStats(team_id = team['id'])
        team_stats = team_stats.get_dict()
        # obtaining a dict of team's year by year stats

        for rowset in team_stats['resultSets'][0]['rowSet']:
            if rowset [3] == season:
            # checking if the team participated in the season
                a += 1
                team_year_stats = {}
                for i in range(len(team_stats['resultSets'][0]['headers'][15:-1])):
                    if team_stats['resultSets'][0]['headers'][15:-1][i] not in ['FG_PCT', 'FG3_PCT', 'FT_PCT']:
                        team_year_stats[team_stats['resultSets'][0]['headers'][15:-1][i]] = rowset[i + 15]/ rowset[4]
                    else:
                        team_year_stats[team_stats['resultSets'][0]['headers'][15:-1][i]] = rowset[i + 15]
                # obtaining the team's stats, only those also accounted to players

                if team_year_stats['FGA'] != 0 and team_year_stats['FTA'] != 0:
                    team_year_stats['TS%'] = team_year_stats['PTS'] / (2 * (team_year_stats['FGA'] + 0.44 * team_year_stats['FTA']))
                    team_year_stats['UPTS'] = team_year_stats['PTS'] * team_year_stats['TS%']
                else:
                    team_year_stats['TS%'] = 0
                    team_year_stats['UPTS'] = 0
                # adding True Shooting % to the stats, it takes into account al types of shots (FT, 3pt, 2pt)
                # adding Ultimate Points, so the amount of points scored multiplied by the efficiency of shots
                

                for key in team_year_stats:
                    if key in season_average_stats:
                        season_average_stats[key] += team_year_stats[key]
                    else:
                        season_average_stats[key] = team_year_stats[key]
                        # adding the team's stats to the average
                if rowset[14] == 'LEAGUE CHAMPION':
                    for key in team_year_stats:
                        season_champion_stats[key] = team_year_stats[key]
                        # if the team won the ring, adding their stats to the champion stats
                    
        time.sleep(2)

    for k, v in season_average_stats.items():
        season_average_stats[k] = v / a
        # dividing the league totals per each stat by the number of teams
    if season_champion_stats == {}:
        season_champion_stats = season_average_stats
        # for when no champion is available (season still going on) in the statistics
    for k, v in season_average_stats.items():
        if k not in ['TOV', 'PF']:
            try:
                stats_weights[season][k] = season_champion_stats[k] / season_average_stats[k]
                # adding each 'positive' stat's weight for the season
            except ZeroDivisionError:
                stats_weights[season][k] = 0
                # in case the stat isn't available
        else:
            try:
                stats_weights[season][k] = season_average_stats[k] / season_champion_stats[k]
                # adding each 'negative' stat's weight for the season
            except ZeroDivisionError:
                stats_weights[season][k] = 0
                # in case the stat isn't available
    time.sleep(2)       


stats_weights_final = {}
# creating an empty weights dict to fill with final weights
zero_stats = {}
# creating an empty dict to keep track of how many times each stat isn't available

for season in stats_weights.values():
    for k, v in season.items():
        if v == 0:
            if k in zero_stats:
                zero_stats[k] += 1
            else:
                zero_stats[k] = 1
            # tracking how many times a stat isn't available (not all were always counted), to later
            # consider that amount in calculating all the weights' average values over time
        if k in stats_weights_final:
            stats_weights_final[k] += v
        else:
            stats_weights_final[k] = v
        # adding each stat's weight from each season to the final weights dict

for k, v in stats_weights_final.items():
    if k in zero_stats.keys():
        try:
            stats_weights_final[k] = v / (len(stats_weights) - zero_stats[k])
        except ZeroDivisionError:
            stats_weights_final[k] = 0
    else:
        stats_weights_final[k] = v / len(stats_weights)
    # averaging the weight values in final weights dict- dividing the sum of all seasons' all stats' weights
    # by the amount of seasons the stat was available in


print(stats_weights)
print(stats_weights_final)

stats_weights_df = pd.DataFrame(stats_weights)
stats_weights_final_df = pd.DataFrame.from_dict([stats_weights_final])
# turning the stats_weights_final dict into a dataframe

print(stats_weights_df)
print(stats_weights_final_df)


engine = create_engine('postgresql://postgres:' + haslo_postgres + '@localhost:5432/ultimate_rankings')
stats_weights_df.to_sql('stats_weights_df_test_4', engine, index=True)
stats_weights_final_df.to_sql('stats_weights_final_df_test_4', engine, index=False, index_label='id')


engine.dispose()
# closing the engine