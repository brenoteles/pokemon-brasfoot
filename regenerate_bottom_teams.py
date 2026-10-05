import json
import random
import re

# (Keep your existing mon_names, abilities, moves_pool, items_pool, natures lists here)
mon_names = ['Zapdos','Chansey','Tauros','Moltres','Articuno','Sylveon','Umbreon','Garchomp','Ariados','Mew','Ferrothorn','Kartana','Primeape','Virizion','Arbok','Skarmory','Regieleki','Victini','Jynx','Persian','Mewtwo', 'Dugtrio', 'Xatu', 'Azelf', 'Mienshao', 'Snorlax', 'Braviary', 'Alomomola', 'Cinccino', 'Slowbro', 'Octillery', 'Castform', 'Aerodactyl', 'Steelix', 'Seismitoad', 'Genesect']
abilities = ['Unaware','Rough Skin','Serene Grace','Intimidate','Neutralizing Gas','Sand Stream','Pressure','Defiant','Mold Breaker','Pure Power','Trace','Justified','Good as Gold','Purifying Salt','Grassy Surge','Drizzle','Drought','Transistor','Unseen Fist','Stamina', 'Regenerator', 'Tinted Lens', 'Sap Sipper', 'Hustle', 'Sniper', 'Filter', 'Effect Spore', 'Download']
moves_pool = ['Air Slash','Body Press','Toxic','U-turn','Rock Smash','Dazzling Gleam','Power-Up Punch','Fire Punch','Rapid Spin','Boomburst','Flame Charge','Overheat','Aqua Jet','Fishious Rend','Hydro Pump','Mega Drain','Power Whip','Nuzzle','Thunder','Ice Shard','Blizzard','Mach Punch','Close Combat','Acid','Gunk Shot','Mud Shot','Earthquake','Gust','Brave Bird','Confusion','Psystrike','Megahorn','Rock Tomb','Head Smash','Astonish','Shadow Ball','Shadow Bone','Twister','Draco Meteor','Snarl','Knock Off','Bullet Punch','Bulldoze','Fairy Wind','Play Rough', 'Steel Wing', 'Aura Sphere', 'Flare Blitz', 'Rock Slide', 'Aqua Tail', 'Body Slam', 'Precipice Blades', 'Magnitude']
items_pool = ['Leftovers', 'Life Orb', 'Heavy-Duty Boots', 'Assault Vest', 'Rocky Helmet', 'Focus Sash', 'Sitrus Berry', 'Lum Berry', 'Expert Belt', 'Black Sludge', 'White Herb', 'Mental Herb', 'Power Herb', 'Red Card', 'Eject Button', 'Eject Pack', 'Weakness Policy', 'Clear Amulet', 'Covert Cloak', 'Loaded Dice']
natures = ["Hardy", "Lonely", "Brave", "Adamant", "Naughty", "Bold", "Docile", "Relaxed", "Impish", "Lax", "Timid", "Hasty", "Serious", "Jolly", "Naive", "Modest", "Mild", "Quiet", "Bashful", "Rash", "Calm", "Gentle", "Sassy", "Careful", "Quirky"]

def generate_random_evs():
    stats = ['HP', 'Atk', 'Def', 'SpA', 'SpD', 'Spe']
    evs = {stat: 0 for stat in stats}
    remaining_blocks = 508 // 4 
    while remaining_blocks > 0:
        stat = random.choice(stats)
        if evs[stat] < 252:
            evs[stat] += 4
            remaining_blocks -= 1
    return " / ".join([f"{value} {stat}" for stat, value in evs.items() if value > 0])

def generate_random_pokemon(name, abils, moves, items):
    ability = random.choice(abils)
    item = random.choice(items) 
    num_moves = min(len(moves), 4)
    selected_moves = random.sample(moves, num_moves)
    
    lines = [
        f"{name} @ {item}",
        f"Ability: {ability}",
        f"EVs: {generate_random_evs()}",
        f"{random.choice(natures)} Nature"
    ]
    for move in selected_moves:
        lines.append(f"- {move}")
    return "\n".join(lines)

def generate_team_text(player_num, names, abils, moves, items):
    team_names = random.sample(names, min(len(names), 6))
    pokemon_blocks = [generate_random_pokemon(name, abils, moves, items) for name in team_names]
    team_string = "\n\n".join(pokemon_blocks)
    return f'player_{player_num} = """\n{team_string}\n"""'

def regenerate_worst_teams(json_file="tournament_state.json", python_file="times.py", num_teams=25):
    print(f"🔍 Reading tournament state from {json_file}...")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ JSON file not found. Run the main tournament simulation first.")
        return

    # Sort leaderboard by Elo (ascending) to get the worst performers
    leaderboard = data.get("leaderboard", [])
    leaderboard.sort(key=lambda x: x["Elo"])
    
    worst_players = leaderboard[:num_teams]
    # Extract the numeric ID from "Player X"
    target_ids = [int(p["Nome"].replace("Player ", "")) for p in worst_players]
    
    print(f"🗑️ Relegating top {num_teams} worst teams: {target_ids}")

    with open(python_file, 'r', encoding='utf-8') as f:
        file_content = f.read()

    for player_id in target_ids:
        new_team_block = generate_team_text(player_id, mon_names, abilities, moves_pool, items_pool)
        
        # Regex to find the specific player's multiline string block and replace it
        pattern = rf'player_{player_id}\s*=\s*\"\"\"[\s\S]*?\"\"\"'
        file_content = re.sub(pattern, new_team_block, file_content)

    with open(python_file, 'w', encoding='utf-8') as f:
        f.write(file_content)

    print(f"🔄 Successfully regenerated {num_teams} teams in '{python_file}'!")

if __name__ == "__main__":
    regenerate_worst_teams()