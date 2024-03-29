import discord
import MusicPlayer as mp
from discord.ext import commands
from dotenv import dotenv_values

config = dotenv_values(".env")
intents = discord.Intents.all()
client = commands.Bot(command_prefix=config.get('COMMAND_PREFIX'), intents=intents)
musicPlayer = mp.MusicPlayer(client)


@client.command()
async def play(ctx, *args):
    await connect_channel(ctx)
    query_string = ' '.join(args)
    if not musicPlayer.voiceClient.is_playing():
        source = musicPlayer.play_song(query_string)
        await ctx.send("Playing: {title}".format(title=source['title']))
        return

    musicPlayer.add_song(query_string)
    await ctx.send("Song {query} added to queue".format(query=query_string))


async def connect_channel(ctx):
    if ctx.author.voice is None:
        return await ctx.send("You are not in a voice channel")

    if not is_connected(ctx):
        voice_channel = ctx.author.voice.channel
        await voice_channel.connect()
        musicPlayer.voiceClient = discord.utils.get(client.voice_clients)
        musicPlayer.ctx = ctx


def is_connected(ctx):
    voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()


@client.command()
async def leave(ctx):
    voice = musicPlayer.voiceClient
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@client.command()
async def pause(ctx):
    voice = musicPlayer.voiceClient
    if is_connected(ctx) and voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Currently no audio is playing.")


@client.command()
async def resume(ctx):
    voice = musicPlayer.voiceClient
    if is_connected(ctx) and voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")


@client.command()
async def stop(ctx):
    musicPlayer.clear_queue()
    musicPlayer.isStopped = True
    voice = musicPlayer.voiceClient
    if is_connected(ctx):
        voice.stop()
        await ctx.send('Stopped')
    else:
        await ctx.send('The bot is not connected')


@client.command()
async def skip(ctx):
    voice = musicPlayer.voiceClient
    if is_connected(ctx):
        voice.stop()


client.run(config.get('TOKEN'))
