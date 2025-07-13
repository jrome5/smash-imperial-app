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
    advantage = 0
    bigger_player = attacking_player_count if attacking_player_count > defending_player_count else defending_player_count
    smaller_player = defending_player_count if bigger_player == attacking_player_count else attacking_player_count
    diff = bigger_player - smaller_player
    if diff <= 4:
        advantage = 0
    if diff >= 4 :
        advantage = 10
    scale = floor(bigger_player / smaller_player)
    if 4 <= scale < 8:
        advantage = 20
    if scale >= 8:
        advantage = 30

    if attacking_player_count > defending_player_count:
        return advantage
    else:
        return -advantage

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

