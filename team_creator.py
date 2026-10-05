import random

# Example lists - replace these with your full datasets
mon_names = ['Zapdos','Chansey','Tauros','Moltres','Articuno','Sylveon','Umbreon','Garchomp','Ariados','Mew','Ferrothorn','Kartana','Primeape','Virizion','Arbok','Skarmory','Regieleki','Victini','Jynx','Persian','Mewtwo', 'Dugtrio', 'Xatu', 'Azelf', 'Mienshao', 'Snorlax', 'Braviary', 'Alomomola', 'Cinccino', 'Slowbro', 'Octillery', 'Castform', 'Aerodactyl']
abilities = ['Unaware','Rough Skin','Serene Grace','Intimidate','Neutralizing Gas','Sand Stream','Pressure','Defiant','Mold Breaker','Pure Power','Trace','Justified','Good as Gold','Purifying Salt','Grassy Surge','Drizzle','Drought','Transistor','Unseen Fist','Stamina', 'Regenerator', 'Tinted Lens', 'Sap Sipper', 'Hustle', 'Sniper', 'Filter', 'Effect Spore']
moves_pool = ['Air Slash','Body Press','Toxic','U-turn','Rock Smash','Dazzling Gleam','Power-Up Punch','Fire Punch','Rapid Spin','Boomburst','Flame Charge','Overheat','Aqua Jet','Fishious Rend','Hydro Pump','Mega Drain','Power Whip','Nuzzle','Thunder','Ice Shard','Blizzard','Mach Punch','Close Combat','Acid','Gunk Shot','Mud Shot','Earthquake','Gust','Brave Bird','Confusion','Psystrike','Megahorn','Rock Tomb','Head Smash','Astonish','Shadow Ball','Shadow Bone','Twister','Draco Meteor','Snarl','Knock Off','Bullet Punch','Steel Beam','Fairy Wind','Play Rough', 'Steel Wing', 'Aura Sphere', 'Flare Blitz', 'Rock Slide', 'Aqua Tail', 'Body Slam']

# Added a pool of generic, non-choice, non-species-specific items
items_pool = [
    'Leftovers', 'Life Orb', 'Heavy-Duty Boots', 'Assault Vest', 
    'Rocky Helmet', 'Focus Sash', 'Sitrus Berry', 'Lum Berry', 
    'Expert Belt', 'Black Sludge', 'White Herb', 'Mental Herb', 
    'Power Herb', 'Red Card', 'Eject Button', 'Eject Pack', 
    'Weakness Policy', 'Clear Amulet', 'Covert Cloak', 'Loaded Dice'
]

natures = [
    "Hardy", "Lonely", "Brave", "Adamant", "Naughty",
    "Bold", "Docile", "Relaxed", "Impish", "Lax",
    "Timid", "Hasty", "Serious", "Jolly", "Naive",
    "Modest", "Mild", "Quiet", "Bashful", "Rash",
    "Calm", "Gentle", "Sassy", "Careful", "Quirky"
]

def generate_random_evs():
    """Generates a valid random EV spread (max 508 total, max 252 per stat)"""
    stats = ['HP', 'Atk', 'Def', 'SpA', 'SpD', 'Spe']
    evs = {stat: 0 for stat in stats}
    remaining_blocks = 508 // 4 
    
    while remaining_blocks > 0:
        stat = random.choice(stats)
        if evs[stat] < 252:
            evs[stat] += 4
            remaining_blocks -= 1
            
    ev_strings = [f"{value} {stat}" for stat, value in evs.items() if value > 0]
    return " / ".join(ev_strings)

def generate_random_pokemon(name, abils, moves, items):
    """Generates a single Pokemon using a provided name and random selections"""
    ability = random.choice(abils)
    item = random.choice(items) # Select a random item
    
    # Select 4 unique moves (or fewer if the pool is small)
    num_moves = min(len(moves), 4)
    selected_moves = random.sample(moves, num_moves)
    
    ev_spread = generate_random_evs()
    nature = random.choice(natures)
    
    # Format updated to include the item using the standard Showdown syntax (@ Item)
    lines = [
        f"{name} @ {item}",
        f"Ability: {ability}",
        f"EVs: {ev_spread}",
        f"{nature} Nature"
    ]
    for move in selected_moves:
        lines.append(f"- {move}")
        
    return "\n".join(lines)

def generate_team_text(player_num, names, abils, moves, items):
    """Generates a complete team of 6 unique random Pokemon"""
    pokemon_blocks = []
    
    # SPECIES CLAUSE FIX: Sample 6 unique names from the list upfront
    team_size = min(len(names), 6)
    team_names = random.sample(names, team_size)
    
    for name in team_names:
        pokemon_blocks.append(generate_random_pokemon(name, abils, moves, items))
    
    team_string = "\n\n".join(pokemon_blocks)
    return f'player_{player_num} = """\n{team_string}\n"""\n'

def main():
    filename = "teams.py"
    with open(filename, "w", encoding="utf-8") as file:
        for i in range(1, 101):
            # Pass all four lists into the generator
            team_code = generate_team_text(i, mon_names, abilities, moves_pool, items_pool)
            file.write(team_code)
            if i < 100: # Fixed this to match the loop range so it spaces out properly
                file.write("\n")
                
    print(f"Successfully generated 1000 teams of randomized chaos (with Items and Species Clause enforced)!")

if __name__ == "__main__":
    main()