from requests import get
import json
from datetime import datetime

def print_menu():
    print("\n1. Total kills over last x matches")
    print("2. List of ACSs over last x matches")
    print("3. Check stats from last game with a given player")
    print("4. Check rr changes for last 3 matches")
    pass


def get_data_for_x_matches(player_name, player_tag, amount_of_matches):
    url = f"https://api.henrikdev.xyz/valorant/v1/lifetime/matches/na/{player_name}/{player_tag}?mode=competitive&size={amount_of_matches}"
    result = get(url)
    data = json.loads(result.content)["data"]
    return data


def total_kills_over_x_matches(player_name, player_tag, amount_of_matches):
    data = get_data_for_x_matches(player_name, player_tag, amount_of_matches)
    total_kills = sum(match['stats']['kills'] for match in data)
    total_rounds = sum(match['teams']['red'] for match in data) + sum(match['teams']['blue'] for match in data)
    return [total_kills, total_rounds]
    
    
def list_of_acs(player_name, player_tag, amount_of_matches):
    data = get_data_for_x_matches(player_name, player_tag, amount_of_matches)
    acs_list = []
    for match in data:
        num_rounds = match['teams']['red'] + match['teams']['blue']
        acs_list.append(match['stats']['score']/num_rounds)
        pass
    return acs_list


def find_first_common_element_with_index(list1, list2):
    for index1, element1 in enumerate(list1):
        for index2, element2 in enumerate(list2):
            if element1 == element2:
                return element1, index1, index2
    return None, None, None


def get_player_stats_for_match(data):
    kills = data['stats']['kills']
    deaths = data['stats']['deaths']
    assists = data['stats']['assists']
    dd_delta = round((data['stats']['damage']['made'] - data['stats']['damage']['received'])/(data['teams']['red'] + data['teams']['blue']),1)
    acs = round(data['stats']['score']/(data['teams']['red'] + data['teams']['blue']),1)
    character = data['stats']['character']['name']
    return kills, deaths, assists, dd_delta, acs, character


def print_table(player1_stats, player2_stats):
    headers = ['Statistics', player1_stats['name'], player2_stats['name']]
    data = [
        ['Character', player1_stats['character'], player2_stats['character']],
        ['Kills', player1_stats['kills'], player2_stats['kills']],
        ['Deaths', player1_stats['deaths'], player2_stats['deaths']],
        ['Assists', player1_stats['assists'], player2_stats['assists']],
        ['DDΔ', player1_stats['dd_delta'], player2_stats['dd_delta']],
        ['ACS', player1_stats['acs'], player2_stats['acs']]
    ]

    # Find the maximum width for each column
    col_widths = [max(len(str(item)) for item in col) for col in zip(headers, *data)]

    # Print the top border
    top_border = "+" + "+".join("-" * (width + 2) for width in col_widths) + "+"
    print(top_border)

    # Print the header
    header_row = "| " + " | ".join(f"{header:<{col_widths[i]}}" for i, header in enumerate(headers)) + " |"
    print(header_row)
    print(top_border)

    # Print the data rows
    for row in data:
        data_row = "| " + " | ".join(f"{item:<{col_widths[i]}}" for i, item in enumerate(row)) + " |"
        print(data_row)

    # Print the bottom border
    print(top_border)


def compare_performace(first_player_name, first_player_tag, second_player_name, second_player_tag):
    #go through each game from first player and check if second player is in that game
    # if so, that is target game
    # find data for that game
    first_player_data = get_data_for_x_matches(first_player_name, first_player_tag, 100)
    second_player_data = get_data_for_x_matches(second_player_name, second_player_tag, 100)
    first_player_ids = []
    second_player_ids = []
    for match in first_player_data:
        first_player_ids.append(match["meta"]["id"])
        pass
    for match in second_player_data:
        second_player_ids.append(match["meta"]["id"])
        pass
    common_id, index1, index2 = find_first_common_element_with_index(first_player_ids, second_player_ids)
    if index1 is None or index2 is None:
        print("These players do not have a game together accessible by the API")
        return None
    common_game_data_1 = first_player_data[index1]
    common_game_data_2 = second_player_data[index2]
    player1_kills, player1_deaths, player1_assists, player1_dd_delta, player1_acs, player1_character = get_player_stats_for_match(common_game_data_1)
    player2_kills, player2_deaths, player2_assists, player2_dd_delta, player2_acs, player2_character = get_player_stats_for_match(common_game_data_2)
    player1_stats = {
        'name': first_player_name,
        'kills': player1_kills,
        'deaths': player1_deaths,
        'assists': player1_assists,
        'dd_delta': player1_dd_delta,
        'acs': player1_acs,
        'character': player1_character
    }
    player2_stats = {
        'name': second_player_name, 
        'kills': player2_kills,
        'deaths': player2_deaths,
        'assists': player2_assists,
        'dd_delta': player2_dd_delta,
        'acs': player2_acs,
        'character': player2_character
    }
    # Date - Win/Loss
    if common_game_data_1['stats']['team'] == 'Red':
        if common_game_data_1['teams']['red'] > common_game_data_1['teams']['blue']:
            result = "Win " + str(common_game_data_1['teams']['red'])+"-"+str(common_game_data_1['teams']['blue'])
            pass
        elif common_game_data_1['teams']['red'] < common_game_data_1['teams']['blue']:
            result = "Lost " + str(common_game_data_1['teams']['red'])+"-"+str(common_game_data_1['teams']['blue'])
            pass
        else:
            result = "Tie "+ str(common_game_data_1['teams']['red'])+"-"+str(common_game_data_1['teams']['blue'])
        pass
    elif common_game_data_1['stats']['team'] == 'Blue':
        if common_game_data_1['teams']['blue'] > common_game_data_1['teams']['red']:
            result = "Win " + str(common_game_data_1['teams']['blue'])+"-"+str(common_game_data_1['teams']['red'])
            pass
        elif common_game_data_1['teams']['blue'] < common_game_data_1['teams']['red']:
            result = "Lost " + str(common_game_data_1['teams']['blue'])+"-"+str(common_game_data_1['teams']['red'])
            pass
        else:
            result = "Tie "+ str(common_game_data_1['teams']['blue'])+"-"+str(common_game_data_1['teams']['red'])
        pass 
    date_obj = datetime.strptime(common_game_data_1['meta']['started_at'][:10], '%Y-%m-%d')
    formatted_date = date_obj.strftime('%B %d, %Y')        
    print("\n\n      ",formatted_date , "-", result)
    print_table(player1_stats, player2_stats)
    pass


def rr_change_last_3_matches(player_name: str, player_tag: str):
    url = f"https://api.henrikdev.xyz/valorant/v1/lifetime/mmr-history/na/{player_name}/{player_tag}?size=3"
    result = get(url)
    data = json.loads(result.content)["data"]
    maps = []
    rr_changes = []
    for match in data:
        maps.append(match["map"]["name"])
        rr_changes.append(match["last_mmr_change"])
        pass
    i = 0
    print(f"\n\n{player_name}'s rank is currently {data[0]['tier']['name']} {data[0]['ranking_in_tier']}/100")
    for index, map in enumerate(maps, start=1):
            print(f"Match {index} on {map}: {rr_changes[i]}")
            i = i+1
            pass
    pass


def user_selection(choice):
    if(choice=="1"):
        player_name = input("Enter player name: ")
        player_tag = input("Enter player tag: ")
        amount_of_matches = input("Enter number of matches: ")
        info = total_kills_over_x_matches(player_name, player_tag, amount_of_matches)
        print(f"\nYou had {info[0]} kills in {info[1]} rounds in the last {amount_of_matches} matches.")
        pass
    elif(choice=="2"):
        player_name = input("\nEnter player name: ")
        player_tag = input("Enter player tag: ")
        amount_of_matches = input("Enter number of matches: ")
        print()
        acs_list = list_of_acs(player_name, player_tag, amount_of_matches)
        average_acs = sum(acs_list)/len(acs_list)
        for index, score in enumerate(acs_list, start=1):
            print(f"Match {index}: {score:.2f}")
            pass
        print(f"Your average ACS over the past {len(acs_list)} games is {average_acs:.2f}")
        pass
    elif choice == "3":
        first_player_name = input("\nEnter first player name: ")
        first_player_tag = input("Enter first player tag: ")
        second_player_name = input("Enter second player name: ")
        second_player_tag = input("Enter second player tag: ")
        compare_performace(first_player_name, first_player_tag, second_player_name, second_player_tag)
        pass
    elif choice == "4":
        player_name = input("Enter player name: ")
        player_tag = input("Enter player tag: ")
        rr_change_last_3_matches(player_name, player_tag)
        pass
    
    
def run():
    choice = ""
    while choice != "stop":
        print_menu()
        choice = input("Enter your selection: ")
        user_selection(choice)


run()
