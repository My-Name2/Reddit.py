import streamlit as st
import random
import string

# Global variable to store all active games
if "games" not in st.session_state:
    st.session_state.games = {}

# Helper function to generate a unique host code
def generate_host_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Game board and properties
board = [
    "GO",
    "Mediterranean Avenue", "Community Chest", "Baltic Avenue", "Income Tax",
    "Reading Railroad", "Oriental Avenue", "Chance", "Vermont Avenue", "Connecticut Avenue",
    "Jail", "St. Charles Place", "Electric Company", "States Avenue", "Virginia Avenue",
    "St. James Place", "Tennessee Avenue", "New York Avenue", "Free Parking",
    "Kentucky Avenue", "Chance", "Indiana Avenue", "Illinois Avenue", "B&O Railroad",
    "Atlantic Avenue", "Ventnor Avenue", "Water Works", "Marvin Gardens", "Go to Jail",
    "Pacific Avenue", "North Carolina Avenue", "Community Chest", "Pennsylvania Avenue",
    "Short Line Railroad", "Chance", "Park Place", "Luxury Tax", "Boardwalk"
]

property_prices = {
    "Mediterranean Avenue": 60,
    "Baltic Avenue": 60,
    "Oriental Avenue": 100,
    "Vermont Avenue": 100,
    "Connecticut Avenue": 120,
    "St. Charles Place": 140,
    "States Avenue": 140,
    "Virginia Avenue": 160,
    "St. James Place": 180,
    "Tennessee Avenue": 180,
    "New York Avenue": 200,
    "Kentucky Avenue": 220,
    "Indiana Avenue": 220,
    "Illinois Avenue": 240,
    "Atlantic Avenue": 260,
    "Ventnor Avenue": 260,
    "Marvin Gardens": 280,
    "Pacific Avenue": 300,
    "North Carolina Avenue": 300,
    "Pennsylvania Avenue": 320,
    "Park Place": 350,
    "Boardwalk": 400,
    "Reading Railroad": 200,
    "B&O Railroad": 200,
    "Short Line Railroad": 200,
    "Water Works": 150,
    "Electric Company": 150,
}

# Rent prices for properties (simplified: rent = 10% of property price)
property_rent = {key: int(value * 0.1) for key, value in property_prices.items()}

# Chance and Community Chest cards
chance_cards = [
    "Advance to GO! Collect $200.",
    "Go to Jail! Do not pass GO, do not collect $200.",
    "Bank pays you a dividend of $50.",
    "You are assessed for street repairs: Pay $100.",
]
community_chest_cards = [
    "Receive $100 for your birthday!",
    "Doctor's fee: Pay $50.",
    "Go directly to Jail! Do not pass GO, do not collect $200.",
    "Collect $20 from every player.",
]

# Create or join a game
st.title("Streamlit Monopoly")
game_code = None

if "game_code" not in st.session_state:
    st.session_state.game_code = None

# Host a new game
if st.button("Host a Game"):
    game_code = generate_host_code()
    st.session_state.game_code = game_code
    st.session_state.games[game_code] = {
        "host": True,
        "players": [],
        "game_started": False,
        "player_positions": {},
        "player_balances": {},
        "player_properties": {},
        "current_turn": 0,
        "bankrupted_players": [],
    }
    st.success(f"Game hosted! Share this code with others to join: {game_code}")

# Join an existing game
st.write("---")
st.write("### Join a Game")
join_code = st.text_input("Enter Host Code")
if st.button("Join Game"):
    if join_code in st.session_state.games:
        st.session_state.game_code = join_code
        if "username" not in st.session_state:
            st.session_state.username = st.text_input("Enter your name:")
            if st.button("Set Name"):
                st.session_state.games[join_code]["players"].append(st.session_state.username)
                st.session_state.games[join_code]["player_positions"][st.session_state.username] = 0
                st.session_state.games[join_code]["player_balances"][st.session_state.username] = 1500
                st.session_state.games[join_code]["player_properties"][st.session_state.username] = []
                st.success(f"Joined game {join_code} as {st.session_state.username}!")
    else:
        st.error("Invalid host code. Please try again.")

# Display lobby if a game is joined
if st.session_state.game_code:
    game = st.session_state.games[st.session_state.game_code]
    st.write(f"### Lobby for Game {st.session_state.game_code}")
    st.write("Players:")
    for player in game["players"]:
        st.write(f"- {player}")

    # Start the game (host only)
    if not game["game_started"] and len(game["players"]) >= 2:
        if st.button("Start Game (Host Only)") and game["host"]:
            game["game_started"] = True
            st.success("Game started!")
            st.experimental_rerun()

# Game logic after start
if st.session_state.game_code and st.session_state.games[st.session_state.game_code]["game_started"]:
    game = st.session_state.games[st.session_state.game_code]
    current_player = game["players"][game["current_turn"]]

    st.write(f"### Current Turn: {current_player}")
    st.write(f"Position: {board[game['player_positions'][current_player]]}")
    st.write(f"Balance: ${game['player_balances'][current_player]}")

    if st.button("Roll Dice"):
        dice_roll = random.randint(1, 6) + random.randint(1, 6)
        st.write(f"{current_player} rolled a {dice_roll}!")

        # Update position
        new_position = (game["player_positions"][current_player] + dice_roll) % len(board)
        game["player_positions"][current_player] = new_position

        current_space = board[new_position]
        st.write(f"{current_player} landed on {current_space}!")

        # Handle Chance and Community Chest
        if current_space == "Chance":
            card = random.choice(chance_cards)
            st.write(f"Chance Card: {card}")
            if "Advance to GO" in card:
                game["player_positions"][current_player] = 0
                game["player_balances"][current_player] += 200
            elif "Go to Jail" in card:
                game["player_positions"][current_player] = board.index("Jail")
            elif "dividend" in card:
                game["player_balances"][current_player] += 50
            elif "Pay $100" in card:
                game["player_balances"][current_player] -= 100
        elif current_space == "Community Chest":
            card = random.choice(community_chest_cards)
            st.write(f"Community Chest Card: {card}")
            if "birthday" in card:
                game["player_balances"][current_player] += 100
            elif "Doctor's fee" in card:
                game["player_balances"][current_player] -= 50
            elif "Go directly to Jail" in card:
                game["player_positions"][current_player] = board.index("Jail")
            elif "Collect $20" in card:
                for player in game["players"]:
                    if player != current_player and player not in game["bankrupted_players"]:
                        game["player_balances"][player] -= 20
                        game["player_balances"][current_player] += 20

        # Handle property purchase and rent
        if current_space in property_prices:
            if current_space not in [prop for player_props in game["player_properties"].values() for prop in player_props]:
                price = property_prices[current_space]
                st.write(f"{current_space} is available for purchase for ${price}.")
                if game["player_balances"][current_player] >= price:
                    if st.button("Buy Property"):
                        game["player_balances"][current_player] -= price
                        game["player_properties"][current_player].append(current_space)
                        st.success(f"{current_player} purchased {current_space}!")
                else:
                    st.error("Not enough money to buy this property!")
            else:
                # Pay rent
                for owner, properties in game["player_properties"].items():
                    if current_space in properties and owner != current_player:
                        rent = property_rent[current_space]
                        st.write(f"{current_player} pays ${rent} in rent to {owner}.")
                        game["player_balances"][current_player] -= rent
                        game["player_balances"][owner] += rent
                        if game["player_balances"][current_player] < 0:
                            st.error(f"{current_player} is bankrupt!")
                            game["bankrupted_players"].append(current_player)
                        break

        # End turn
        if st.button("End Turn"):
            game["current_turn"] = (game["current_turn"] + 1) % len(game["players"])
            st.experimental_rerun()
