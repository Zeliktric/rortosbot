import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.utils import get, find
from discord.ext.commands import has_permissions, MissingPermissions, is_owner
from discord import app_commands
from discord import Interaction
from discord.app_commands import AppCommandError, Command, ContextMenu

import os, urllib, asyncio, aiohttp, traceback, random
from datetime import datetime
from threading import Thread
from glob import glob
from typing import *

from Cogs.twitterbot import listen
from Cogs.UI.feedback import Feedback
from Cogs.UI.feedback import Reject

#os.system("kill 1")
try:
  from easypymongodb import DB
except:
  os.system("pip install easypymongodb")
  from easypymongodb import DB

from flask import Flask
app = Flask("")

@app.route("/")
def home():
  return "I'm Alive"

def run():
  app.run(host="0.0.0.0", port=8080, use_reloader=False)

def keep_alive():  
  t = Thread(target=run)
  t.start()



class MyBot(commands.Bot):
  
  def __init__(self):
    super().__init__(
      command_prefix = "r?",
      case_insensitive = True,
      intents = discord.Intents(
        members = True,
        guilds = True,
        messages = True,
        message_content = True,
        reactions = True
      ),
      activity = discord.Activity(
        type = discord.ActivityType.watching,
        name = f"Rortos-RFS Discord Server"
      ),
      help_command = None
    )
    self.initial_extensions = []

    c = glob("Cogs/SlashCommands/*.py")
    commands = [cog.replace(".py", "").replace("/", ".") for cog in c]
    for each in commands:
      self.initial_extensions.append(each)
    password = urllib.parse.quote(os.environ.get(f"db_password"))
    self._db = DB(f"mongodb+srv://Admin:{password}{os.environ.get(f'string')}")


  async def on_ready(self):
    print("I'm Alive!")

  async def setup_hook(self):
    #self.background_task.start()
    self.session = aiohttp.ClientSession()
    for ext in self.initial_extensions:
      await self.load_extension(ext)
    
    # self.add_view(RolesView())
    # self.add_view(VerifyView())
    # self.add_view(VotesView())

  async def generate_id(self):
    time = datetime.utcnow()
    num = random.randint(1, 1048575)
    string = f"{time.strftime('%H')}{time.strftime('%M')}{time.strftime('%S')}{num}"
    return hex(int(num)).split("x")[-1]
  
  async def close(self):
    await super().close()
    await self.session.close()

  @tasks.loop()
  async def background_task(self):
    await listen()

  async def create_embed(self, title, description, member, header, scmd=False, colour=discord.Colour.blue()):
    embed = discord.Embed(
      title = title,
      description = description,
      colour = colour,
      timestamp = datetime.utcnow()
    )
    if(header != False):
      embed.set_author(
        name = header,
        icon_url = member.display_avatar
      )
    if(scmd == False):
      embed.set_footer(
        text = "You can also use slash commands (/)"
      )
    return embed

  async def getDBData(self, dbName, colName):
    self._db.dbName = dbName
    self._db.colName = colName
    return self._db.findAll()

  async def postDBData(self, dbName, colName, data):
    self._db.dbName = dbName
    self._db.colName = colName
    self._db.deleteMany({})
    self._db.insertMany(data)

  async def guild(self):
    return self.get_guild(665183274452254740)

  async def logData(self, user, command, desc):
    guild = self.get_guild(761890780158754836)
    channel = await guild.fetch_channel(963831313520013412)

    description = f"""
**Command**
```{command}```
**User**
```{user}```
**Description**
```{desc}```
    """

    embed = await self.create_embed("", description, user, f"{user}", True)
    return await channel.send(embed=embed)


    


bot = MyBot()
tree = bot.tree

# Context Menus

@tree.context_menu(name="mod-delete", guild=discord.Object(id=665183274452254740))
@app_commands.checks.has_any_role(671297395413221377, 665183525925945372, 665206100697808937)
async def _mod_delete(interaction: discord.Interaction, message: discord.Message):
  data1 = await interaction.client.getDBData("Feedback", "MessageIDs")
  try:
    suggestion_id = data1[0][str(message.id)]
  except:
    await bot.logData(interaction.user, f"mod-delete (context menu)", "Selected message is not a feedback-idea message!")
    return await interaction.response.send_message("Selected message is not a feedback-idea message!", ephemeral=True)
  modal = Reject()
  await interaction.response.send_modal(modal)
  await modal.wait()
  reason = modal._reason

  
  data = await interaction.client.getDBData("Feedback", "MemberIDs")
  data2 = await interaction.client.getDBData("Feedback", "Feedbacks")
  data3 = await interaction.client.getDBData("Feedback", "FeedbackIDs")

  try:
    user_id = data3[0][suggestion_id]
  except:
    await bot.logData(interaction.user, f"mod-delete (context menu)", f"Could not find suggestion with ID: {suggestion_id}")
    return await interaction.send_message(f"Could not find suggestion with ID: {suggestion_id}", ephemeral=True)

  try:
    messageid = data2[0][user_id][suggestion_id]["Message ID"]
    subject = data2[0][user_id][suggestion_id]["Subject"]
    feedback = data2[0][user_id][suggestion_id]["Feedback"]
    userid = data2[0][user_id][suggestion_id]["User ID"]
  except:
    await bot.logData(interaction.user, f"mod-delete (context menu)", f"Could not find suggestion with ID: {suggestion_id}")
    return await interaction.send_message(f"Could not find suggestion with ID: {suggestion_id}", ephemeral=True)

  if(data2[0][user_id][suggestion_id]["Approved"]):
    await bot.logData(interaction.user, f"mod-delete (context menu)", f"Cannot delete an approved suggestion!")
    return await interaction.send_message(f"Cannot delete an approved suggestion!", ephemeral=True)

  data[0][user_id].remove(suggestion_id)
  data2[0][user_id].pop(suggestion_id)
  data1[0].pop(str(messageid))
  data3[0].pop(suggestion_id)

  await interaction.client.postDBData("Feedback", "MemberIDs", data)
  await interaction.client.postDBData("Feedback", "Feedbacks", data2)
  await interaction.client.postDBData("Feedback", "FeedbackIDs", data3)
  await interaction.client.postDBData("Feedback", "MessageIDs", data1)

  guild = await bot.guild()
  channel = await guild.fetch_channel(665229048179326976)
  message = await channel.fetch_message(messageid)
  await message.delete()

  member = await guild.fetch_member(userid)
  try:
    description = f"""
**Your Subject**
{subject}

**Your Feedback**
{feedback}

**Moderator**
{interaction.user}

**Reason**
{reason}
    """
    embed = await interaction.client.create_embed("Suggestion Deleted", description, interaction.user, False, True)
    await member.send(embed=embed)
  except:
    pass

  await bot.logData(interaction.user, f"mod-delete (context menu)", f"Deleted {subject} with ID: {suggestion_id}\nReason: {reason}")

  try:
    return await interaction.response.send_message(f"Deleted {subject} with ID: {suggestion_id}", ephemeral=True)
  except:
    return await interaction.followup.send(f"Deleted {subject} with ID: {suggestion_id}", ephemeral=True)
  
  

@tree.context_menu(name="approve", guild=discord.Object(id=665183274452254740))
@app_commands.checks.has_any_role(671297395413221377, 665183525925945372, 665206100697808937)
async def _approve(interaction: discord.Interaction, message: discord.Message):
  data1 = await interaction.client.getDBData("Feedback", "MessageIDs")
  try:
    suggestion_id = data1[0][str(message.id)]
  except:
    await bot.logData(interaction.user, f"approve (context menu)", f"Selected message is not a feedback-idea message!")
    return await interaction.response.send_message("Selected message is not a feedback-idea message!", ephemeral=True)
  data = await interaction.client.getDBData("Feedback", "MemberIDs")
  data2 = await interaction.client.getDBData("Feedback", "Feedbacks")
  data3 = await interaction.client.getDBData("Feedback", "FeedbackIDs")

  try:
    user_id = data3[0][suggestion_id]
  except:
    await bot.logData(interaction.user, f"approve (context menu)", f"Could not find suggestion with ID: {suggestion_id}")
    return await interaction.response.send_message(f"Could not find suggestion with ID: {suggestion_id}", ephemeral=True)

  try:
    messageid = data2[0][user_id][suggestion_id]["Message ID"]
    subject = data2[0][user_id][suggestion_id]["Subject"]
    feedback = data2[0][user_id][suggestion_id]["Feedback"]
    userid = data2[0][user_id][suggestion_id]["User ID"]
  except:
    await bot.logData(interaction.user, f"approve (context menu)", f"Could not find suggestion with ID: {suggestion_id}")
    return await interaction.response.send_message(f"Could not find suggestion with ID: {suggestion_id}", ephemeral=True)

  if(data2[0][user_id][suggestion_id]["Approved"]):
    await bot.logData(interaction.user, f"approve (context menu)", f"Cannot approve an approved suggestion!")
    return await interaction.response.send_message(f"Cannot approve an approved suggestion!", ephemeral=True)
  
  data2[0][user_id][suggestion_id]["Approved"] = True
  

  


  guild = await bot.guild()
  channel = await guild.fetch_channel(665229048179326976)
  message = await channel.fetch_message(messageid)
  await message.delete()

  member = await guild.fetch_member(userid)
  description = f"""
**Subject**
{subject}

**Feedback**
{feedback}

**Submitter**
{member.mention}
  
**Approved By**
{interaction.user.mention}
  """
  embed = await interaction.client.create_embed("New Suggestion", description, interaction.user, False, True, colour=discord.Colour.green())
  embed.set_footer(
    text = f"ID: {suggestion_id}"
  )
  channel = await guild.fetch_channel(682601030843629626)
  msg = await channel.send(embed=embed)
  await msg.add_reaction("<:Y_YES:715970721859239946>") 
  await msg.add_reaction("<:Y_Y_NO:715970748400926730>") 
  data2[0][user_id][suggestion_id]["Message ID"] = msg.id
  await interaction.client.postDBData("Feedback", "Feedbacks", data2)

  try:
    await member.send(f":partying_face: Your suggestion ({subject}) got approved!")
  except:
    pass

  await bot.logData(interaction.user, f"approve (context menu)", f"Approved {subject} with ID: {suggestion_id}")
  
  try:
    return await interaction.response.send_message(f"Approved {subject} with ID: {suggestion_id}", ephemeral=True)
  except:
    return await interaction.followup.send(f"Approved {subject} with ID: {suggestion_id}", ephemeral=True)
  

@tree.context_menu(name="suggest", guild=discord.Object(id=665183274452254740))
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
async def _suggest(interaction: discord.Interaction, message: discord.Message):
  await bot.logData(interaction.user, f"suggest (context menu)", f"Opened modal")
  return await interaction.response.send_modal(Feedback())

@tree.context_menu(name="delete", guild=discord.Object(id=665183274452254740))
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
async def _delete(interaction: discord.Interaction, message: discord.Message):
  data1 = await interaction.client.getDBData("Feedback", "MessageIDs")
  try:
    suggestion_id = data1[0][str(message.id)]
  except:
    await bot.logData(interaction.user, f"delete (context menu)", "Selected message is not a feedback-idea message!")
    return await interaction.response.send_message("Selected message is not a feedback-idea message!", ephemeral=True)

  data = await interaction.client.getDBData("Feedback", "MemberIDs")
  data2 = await interaction.client.getDBData("Feedback", "Feedbacks")
  data3 = await interaction.client.getDBData("Feedback", "FeedbackIDs")

  try:
    messageid = data2[0][str(interaction.user.id)][suggestion_id]["Message ID"]
    subject = data2[0][str(interaction.user.id)][suggestion_id]["Subject"]
  except:
    await bot.logData(interaction.user, f"delete (context menu)", "Selected message is not a feedback-idea message!")
    return await interaction.response.send_message("Selected feedback-idea message is not your suggestion!", ephemeral=True)

  if(data2[0][str(interaction.user.id)][suggestion_id]["Approved"]):
    await bot.logData(interaction.user, f"delete (context menu)", f"Cannot delete an approved suggestion!")
    return await interaction.response.send_message(f"Cannot delete an approved suggestion!", ephemeral=True)

  data[0][str(interaction.user.id)].remove(suggestion_id)
  data2[0][str(interaction.user.id)].pop(suggestion_id)
  data1[0].pop(str(message.id))
  data3[0].pop(suggestion_id)

  await interaction.client.postDBData("Feedback", "MemberIDs", data)
  await interaction.client.postDBData("Feedback", "Feedbacks", data2)
  await interaction.client.postDBData("Feedback", "MessageIDs", data1)
  await interaction.client.postDBData("Feedback", "FeedbackIDs", data3)

  guild = await bot.guild()
  channel = await guild.fetch_channel(665229048179326976)
  message = await channel.fetch_message(messageid)
  await message.delete()
  #await interaction.followup.send(embed=embed, ephemeral=False)

  await bot.logData(interaction.user, f"delete (context menu)", f"Deleted {subject} with ID: {suggestion_id}")
  
  try:
    return await interaction.response.send_message(f"Deleted {subject} with ID: {suggestion_id}", ephemeral=True)
  except:
    return await interaction.followup.send(f"Deleted {subject} with ID: {suggestion_id}", ephemeral=True)


@tree.error
async def app_command_error(
  interaction: Interaction,
  command: Union[Command, ContextMenu],
  error: AppCommandError
):
  if(isinstance(error, app_commands.MissingRole)):
    return await interaction.response.send_message("You do not have permission to use this command!", ephemeral=True)
  if(isinstance(error, app_commands.MissingAnyRole)):
    return await interaction.response.send_message("You do not have permission to use this command!", ephemeral=True)
  if(isinstance(error, app_commands.MissingPermissions)):
    return await interaction.response.send_message("You do not have permission to use this command!", ephemeral=True)
  if(isinstance(error, app_commands.CommandOnCooldown)):
    return await interaction.response.send_message(f"You are on cooldown! Retry in {round(error.retry_after)} seconds!", ephemeral=True)
  guild = await bot.guild()
  member = await guild.fetch_member(685842582856532059)
  await member.send(f"Error\n```{error}```")
  return await interaction.response.send_message(f"Sorry an error occured! Please try again later.", ephemeral=True)

#bot.loop.create_task(app.run_task("0.0.0.0", use_reloader=False))

keep_alive()
bot.run(os.environ.get("secret"))