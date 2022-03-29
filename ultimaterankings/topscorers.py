"""
Here I'm fetching all player's stats and data from NBA API, fetching the stats' weights from
the database, applying the formula to determine who's the best, and saving the results to the database.
The sleepers are here to avoid timeouts that might occur.
"""
import time
import pandas as pd
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.endpoints import playercareerstats
import copy
from sqlalchemy import create_engine
from haslo import haslo_postgres



custom_headers = {'Host': 'stats.nba.com', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0', 'Accept': 'application/json, text/plain, */*', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate, br', 'x-nba-stats-origin': 'stats', 'x-nba-stats-token': 'true', 'Connection': 'keep-alive', 'Referer': 'https://stats.nba.com/', 'Pragma': 'no-cache', 'Cache-Control': 'no-cache'}

all_players = players.get_players()
time.sleep(2)
top_scorers = []
# creating an empty list to fill with dictionaries of particular players


for athlete in all_players:
    player_info = commonplayerinfo.CommonPlayerInfo(player_id = athlete['id'])
    # obtaining basic player info
    player_info = player_info.get_dict()
    # turning the info into a dictionary
    if player_info['resultSets'][0]['rowSet'][0][24] < 1951:
        continue
        # dropping all players who started playing before the 1951-52 season
        # their minutes in statistics are corrupted- minutes weren't tracked before that season
    player = {}
    # creating an empty dictionary to store the needed player data in
    player['FULLNAME'] = player_info['resultSets'][0]['rowSet'][0][3]
    # adding playeer's full name to the dict
    if player_info['resultSets'][0]['rowSet'][0][11] == '' and player['FULLNAME'] != 'Muggsy Bogues':
        player['HEIGHT'] = 2
        # adding player's height to the dict in case no value is available, default value- 2 meters
    elif player['FULLNAME'] == 'Muggsy Bogues':
        player['HEIGHT'] = 1.6
        # specially adding the all time shortest player's height - for some reason NBA doesn't hold that info
    elif player_info['resultSets'][0]['rowSet'][0][11] in ['5-10', '5-11', '6-10', '6-11']:
        if player_info['resultSets'][0]['rowSet'][0][11] == '5-10':
            player['HEIGHT'] = round(70 * 2.54 / 100, 2)
        elif player_info['resultSets'][0]['rowSet'][0][11] == '5-11':
            player['HEIGHT'] = round(71 * 2.54 / 100, 2)
        elif player_info['resultSets'][0]['rowSet'][0][11] == '6-10':
            player['HEIGHT'] = round(82 * 2.54 / 100, 2)
        elif player_info['resultSets'][0]['rowSet'][0][11] == '6-11':
            player['HEIGHT'] = round(83 * 2.54 / 100, 2)
        # adding player's height to the dict and converting to meters in case of uneasy feet values
        # no player ever was 4-11 or shorter, and none was 7-10 or taller 
        # so these are the only 4 possibilities
    else:
        player['HEIGHT'] = player_info['resultSets'][0]['rowSet'][0][11].replace('-', '.')
        height = 0
        height += float(player['HEIGHT'][0]) * 0.3048 + float(player['HEIGHT'][2]) * 0.0254
        player['HEIGHT'] = round(height, 2)
    # adding player's height to the dict, converting to meters, and turning it into a useable number

    player_stats = playercareerstats.PlayerCareerStats(player_id = athlete['id'])
    # obtaining the player career stats
    player_stats = player_stats.career_totals_regular_season.get_dict()
    # turning the player's regular season totals into a dict
    player_playoff_stats = playercareerstats.PlayerCareerStats(player_id = athlete['id'])
    # obtaining the player career stats under new name
    player_playoff_stats = player_playoff_stats.career_totals_post_season.get_dict()
    # turning the player's playoff totals into a dict
    if player_stats['data'] == [] and player_playoff_stats['data'] == []:
    # in case no stats at all are available
        continue
    del player_stats['headers'][1:3]
    # getting rid of unnecessary info (league ID, Team ID)
    if player_stats['data'] != []:
        player_stats['data'] = player_stats['data'][0]
        # turning the stats list of lists (that's how it's supplied) into just a list
        del player_stats['data'][1:3]
        # getting rid of unnecessary info (league ID, Team ID)
    
    del player_playoff_stats['headers'][1:3]
    # getting rid of unnecessary info (league ID, Team ID)    
    if player_playoff_stats['data'] != []:
        player_playoff_stats['data'] = player_playoff_stats['data'][0]
        # turning the stats list of lists (that's how it's supplied) into just a list
        del player_playoff_stats['data'][1:3]
        # getting rid of unnecessary info (league ID, Team ID)

    for i in range(len(player_stats['data'])):
        if player_stats['data'] != [] and player_stats['data'][i] is None:
            player_stats['data'][i] = 0
    # making sure all the stats are represented as numbers
    for i in range(len(player_playoff_stats['data'])):
        if player_playoff_stats['data'] != [] and player_playoff_stats['data'][i] is None:
            player_playoff_stats['data'][i] = 0
    # making sure all the stats are represented as numbers

    if player_stats['data'] != [] and player_stats['data'][3] == 0:
        continue
    if player_playoff_stats['data'] != [] and player_playoff_stats['data'][3] == 0:
        continue
        # dropping players without the amount of minutes, as there's no way to compare them
        # NBA started counting minutes in 1951-52 season

    if player_stats['data'] != [] and player_playoff_stats['data'] != []:
        if (player_stats['data'][3] + player_playoff_stats['data'][3])/ (player_stats['data'][1] + 
        player_playoff_stats['data'][1]) < 10:
            continue
    if player_stats['data'] != [] and player_playoff_stats['data'] == []:
        if player_stats['data'][3] / player_stats['data'][1] < 10:
            continue
    if player_stats['data'] == [] and player_playoff_stats['data'] != []:
        if player_playoff_stats['data'][3] / player_playoff_stats['data'][1] < 10:
            continue
        # dropping players that played less than 10 minutes per game

    i = 0
    # creating a track keeper to get both headers and their corresponding values in the right places  
    for header in player_stats['headers']:
        if header == 'PLAYER_ID':
            player[header] = player_stats['data'][i]
            # adding player ID to the playerdict
        if player_stats['data'] != [] and player_playoff_stats['data'] != []:
            # in case both reg season and playoff stats are available
            if i < 3:
                player[header] = player_stats['data'][i] + player_playoff_stats['data'][i]
                # making sure the amount of reg season games and playoff games is added, not averaged
            elif i >= 3 and header not in ['FG_PCT', 'FG3_PCT', 'FT_PCT']:
                player[header + '/MIN'] = (player_stats['data'][i] +
                player_playoff_stats['data'][i]) / (player_stats['data'][3] + player_playoff_stats['data'][3])
                # combining career totals from reg seasons and playoffs, and turning them into
                # a per minute format
            else:
                player[header] = (player_stats['data'][i] +
                player_playoff_stats['data'][i]) / 2
                # averaging shot percentages from reg seasons and playoffs
            player['MIN/GAME'] = (player_stats['data'][3] + 
            player_playoff_stats['data'][3]) / (player_stats['data'][1] + player_playoff_stats['data'][1])
        
        elif player_stats['data'] != [] and player_playoff_stats['data'] == []:
            # in case only reg season stats are available
            if i < 3:
                player[header] = player_stats['data'][i]
                # adding the amount of games to the playerdict
            elif i >= 3 and header not in ['FG_PCT', 'FG3_PCT', 'FT_PCT']:
                player[header + '/MIN'] = player_stats['data'][i] / player_stats['data'][3]
                # turning career totals from reg seasons into a per minute format
            else:
                player[header] = player_stats['data'][i]
                # adding shot percentages from reg seasons to the playerdict
            player['MIN/GAME'] = player_stats['data'][3] / player_stats['data'][1]

        elif player_stats['data'] == [] and player_playoff_stats['data'] != []:
            # in case only playoff stats are available
            if i < 3:
                player[header] = player_playoff_stats['data'][i]
                # adding the amount of games to the playerdict
            elif i >= 3 and header not in ['FG_PCT', 'FG3_PCT', 'FT_PCT']:
                player[header + '/MIN'] = player_playoff_stats['data'][i] / player_playoff_stats['data'][3]
                # turning career totals from playoffs int a per minute format
            else:
                player[header] = player_playoff_stats['data'][i]
                # adding shot percentages from playoffs to the playerdict
            player['MIN/GAME'] = player_playoff_stats['data'][3] / player_playoff_stats['data'][1]
        i += 1
    
    if player['DREB/MIN'] + player['OREB/MIN'] == player['REB/MIN']:
        player['REBS_OK'] = True
    else:
        player['REBS_OK'] = False
        # checking if player's offensive and devensive rebounds equal his total rebounds
        # the NBA started tracking rebounds separately in 1973-74 season
        # player's that played before that need to be assessed on the basis of overall REBS, not OREBS + DREBS
    
    top_scorers.append(player.copy())
    time.sleep(2)





top_scorers_ha = copy.deepcopy(top_scorers)
# copying the top_scorers dict to later adjust the stats by height
for player in top_scorers_ha:
    for k, v in player.items():
        if k in ['PTS/MIN', 'REB/MIN', 'DREB/MIN', 'OREB/MIN', 'AST/MIN', 'STL/MIN',
        'BLK/MIN','FG_PCT', 'FGM/MIN', 'FG3_PCT', 'FG3M/MIN', 'FT_PCT','FTM/MIN']:
            player[k] = v / player['HEIGHT']
            # adjusting the 'positive' stats by height
        elif k in ['TOV/MIN', 'PF/MIN']:
            player[k] = v * player['HEIGHT']
            # adjusting the 'negative' stats by height




engine = create_engine('postgresql://postgres:' + haslo_postgres + '@localhost:5432/ultimate_rankings')
dbConnection = engine.connect()
# establishing a connection with the database

stats_weights_final_1 = pd.read_sql("select * from \"stats_weights_final\"", dbConnection)
stats_weights_final_1 = stats_weights_final_1.to_dict(orient='list')
# fetching the stats weights from the database and turning them into a dict
print(stats_weights_final_1)
stats_weights_final = {}
for k, v in stats_weights_final_1.items():
    if k in ['FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'OREB', 'DREB', 'REB', 'AST', 'PF', 'STL',
    'TOV', 'BLK', 'UPTS']:
        stats_weights_final[k + '/MIN'] = v[0]
    else:
        stats_weights_final[k] = v[0]
    # turning the key names so the're the same as the keys in player dicts
print(stats_weights_final)



ultimate_players = copy.deepcopy(top_scorers)
# copying the top_scorers dict to later add True Shooting % (both explained in stats.py)
# and Ultimate Points(both explained in stats.py) and weigh the stats
for player in ultimate_players:
    if player['FGA/MIN'] != 0 and player['FTA/MIN'] != 0:
        player['TS%'] = player['PTS/MIN'] / (2 * (player['FGA/MIN'] + 0.44 * player['FTA/MIN']))
        player['UPTS/MIN'] = player['PTS/MIN'] * player['TS%']
    else:
        player['TS%'] = 0
        player['UPTS/MIN'] = 0
        # adding TS% and UPTS to the player dict
    player['OVRL'] = 0
    # adding overall stat to the player dict
    for k, v in player.items():
        if player['REBS_OK']:
            if k in ['UPTS/MIN', 'DREB/MIN', 'OREB/MIN', 'AST/MIN', 'STL/MIN','BLK/MIN']:
                player['OVRL'] += 100 * v * stats_weights_final[k]
                # increasing the overall with each positive stat
            elif k in ['TOV/MIN', 'PF/MIN']:
                player['OVRL'] -= 100 * v * stats_weights_final[k]
                # decreasing the overall with each negative stat
        if not player['REBS_OK']:
            if k in ['UPTS/MIN', 'REB/MIN', 'AST/MIN', 'STL/MIN', 'BLK/MIN']:
                player['OVRL'] += 100 * v * stats_weights_final[k]
                # increasing the overall with each positive stat
            elif k in ['TOV/MIN', 'PF/MIN']:
                player['OVRL'] -= 100 * v * stats_weights_final[k]
                # decreasing the overall with each negative stat
        # no stats are repeated while counting the overall
        # i.e. if DREBs and OREBs are counted, REBs in general aren't, and vice versa
        # and UPTS covers all socring stats
        # OVRL is multiplied by 100 to make it easier to read


ultimate_players_ha = copy.deepcopy(ultimate_players)
# copying the ultimate_players dict to later adjust the stats by height
for player in ultimate_players_ha:
    player['OVRL'] /= player['HEIGHT']
    # adjusting the OVRL by height- can't do it with all stats because it would return
    # inconsistent results, namely
    # PTS/HEIGHT * TS%/HEIGHT != UPTS/HEIGHT, it'd equal UPTS/HEIGHT*HEIGHT
        



ultimate_players_oa = copy.deepcopy(top_scorers)
# creating an only available stats dict (many important stats weren't tracked early on)
# i.e blocks and steals weren't tracked untill 1973, and at that stage there had alrady been many great players
for player in ultimate_players_oa:
    if player['FGA/MIN'] != 0 and player['FTA/MIN'] != 0:
        player['TS%'] = player['PTS/MIN'] / (2 * (player['FGA/MIN'] + 0.44 * player['FTA/MIN']))
        player['UPTS/MIN'] = player['PTS/MIN'] * player['TS%']
    else:
        player['TS%'] = 0
        player['UPTS/MIN'] = 0
        # adding TS% and UPTS to each player's stats
    player['OVRL'] = 0
    # adding overall stat to the player dict
    for k, v in player.items():
        if k in ['UPTS/MIN', 'REB/MIN', 'AST/MIN',]:
            player['OVRL'] += 100 * v * stats_weights_final[k]
            # increasing the overall with each positive stat
        elif k in ['PF/MIN']:
            player['OVRL'] -= 100 * v * stats_weights_final[k]
            # decreasing the overall with each negative stat


ultimate_players_oa_ha = copy.deepcopy(ultimate_players_oa)
# copying the ultimate_players_oa dict to later adjust the stats by height      
for player in ultimate_players_oa_ha:
    player['OVRL'] /= player['HEIGHT']
    # adjusting the OVRL by height- can't do it with all stats because it would return
    # inconsistent results, namely
    # PTS/HEIGHT * TS%/HEIGHT != UPTS/HEIGHT, it'd equal UPTS/HEIGHT*HEIGHT



print(top_scorers[:5])
print(top_scorers_ha[:5])
print('-' * 50)
print('-' * 50)
print(ultimate_players[:5])
print(ultimate_players_ha[:5])
print('-' * 50)
print('-' * 50)
print(ultimate_players_oa[:5])
print(ultimate_players_oa_ha[:5])


top_scorers_df = pd.DataFrame(top_scorers)
# turning the dictionary into a dataframe
top_scorers_df = top_scorers_df.sort_values(by='PTS/MIN', ascending=False)
# sorting the dataframe by pts/min
top_scorers_df = top_scorers_df.round(2)
# rounding the values
top_scorers_df = top_scorers_df[['FULLNAME', 'HEIGHT', 'MIN/GAME', 'PTS/MIN', 'GP', 'GS',
'REB/MIN','DREB/MIN', 'OREB/MIN', 'AST/MIN', 'STL/MIN', 'BLK/MIN', 'TOV/MIN', 
'PF/MIN', 'FG_PCT','FGM/MIN', 'FGA/MIN', 'FG3_PCT', 'FG3M/MIN', 'FG3A/MIN', 'FT_PCT',
'FTM/MIN', 'FTA/MIN', 'PLAYER_ID']]
# setting the order of columns


top_scorers_ha_df = pd.DataFrame(top_scorers_ha)
# turning the dictionary into a dataframe
top_scorers_ha_df = top_scorers_ha_df.sort_values(by='PTS/MIN', ascending=False)
# sorting the dataframe by pts/min
top_scorers_ha_df = top_scorers_ha_df.round(2)
# rounding the values
top_scorers_ha_df = top_scorers_ha_df[['FULLNAME', 'HEIGHT', 'MIN/GAME', 'PTS/MIN', 'GP', 'GS',
'REB/MIN','DREB/MIN', 'OREB/MIN', 'AST/MIN', 'STL/MIN', 'BLK/MIN', 'TOV/MIN', 
'PF/MIN', 'FG_PCT','FGM/MIN', 'FGA/MIN', 'FG3_PCT', 'FG3M/MIN', 'FG3A/MIN', 'FT_PCT',
'FTM/MIN', 'FTA/MIN', 'PLAYER_ID']]
# setting the order of columns


ultimate_players_df = pd.DataFrame(ultimate_players)
# turning the dictionary into a dataframe
ultimate_players_df = ultimate_players_df.sort_values(by='OVRL', ascending=False)
# sorting the dataframe by ovrl
ultimate_players_df = ultimate_players_df.round(2)
# rounding the values
ultimate_players_df = ultimate_players_df[['FULLNAME', 'HEIGHT', 'OVRL', 'MIN/GAME', 'PTS/MIN', 'GP', 'GS',
'TS%', 'UPTS/MIN' ,'REB/MIN','DREB/MIN', 'OREB/MIN', 'AST/MIN', 'STL/MIN', 'BLK/MIN', 'TOV/MIN', 
'PF/MIN', 'FG_PCT','FGM/MIN', 'FGA/MIN', 'FG3_PCT', 'FG3M/MIN', 'FG3A/MIN', 'FT_PCT',
'FTM/MIN', 'FTA/MIN', 'PLAYER_ID']]
# setting the order of columns


ultimate_players_ha_df = pd.DataFrame(ultimate_players_ha)
# turning the dictionary into a dataframe
ultimate_players_ha_df = ultimate_players_ha_df.sort_values(by='OVRL', ascending=False)
# sorting the dataframe by ovrl
ultimate_players_ha_df = ultimate_players_ha_df.round(2)
# rounding the values
ultimate_players_ha_df = ultimate_players_ha_df[['FULLNAME', 'HEIGHT', 'OVRL', 'MIN/GAME', 'PTS/MIN', 'GP', 'GS',
'TS%', 'UPTS/MIN' ,'REB/MIN','DREB/MIN', 'OREB/MIN', 'AST/MIN', 'STL/MIN', 'BLK/MIN', 'TOV/MIN', 
'PF/MIN', 'FG_PCT','FGM/MIN', 'FGA/MIN', 'FG3_PCT', 'FG3M/MIN', 'FG3A/MIN', 'FT_PCT',
'FTM/MIN', 'FTA/MIN', 'PLAYER_ID']]
# setting the order of columns

ultimate_players_oa_df = pd.DataFrame(ultimate_players_oa)
# turning the dictionary into a dataframe
ultimate_players_oa_df = ultimate_players_oa_df.sort_values(by='OVRL', ascending=False)
# sorting the dataframe by ovrl
ultimate_players_oa_df = ultimate_players_oa_df.round(2)
# rounding the values
ultimate_players_oa_df = ultimate_players_oa_df[['FULLNAME', 'HEIGHT', 'OVRL', 'MIN/GAME', 'PTS/MIN', 'GP', 'GS',
'TS%', 'UPTS/MIN' ,'REB/MIN','DREB/MIN', 'OREB/MIN', 'AST/MIN', 'STL/MIN', 'BLK/MIN', 'TOV/MIN', 
'PF/MIN', 'FG_PCT','FGM/MIN', 'FGA/MIN', 'FG3_PCT', 'FG3M/MIN', 'FG3A/MIN', 'FT_PCT',
'FTM/MIN', 'FTA/MIN', 'PLAYER_ID']]
# setting the order of columns


ultimate_players_oa_ha_df = pd.DataFrame(ultimate_players_oa_ha)
# turning the dictionary into a dataframe
ultimate_players_oa_ha_df = ultimate_players_oa_ha_df.sort_values(by='OVRL', ascending=False)
# sorting the dataframe by ovrl
ultimate_players_oa_ha_df = ultimate_players_oa_ha_df.round(2)
# rounding the values
ultimate_players_oa_ha_df = ultimate_players_oa_ha_df[['FULLNAME', 'HEIGHT', 'OVRL', 'MIN/GAME', 'PTS/MIN', 'GP', 'GS',
'TS%', 'UPTS/MIN' ,'REB/MIN','DREB/MIN', 'OREB/MIN', 'AST/MIN', 'STL/MIN', 'BLK/MIN', 'TOV/MIN', 
'PF/MIN', 'FG_PCT','FGM/MIN', 'FGA/MIN', 'FG3_PCT', 'FG3M/MIN', 'FG3A/MIN', 'FT_PCT',
'FTM/MIN', 'FTA/MIN', 'PLAYER_ID']]
# setting the order of columns

top_scorers_df.to_sql('top_scorers', engine, index=False, index_label='id')
top_scorers_ha_df.to_sql('top_scorers_ha', engine, index=False, index_label='id')
ultimate_players_df.to_sql('ultimate_players', engine, index=False, index_label='id')
ultimate_players_ha_df.to_sql('ultimate_players_ha', engine, index=False, index_label='id')
ultimate_players_oa_df.to_sql('ultimate_players_oa', engine, index=False, index_label='id')
ultimate_players_oa_ha_df.to_sql('ultimate_players_oa_ha', engine, index=False, index_label='id')
# saving the tables in a database
dbConnection.close()
engine.dispose()
# closing the connection and engine
  
print(top_scorers_df[:5])
print(top_scorers_ha_df[:5])
print('-' * 50)
print('-' * 50)
print(ultimate_players_df[:5])
print(ultimate_players_ha_df[:5])
print('-' * 50)
print('-' * 50)
print(ultimate_players_oa_df[:5])
print(ultimate_players_oa_ha_df[:5])
