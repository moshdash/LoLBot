import os
import discord
from dotenv import load_dotenv
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import random
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

summoner_name = os.getenv('SUMMONER')
region = 'EUW1'  # e.g., NA1, EUW1, etc.
api_key = os.getenv('RIOTAPI')

# Get summoner ID
summoner_url = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={api_key}'
response = requests.get(summoner_url)
summoner_data = response.json()
if response.status_code == 200:
    encrypted_summoner_id = summoner_data['id']
else:
    print(f'Failed to retrieve summoner ID for {summoner_name}')

def current_rank():
    rank_url = f'https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}?api_key={api_key}'
    response_rank = requests.get(rank_url)
    rank_data = response_rank.json()
    tier = rank_data[0]['tier']
    tier_rank = rank_data[0]['rank']
    player_rank = tier.capitalize() + ' ' + tier_rank
    return player_rank

def promoCheckCurrentRank():
    rankUrl = f'https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}?api_key={api_key}'
    responseRank = requests.get(rankUrl)
    rankData = responseRank.json()
    tier = rankData[0]['tier']
    rank = rankData[0]['rank']
    return {'tier': tier, 'rank': rank}

tier = {
    'IRON': 0,
    'BRONZE': 1,
    'SILVER': 2,
    'GOLD': 3,
    'PLATINUM': 4,
    'DIAMOND': 5,
    'MASTER': 6,
    'GRANDMASTER': 7,
    'CHALLENGER': 8
}

rank = {
    'IV': 0,
    'III': 1,
    'II': 2,
    'I': 3
}

def get_random_time():
    random_hour = random.randint(11, 13)
    random_minute = random.randint(0, 59)
    return datetime.now().replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)

def schedule_next_random_time():
    random_time = get_random_time()
    scheduler.add_job(check_rank, 'cron', hour=random_time.hour, minute=random_time.minute)
    next_time = random_time + timedelta(days=1)
    scheduler.add_job(schedule_next_random_time, 'date', run_date=next_time)

client = discord.Client()
scheduler = AsyncIOScheduler()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await check_promotion_status()
    schedule_next_random_time()
    scheduler.start()

async def check_rank():
    if current_rank() not in ['Platinum IV', 'Platinum III', 'Platinum II', 'Platinum I']:
        message = f'<@271650232700370944> is currently {current_rank()} and hasn\'t reached his goal of getting to Platinum. What a loser!'
    else:
        message = f'<@271650232700370944> is FINALLY {current_rank()}. Now he can touch grass!'

    # Send message to Discord
    channel = client.get_channel(274579910230540288)
    await channel.send(message)

async def check_promotion_status():
    channel = client.get_channel(274579910230540288)

    currentRank = {'tier': 'GOLD', 'rank': 'II'}
    promoCheckRank = promoCheckCurrentRank()
    if promoCheckRank:
        currentTier = tier[currentRank['tier'].strip()]
        currentDivision = rank[currentRank['rank'].strip()]

        promoCheckTier = tier[promoCheckRank['tier'].strip()]
        promoCheckDivision = rank[promoCheckRank['rank'].strip()]

        if currentTier == promoCheckTier and currentDivision == promoCheckDivision:
            pass

        # User has made it to Platinum
        if currentTier == 4:
            message = f'Thats all folks! <@271650232700370944> has made it to {currentRank["tier"].capitalize()}'
            await channel.send(message)

        # User has gone up a division, but not a Tier
        if currentTier == promoCheckTier and currentDivision < promoCheckDivision:
            message = f'<@271650232700370944> is on that climb, but still a way to go. From {currentRank["tier"].capitalize()} {currentRank["rank"]} to {promoCheckRank["tier"].capitalize()} {promoCheckRank["rank"]}.'
            await channel.send(message)
            currentRank = promoCheckRank

        # User has gone down a division but not a Tier
        if currentTier == promoCheckTier and currentDivision > promoCheckDivision:
            message = f'F\'s in chat boys. <@271650232700370944> has dropped from {currentRank["tier"].capitalize()} {currentRank["rank"]} and is now in {promoCheckRank["tier"].capitalize()} {promoCheckRank["rank"]}'
            await channel.send(message)
            currentRank = promoCheckRank

        # User has gone down a Tier
        if currentTier > promoCheckTier:
            message = f'Avoid <@271650232700370944> at all costs today- he has dropped from {currentRank["tier"].capitalize()} {currentRank["rank"]} to {promoCheckRank["tier"].capitalize()} {promoCheckRank["rank"]}'
            await channel.send(message)
            currentRank = promoCheckRank

        # User has gone up a Tier
        if currentTier < promoCheckTier:
            message = f'Looks like someone was carried! <@271650232700370944> has made it from {currentRank["tier"].capitalize()} {currentRank["rank"]} to {promoCheckRank["tier"].capitalize()} {promoCheckRank["rank"]}.'
            await channel.send(message)
            currentRank = promoCheckRank

client.run(TOKEN)
