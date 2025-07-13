import cv2
import numpy as np
import random
import matplotlib.pyplot as plt
from visualisations import plot_map, plot_map_animation, plot_map_animation_to_mp4
from character_roster import roster as starting_roster
from math import floor

def find_surrounding_players(players, target_player):
    # Find the position of the target player
    positions = [(i, j) for i, row in enumerate(players) for j, player in enumerate(row) if player == target_player]

    surrounding_players = set()
    for x, y in positions:
        # Check all surrounding cells
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                # Skip the target player itself
                if (nx, ny) == (x, y):
                    continue
                # Check if the position is within the bounds of the array
                if 0 <= nx < len(players) and 0 <= ny < len(players[0]):
                    # Add the player to the set
                    if players[nx][ny] != "blank" and players[nx][ny] != target_player:
                        surrounding_players.add(players[nx][ny])

    return list(surrounding_players)

'''
If you have more spaces than your opponent, you can get a small percentage
advantage
4+ = 10%
4x = 20%
8x = 30%
Rounds down but not up
'''
def calculate_advantage(attacking_player_count, defending_player_count):
    if attacking_player_count - defending_player_count <= 4:
        return 0
    if attacking_player_count - defending_player_count >= 4:
        return 10
    elif floor(attacking_player_count / defending_player_count) == 4:
        return 20
    elif floor(attacking_player_count / defending_player_count) == 8:
        return 30
    else:
        return 0

import numpy as np

def update_map(map, winner, loser, losing_player_count=1):
    height = len(map)
    width = len(map[0]) if height > 0 else 0

    # Determine how many loser tiles to replace
    if losing_player_count < 16:
        players_to_lose = losing_player_count
    elif losing_player_count < 32:
        players_to_lose = losing_player_count // 2
    else:
        players_to_lose = losing_player_count // 4

    # Get coordinates of winner and loser tiles
    winner_coords = [(i, j) for i in range(height) for j in range(width) if map[i][j] == winner]
    loser_coords = [(i, j) for i in range(height) for j in range(width) if map[i][j] == loser]

    if not winner_coords or not loser_coords:
        return map  # Nothing to do

    # Compute distance from each loser to the nearest winner
    def min_distance_to_winner(loser_pos):
        li, lj = loser_pos
        return min((li - wi) ** 2 + (lj - wj) ** 2 for wi, wj in winner_coords)  # squared distance

    # Sort loser positions by proximity to winners
    loser_coords.sort(key=min_distance_to_winner)

    # Replace closest losers
    for i, j in loser_coords[:players_to_lose]:
        map[i][j] = winner

    return map


def check_winner(map):
    flattened_map = [character for row in map for character in row if character != "blank"]
    from collections import Counter

    num_values = len(Counter(flattened_map).keys())
    print(f'{num_values} players remaining')
    return num_values == 1

#steps
# 1. choose random character
# 2. choose random surrounding character
# 3. declare battle and ask who wins
# 4. update roster
def step(map, simulate=False):
    flattened_map = [character for row in map for character in row if character != "blank"]
    attacking_player = random.choice(flattened_map)
    surrounding_players = find_surrounding_players(map, attacking_player)
    flattened_surrounding_players = np.reshape(surrounding_players, -1)
    # if flattened_surrounding_players.count("blank") > 0:
        # flattened_surrounding_players.remove("blank")
    defending_player = random.choice(flattened_surrounding_players)

    attacking_player_count = flattened_map.count(attacking_player)
    defending_player_count = flattened_map.count(defending_player)
    print(f"{attacking_player} attacks {defending_player}")
    advantage = calculate_advantage(attacking_player_count, defending_player_count)
    print(f"{defending_player} player has handicap: {advantage}%")
    # declare battle
    # TODO: implement battle logic
    if simulate:
        victor = random.choice(["A", "B"])
    else:
        victor = input("Who won? A or B? ")

    winner = attacking_player if victor == "A" else defending_player
    loser = defending_player if victor == "A" else attacking_player
    print(f"{winner} wins!")

    losing_player_count = defending_player_count if victor == "A" else attacking_player_count
    return update_map(map, winner, loser, losing_player_count), check_winner(map)


def main():
    map = starting_roster
    count = 0
    while True:
        map, is_over = step(map, simulate=True)
        if is_over:
            print(f"Game over! Winner: {map[0][0]}")
            plot_map(map, save=True, map_count=count)
            plot_map_animation()
            return
        plot_map(map, save=True, map_count=count)
        count += 1

if __name__ == "__main__":
    main()