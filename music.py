import discord
from discord import FFmpegPCMAudio
from discord.ext import commands
from youtube_dl import YoutubeDL

class Music(commands.Cog):
  # array holding queue for songs 
  music_queue = []

  # current voice channel bot is in
  vc = ''

  # description of the cog
  description = "This contains all the music functions."

  # boolean to check if it is currently is playing 
  is_playing = False

  # best settings for streaming in discord channel
  FFMPEG_OPTIONS = {'before_options': '-reconnect 1 - reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
  YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
  
  def _init_(self, bot):
    self.bot = bot

  @commands.command(name='join', description='This will make the bot join a voice channel')
  async def join(self, ctx):
    if ctx.author.voice is None:
      await ctx.send('You are not in a voice channel. Join a voice channel to connect the bot.')
    elif ctx.voice_client is None:
      await ctx.author.voice.channel.connect()
      await ctx.send(embed = discord.Embed(title="", description= "Joined your voice channel"))
    else:
      # if the bot is in the same channel and then don't display 
      if ctx.author.voice.channel is ctx.voice_client.channel:
        await ctx.send(embed = discord.Embed(title="", description= "Already in your voice channel"))
        return
      else:
        await ctx.voice_client.move_to(ctx.author.voice.channel)
        await ctx.send(embed = discord.Embed(title="", description= "Joined your voice channel"))

  @commands.command(name='disconnect', description='This will disconnect the bot from voice channel')
  async def disconnect(self, ctx):
    if ctx.voice_client is None:
      await ctx.send('The bot is already disconnected')
    else:
      await ctx.voice_client.disconnect()
      await ctx.send('Disconnected from your voice channel')

  def search(self, query):
    with YoutubeDL(self.YDL_OPTIONS) as ydl:
      try: 
        info = ydl.extract_info("ytsearch:%s" % query, download=False)['entries'][0]
      except Exception: 
        return False
    return info
  
  @commands.command(name='play', description='This will play a given song')
  async def play(self, ctx, *, query):
    if len(self.music_queue) == 0:
      if ctx.voice_client is None:
        await self.join(ctx)
        if ctx.voice_client is not None:
          await ctx.send(f'Now Searching: {query}')
          result = self.search(query)
          title = result['title']
          url = result['formats'][0]['url']
          await ctx.send(f'Now Playing: {title}')
          ctx.voice_client.play(FFmpegPCMAudio(url))
          ctx.voice_client.is_playing()
          self.music_queue.append([title, url])
          self.is_playing = True

      else:
        await ctx.send(f'Now Searching: {query}')
        result = self.search(query)
        title = result['title']
        url = result['formats'][0]['url']
        await ctx.send(f'Now Playing: {title}')
        ctx.voice_client.play(FFmpegPCMAudio(url))
        ctx.voice_client.is_playing()
        self.music_queue.append([title, url])
        self.is_playing = True
    else:
      await self.queue(ctx, query)

  async def queue(self, ctx, song):
    result = self.search(song)
    title = result['title']
    url = result['formats'][0]['url']
    if len(self.music_queue) > 0:
      await ctx.send(f'Queued: {title}')
      self.music_queue.append([title, url])

  @commands.command(name = 'list-queue', description = "This will queue up the given song")
  async def list_queue(self, ctx):
    embed = discord.Embed(title = "Song Queue", description = "")
    if len(self.music_queue) > 0:
      for music_list in self.music_queue:
        embed.add_field(name = "Song", value= music_list[0], inline=True)
      
      await ctx.send(embed=embed)
    else:
      embed.description = "Empty"
      await ctx.send(embed = embed)


  @commands.command(name = 'seek', description = "This will tell you the song at the specific spot")
  async def seek(self, ctx, index):
    if self.music_queue is not None and int(index) < len(self.music_queue):
      await ctx.send(embed = discord.Embed(title = f"Song: {index}", description = f"{self.music_queue[int(index)][0]}"))
    else:
      await ctx.send(embed = discord.Embed(title = f"Empty", description = f"The queue is empty."))

  
  @commands.command(name='skip', description='This will skip the current song')
  async def skip(self, ctx):
    if self.is_playing:
      if len(self.music_queue) > 1:
        ctx.voice_client.stop()
        ctx.voice_client.play(FFmpegPCMAudio(self.music_queue[1][1]))
        self.music_queue.pop(0)
      else:
        ctx.voice_client.stop()
        self.music_queue.pop(0)
    else:
      await ctx.send(embed = discord.Embed(title = "No song playing", description = ""))

  @commands.command(name='pause', description='This will pause a given song')
  async def pause(self, ctx):
    ctx.voice_client.pause()
    await ctx.send('The music has been paused')
  
  @commands.command(name='resume', description='This will resume the given song')
  async def resume(self, ctx):
    ctx.voice_client.resume()
    await ctx.send(embed = discord.Embed(title = "", description = 'The music has begun'))
  
