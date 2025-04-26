import discord
from discord.ext import commands
import random
import requests
import asyncio


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

current_guess = None
guess_active = False

def get_random_pokemon():
    pokemon_id = random.randint(1, 1010)
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
    response = requests.get(url)
    data = response.json()

    name = data['name']
    image_url = data['sprites']['other']['official-artwork']['front_default']

    return name, image_url

@bot.command()
async def guesspoke(ctx):
    global current_guess, guess_active
    if guess_active:
        await ctx.send("❗ Aktualnie trwa już zgadywanka! Poczekaj aż się skończy.")
        return

    name, image_url = get_random_pokemon()
    current_guess = name.lower()
    guess_active = True

    await ctx.send("Zgadnij tego Pokémona!")
    await ctx.send(image_url)

    # Odczekaj 30 sekund na zgadywanie
    await asyncio.sleep(30)

    if guess_active:
        await ctx.send(f"❌ Nikt nie zgadł! To był **{current_guess.capitalize()}**.")
        current_guess = None
        guess_active = False

@bot.event
async def on_message(message):
    global current_guess, guess_active
    await bot.process_commands(message)

    if guess_active and current_guess and not message.author.bot:
        if message.content.lower() == current_guess:
            await message.channel.send(f"🎉 Brawo {message.author.mention}! To był **{current_guess.capitalize()}**!")
            current_guess = None
            guess_active = False

# Fakty o generacjach Pokémonów
generation_facts = {
    1: "Generacja 1 (Red/Blue) wprowadziła pierwszy Pokédex i 151 Pokémonów. Po raz pierwszy wprowadzono walki Pokémonów i trening.",
    2: "Generacja 2 (Gold/Silver) dodała system dnia i nocy oraz nowe typy: stalowy i ciemny. Wprowadzono także 100 nowych Pokémonów.",
    3: "Generacja 3 (Ruby/Sapphire) wprowadziła nowe regiony i zaczęła używać GBA. Dodano 135 nowych Pokémonów.",
    4: "Generacja 4 (Diamond/Pearl) dodała mechanikę ewolucji z użyciem kamieni i nowe formy regionów. Dodano 107 nowych Pokémonów.",
    5: "Generacja 5 (Black/White) dodała najwięcej Pokémonów z każdej generacji, aż 156 nowych! Dodała również mechanikę 3D w walce.",
    6: "Generacja 6 (X/Y) wprowadziła typ wróżki i 3D w grafice. Dodano 72 nowe Pokémony.",
    7: "Generacja 7 (Sun/Moon) zrewolucjonizowała system Z-moves, a także zmieniła strukturę gier, eliminując tradycyjne sale. Dodano 88 Pokémonów.",
    8: "Generacja 8 (Sword/Shield) wprowadziła Dynamaxing i gigantyczne formy Pokémonów. Dodano 96 nowych Pokémonów.",
    9: "Generacja 9 (Scarlet/Violet) wprowadziła otwarty świat oraz nowe formy i mechaniki, takie jak Terastal. Dodano 103 nowe Pokémony."
}

# Funkcja do pobierania danych o Pokémona z konkretnej generacji
def get_random_pokemon_from_generation(gen):
    url = f"https://pokeapi.co/api/v2/generation/{gen}/"
    response = requests.get(url)
    data = response.json()

    pokemon = random.choice(data['pokemon_species'])
    pokemon_name = pokemon['name']

    pokemon_url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_name}/"
    response = requests.get(pokemon_url)
    data = response.json()

    description = None
    for entry in data['flavor_text_entries']:
        if entry['language']['name'] == 'en':  # angielski opis
            description = entry['flavor_text']
            break

    pokemon_id = data['id']
    image_url = f"https://assets.pokemon.com/assets/cms2/img/pokedex/full/{str(pokemon_id).zfill(3)}.png"

    return pokemon_name, description, image_url

@bot.command()
async def rapoke(ctx):
    generation = random.randint(1, 9)
    pokemon_name, description, image_url = get_random_pokemon_from_generation(generation)

    # Pobierz dane o pokemonie z PokeAPI dla statystyk
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}")
    if response.status_code != 200:
        await ctx.send("❗ Nie udało się pobrać pełnych danych o Pokémonie.")
        return

    data = response.json()

    stats = "\n".join([f"**{s['stat']['name'].capitalize()}**: {s['base_stat']}" for s in data['stats']])

    embed = discord.Embed(
        title=f"Pokémon z generacji {generation}: {pokemon_name.capitalize()} (ID: {data['id']})",
        description=description,
        color=discord.Color.random()
    )
    embed.set_image(url=image_url)
    embed.add_field(name="Statystyki", value=stats, inline=False)

    generation_fact = generation_facts[generation]
    embed.add_field(name="Ciekawostka o tej generacji:", value=generation_fact, inline=False)

    await ctx.send(embed=embed)

# Komenda do wyświetlania faktów o generacjach
@bot.command()
async def pokefact(ctx, generation: int):
    if 1 <= generation <= 9:
        fact = generation_facts[generation]
        await ctx.send(f"Ciekawostka o generacji {generation}: {fact}")
    else:
        await ctx.send("Podaj liczbę od 1 do 9, aby uzyskać fakt o generacji.")

# Komenda do pomocy (help)
@bot.command()
async def pomoc(ctx):
    help_message = """
    **📖 Komendy dostępne na serwerze:**

    📌 **!rapoke**  
    ➝ Losuje Pokémona z losowej generacji, wysyła jego obrazek, opis z Pokédexa, statystyki i ciekawostkę o tej generacji.

    📌 **!pokefact [numer generacji]**  
    ➝ Wyświetla ciekawostkę o podanej generacji Pokémonów (od 1 do 9).  
    *Przykład:* `!pokefact 5`

    📌 **!guesspoke**  
    ➝ Bot wysyła obrazek losowego Pokémona (bez nazwy). Użytkownicy mają 30 sekund na zgadnięcie. Jeśli ktoś odgadnie — bot gratuluje. Jeśli nie — po 30 sekundach podaje prawidłową nazwę.

    📌 **!pomoc**  
    ➝ Wyświetla ten komunikat.
    """

    await ctx.send(help_message)


bot.run('token')
