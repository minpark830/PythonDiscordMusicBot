import discord 
from discord.ext import commands
import os 
from music import Music

#Attribute for MyHelp class, controlling name, aliases, and cooldown
attributes = {
   'name': "help",
   'aliases': ["helper", "helps"],
   'cooldown': commands.Cooldown(2, 5.0, commands.BucketType.user)
} 

help_object = commands.HelpCommand(command_attrs=attributes)

# creating bot object with commands.bot 
bot = commands.Bot(command_prefix='!')
token = os.environ['TOKEN']

# adding a cog(it is like a module) to the bot 
bot.add_cog(Music(bot))

#iterator variable 
count = 0
# array of potential greetings
greetings = ['Hello', 'Salutations','Hola', 'Sup']

@bot.command(name='hello', description='Saying hello to the bot')
async def hello(ctx): 
  global count
  await ctx.send(f'{greetings[count%4]} {ctx.author.name}')
  count+=1

# This the help class 
class My_help(commands.HelpCommand):
  #Overrides inherited function to removed alias names and clean up the output
  def get_command_signature(self, command):
        return '%s%s %s' % (self.clean_prefix, command.qualified_name, command.signature)

  # Error function
  async def send_error_message(self, error):
    embed = discord.Embed(title="Error", description=error)
    channel = self.get_destination()
    await channel.send(embed=embed)

  # !help function
  async def send_bot_help(self, mapping):
    embed = discord.Embed(title = "Help Commands") #Creates embed object
    for cog, specific_commands in mapping.items(): 
      command_signatures = [self.get_command_signature(c) for c in specific_commands]
      if command_signatures:
        cog_name = getattr(cog, "qualified_name", "Main")
        embed.add_field(name=cog_name, value="\n".join(command_signatures),inline=True)
    channel = self.get_destination()
    await channel.send(embed=embed)

  # !help <command> Does not work
  async def send_command_help(self, command):
    channel = self.get_destination()
    await channel.send(embed= discord.Embed(title = command.signature, description = command.description))

  # !help <cog> 
  async def send_cog_help(self, cog):
    channel = self.get_destination()
    embed= discord.Embed(title = "", description = cog.description)
    await channel.send(embed=embed)
  
  '''@help.error
  async def help_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      await ctx.send(embed = discord.Embed(title = "You are on cooldown!", description = f"Try again in {error.retry_after:.2f}s"))
  '''


  
# This notifies us that the bot is currently active 
@bot.event
async def on_ready():
  print('Bot is Online')

#@bot.event
#async def on_voice_state_update(data):
#  return


# setting up the help command on the bot
bot.help_command = My_help(command_attrs=attributes)

# run the bot
bot.run(token)

