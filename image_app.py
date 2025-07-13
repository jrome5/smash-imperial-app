import streamlit as st
from PIL import Image
from io import BytesIO
from collections import Counter
from streamlit_image_coordinates import streamlit_image_coordinates


from character_roster import roster as starting_roster
from visualisations import plot_map
from main import (
    find_surrounding_players,
    calculate_advantage,
    update_map,
)

# ---------------- Initialization ---------------- #

def initialize_game():
    st.session_state.map = [row.copy() for row in starting_roster]
    st.session_state.round = 0
    st.session_state.game_over = False
    st.session_state.images = [Image.fromarray(plot_map(st.session_state.map, return_image=True))]

    st.session_state.last_attacker = None
    st.session_state.last_defender = None
    st.session_state.last_advantage = None
    st.session_state.last_victor = None

    st.session_state.phase = "preparation"
    st.session_state.pending_attacker = None
    st.session_state.pending_defender = None
    st.session_state.pending_advantage = None


# ---------------- Utility ---------------- #

def check_winner(current_map):
    flattened = [p for row in current_map for p in row if p != "blank"]
    remaining = Counter(flattened)
    if len(remaining) == 1:
        return True, list(remaining.keys())[0]
    return False, None

def get_player_scores():
    flat_map = [p for row in st.session_state.map for p in row if p != "blank"]
    return Counter(flat_map)

def render_scoreboard():
    scores = get_player_scores()
    if not scores:
        return

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    leader = sorted_scores[0][0]

    with st.container():
        st.markdown("### 🧮 Player Scores")
        for player, count in sorted_scores:
            is_leader = player == leader
            st.markdown(
                f"- {'🏆 ' if is_leader else ''}**{player}**: {count} tile{'s' if count != 1 else ''}"
            )


def convert_click_to_cell(click, img, grid_rows, grid_cols):
    if not click:
        return None, None
    img_width, img_height = img.size
    cell_width = img_width / grid_cols
    cell_height = img_height / grid_rows
    col = int(click["x"] // cell_width)
    row = int(click["y"] // cell_height)
    return row, col


# ---------------- Game Flow ---------------- #

def handle_map_click(click):
    if st.session_state.get("skip_next_click"):
        st.session_state.skip_next_click = False
        return

    map = st.session_state.map
    grid_rows = len(map)
    grid_cols = len(map[0])
    image = st.session_state.images[-1]

    row, col = convert_click_to_cell(click, image, grid_rows, grid_cols)

    if row is not None and 0 <= row < grid_rows and 0 <= col < grid_cols:
        clicked_cell = map[row][col]

        if clicked_cell == "blank":
            return

        if st.session_state.pending_attacker is None:
            # 🔥 Highlight attacker and defender on map
            st.session_state.pending_attacker = clicked_cell
            attacker = st.session_state.pending_attacker
            highlighted_img = plot_map(map, return_image=True, attacker=attacker)
            st.session_state.images[-1] = Image.fromarray(highlighted_img)
            st.rerun()

        elif st.session_state.pending_defender is None and clicked_cell != st.session_state.pending_attacker:
            st.session_state.pending_defender = clicked_cell

            attacker = st.session_state.pending_attacker
            defender = st.session_state.pending_defender

            attacker_count = sum(r.count(attacker) for r in map)
            defender_count = sum(r.count(defender) for r in map)
            st.session_state.pending_advantage = calculate_advantage(attacker_count, defender_count)

            # 🔥 Highlight attacker and defender on map
            highlighted_img = plot_map(map, return_image=True, attacker=attacker, defender=defender)
            st.session_state.images[-1] = Image.fromarray(highlighted_img)

            st.session_state.phase = "resolution"
            st.rerun()


def resolve_round(victor_choice):
    map = st.session_state.map
    attacker = st.session_state.pending_attacker
    defender = st.session_state.pending_defender
    advantage = st.session_state.pending_advantage

    attacker_count = sum(row.count(attacker) for row in map)
    defender_count = sum(row.count(defender) for row in map)

    winner = attacker if victor_choice == "A" else defender
    loser = defender if victor_choice == "A" else attacker
    losing_count = defender_count if victor_choice == "A" else attacker_count

    updated_map = update_map(map, winner, loser, losing_count)
    st.session_state.map = updated_map
    st.session_state.round += 1

    st.session_state.last_attacker = attacker
    st.session_state.last_defender = defender
    st.session_state.last_advantage = advantage
    st.session_state.last_victor = winner

    st.session_state.images.append(Image.fromarray(
        plot_map(updated_map, return_image=True)))

    over, winning_player = check_winner(updated_map)
    if over:
        st.session_state.game_over = True
        st.success(f"Game over! {winning_player} controls the entire map.")

    # Reset for next round
    st.session_state.phase = "preparation"
    st.session_state.pending_attacker = None
    st.session_state.pending_defender = None
    st.session_state.pending_advantage = None


# ---------------- UI Rendering ---------------- #

def render_map_and_click_handler():
    image = st.session_state.images[-1]
    st.write("### Click a unit to select Attacker and Defender")
    click = streamlit_image_coordinates(image, key=f"map_click_{st.session_state.round}")
    handle_map_click(click)


def render_last_round_summary():
    if st.session_state.last_attacker and st.session_state.last_defender:
        st.write(f"**{st.session_state.last_attacker}** attacked **{st.session_state.last_defender}**")
        st.write(f"{st.session_state.last_defender} had a disadvantage of **{st.session_state.last_advantage}%**")
        st.write(f"🏆 Winner: **{st.session_state.last_victor}**")


def render_game_phase():
    if st.session_state.phase == "preparation":
        if st.session_state.pending_attacker and not st.session_state.pending_defender:
            st.info(f"Selected attacker: **{st.session_state.pending_attacker}**. Now click to select a defender.")
        elif not st.session_state.pending_attacker:
            st.info("Click a unit to select an attacker.")

    elif st.session_state.phase == "resolution":
        attacker = st.session_state.pending_attacker
        defender = st.session_state.pending_defender
        advantage = st.session_state.pending_advantage

        st.write(f"**{attacker}** is attacking **{defender}**")
        st.write(f"{defender} has a disadvantage of **{advantage}%**")

        st.radio(
            "Who won the round?",
            [f"A ({attacker})", f"B ({defender})"],
            key="victor_choice"
        )

        if st.button("Resolve Round"):
            resolve_round(st.session_state.victor_choice[0])
            st.rerun()

    # Clear Selection (always available during selection)
    if st.session_state.pending_attacker or st.session_state.pending_defender:
        if st.button("Clear Selection"):
            clear_selection()
            st.rerun()



def render_restart_button():
    if st.button("Restart Game"):
        initialize_game()
        st.rerun()


def clear_selection():
    st.session_state.pending_attacker = None
    st.session_state.pending_defender = None
    st.session_state.pending_advantage = None
    st.session_state.phase = "preparation"
    st.session_state.skip_next_click = True  # NEW


# ---------------- Main ---------------- #

def main():
    st.set_page_config(page_title="Battle Map Simulator", layout="wide")

    if "map" not in st.session_state:
        initialize_game()

    st.title("Battle Map Simulator")
    st.write(f"### Round {st.session_state.round}")

    # Two-column layout: main game + scores
    col1, col2 = st.columns([3, 1], gap="large")

    with col1:
        render_map_and_click_handler()
        render_last_round_summary()

        if not st.session_state.game_over:
            render_game_phase()

        render_restart_button()

    with col2:
        render_scoreboard()



if __name__ == "__main__":
    main()
