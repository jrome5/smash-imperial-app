from math import floor


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

