import argparse
import os
import requests
import json
import datetime


def make_arguments():
    parser = argparse.ArgumentParser(description="Bulk downloads up to 200 of "
                                     "the specified user's pgn files from "
                                     "Lichess.org")
    parser.add_argument("username", help="Lichess.org username")
    parser.add_argument("num", type=int, nargs="?", default=200, help="Number "
                        "of pgn files to fetch (most recent first). Defaults "
                        "to 200")
    args = parser.parse_args()
    return args


def create_dir():
    # make directory ~/lichess_pgns/<username>, if it doesn't already exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)


def fetch_games_data(username, number):
    games_url = ("https://en.lichess.org/api/user/" + username + "/games?nb=" +
                 str(number) + "&with_moves=1")
    games_data = requests.get(games_url).text  # fetch data as string
    # reload games_data with json parser to enable access as python dictionary
    games_data = json.loads(games_data)               
    return games_data


def convert_timestamp(timestamp):
    in_seconds = (int(timestamp))/1000.0  # convert milliseconds to seconds
    utc = datetime.datetime.utcfromtimestamp(in_seconds)
    date = utc.strftime("%d_%b_%y")
    return date


def make_filenames(games_data):
    filenames = {}
    for game in games_data["currentPageResults"]:
        date = convert_timestamp(game["createdAt"])
        # Games vs AI have a blank "userId" entry
        if "userId" in game["players"]["black"]:
            black = game["players"]["black"]["userId"]
        else:
            black = "stockfish"
        filenames[game["id"]] = (game["players"]["white"]["userId"] + "_vs_" +
                                 black + "_" + date + "_" + game["id"] + ".pgn")
    return filenames


def fetch_pgn(filename):
    pgn_url = "https://en.lichess.org/game/export/"
    pgn = requests.get(pgn_url + filename + ".pgn").text
    return pgn


def write_pgn(filenames, filename, target_dir, pgn):
    path = target_dir + filenames[filename]
    print("writing " + filenames[filename])
    with open(path, "w+") as f:
        f.write(pgn)


target_dir = "lichess_pgns/" + make_arguments().username + "/"
games_data = fetch_games_data(make_arguments().username, make_arguments().num)
filenames = make_filenames(games_data)

dir_contents = os.listdir(target_dir)
count = 0
for filename in filenames:
    if filenames[filename] not in dir_contents:
        pgn = fetch_pgn(filename)
        write_pgn(filenames, filename, target_dir, pgn)
    count = count + 1
print("\nFetched " + str(count) + " files")
    
