import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.utils import get, find
from discord.ext.commands import has_permissions, MissingPermissions, is_owner
from discord import app_commands

import os
import asyncio
from datetime import datetime
from glob import glob
from typing import *

from easypymongodb import DB
from Cogs.UI.feedback import Feedback

cooldown = app_commands.checks.cooldown(1, 10)


class SlashFeedback(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    
  # @app_commands.command(
  #   name = "attach"
  # )
  # @app_commands.checks.cooldown(1, 30, key=lambda i: (i.guild_id, i.user.id))
  # async def _attach(self, interaction: discord.Interaction, suggestion_id: str):
  #   if(suggestion_id == "no_ids_could_be_found"):
  #     await self.bot.logData(interaction.user, f"attach", "You have no available suggestions to attach an image to!")
  #     return await interaction.response.send_message("You have no available suggestions to attach an image to!", ephemeral=True)
  #   try:
  #     imageurl = interaction.message.attachments[0].url
  #   except:
  #     await self.bot.logData(interaction.user, "attach", "You didn't attach any image!" )
  #     return await interaction.response.send_message("You didn't attach any image!", ephemeral=True)

  #   data2 = await interaction.client.getDBData("Feedback", "Feedbacks")

  #   messageid = data2[0][str(interaction.user.id)][suggestion_id]["Message ID"]

  #   if(data2[0][str(interaction.user.id)][suggestion_id]["Approved"]):
  #     await self.bot.logData(interaction.user, f"delete", f"Cannot delete an approved suggestion!")
  #     return await interaction.response.send_message(f"Cannot delete an approved suggestion!", ephemeral=True)

  #   embed = await interaction.client.create_embed(interaction.message.embeds[0].title, interaction.message.embeds[0].description, interaction.user, f"{interaction.user}'s Feedback Idea", True)
  #   embed.set_footer(
  #     text = f"ID: {interaction.message.embeds[0].footer}"
  #   )
  #   embed.set_image(
  #     url = imageurl
  #   )
  #   channel = await interaction.guild.fetch_channel(665229048179326976)
  #   message = await channel.fetch_message(messageid)
  #   return await message.edit(content="", embed=embed)
      
  
  # @_attach.autocomplete("suggestion_id")
  # async def _attach_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
  #   data = await interaction.client.getDBData("Feedback", "MemberIDs")
  #   data2 = await interaction.client.getDBData("Feedback", "Feedbacks")
  #   try:
  #     ids = data[0][str(interaction.user.id)]
  #     return [
  #       app_commands.Choice(name=f"{data2[0][str(interaction.user.id)][id]['Subject'].replace(' ', '_').lower()}-{id}", value=id)
  #       for id in ids if current.lower() in id.lower()
  #     ][:25]
  #   except:
  #     ids = ["no_ids_could_be_found"]
  #     return [
  #       app_commands.Choice(name=id, value=id) 
  #       for id in ids if current.lower() in id.lower()
  #     ]

  

  @app_commands.command(
    name = "suggest"
  )
  @app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
  async def _suggest(self, interaction):
    await self.bot.logData(interaction.user, f"suggest", f"Opened modal")
    return await interaction.response.send_modal(Feedback())
  
    
  @app_commands.command(
    name = "delete"
  )
  @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
  async def _delete(self, interaction: discord.Interaction, suggestion_id: str):
    if(suggestion_id == "no_ids_could_be_found"):
      await self.bot.logData(interaction.user, f"delete", "You have no available suggestions to delete!")
      return await interaction.response.send_message("You have no available suggestions to delete!", ephemeral=True)
    data = await interaction.client.getDBData("Feedback", "MemberIDs")
    data2 = await interaction.client.getDBData("Feedback", "Feedbacks")
    data1 = await interaction.client.getDBData("Feedback", "MessageIDs")
    data3 = await interaction.client.getDBData("Feedback", "FeedbackIDs")

    messageid = data2[0][str(interaction.user.id)][suggestion_id]["Message ID"]
    subject = data2[0][str(interaction.user.id)][suggestion_id]["Subject"]

    if(data2[0][str(interaction.user.id)][suggestion_id]["Approved"]):
      await self.bot.logData(interaction.user, f"delete", f"Cannot delete an approved suggestion!")
      return await interaction.response.send_message(f"Cannot delete an approved suggestion!", ephemeral=True)

    data[0][str(interaction.user.id)].remove(suggestion_id)
    data2[0][str(interaction.user.id)].pop(suggestion_id)
    data1[0].pop(str(messageid))
    data3[0].pop(suggestion_id)

    await interaction.client.postDBData("Feedback", "MemberIDs", data)
    await interaction.client.postDBData("Feedback", "Feedbacks", data2)
    await interaction.client.postDBData("Feedback", "MessageIDs", data1)
    await interaction.client.postDBData("Feedback", "FeedbackIDs", data3)

    guild = await self.bot.guild()
    channel = await guild.fetch_channel(665229048179326976)
    message = await channel.fetch_message(messageid)
    await message.delete()

    await self.bot.logData(interaction.user, f"delete", f"Deleted {subject} with ID: {suggestion_id}")

    try:
      return await interaction.response.send_message(f"Deleted {subject} with ID: {suggestion_id}", ephemeral=True)
    except:
      return await interaction.followup.send(f"Deleted {subject} with ID: {suggestion_id}", ephemeral=True)
  
  @_delete.autocomplete("suggestion_id")
  async def _delete_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    data = await interaction.client.getDBData("Feedback", "MemberIDs")
    data2 = await interaction.client.getDBData("Feedback", "Feedbacks")
    try:
      ids = data[0][str(interaction.user.id)]
      return [
        app_commands.Choice(name=f"{data2[0][str(interaction.user.id)][id]['Subject'].replace(' ', '_').lower()}-{id}", value=id)
        for id in ids if current.lower() in id.lower()
      ][:25]
    except:
      ids = ["no_ids_could_be_found"]
      return [
        app_commands.Choice(name=id, value=id) 
        for id in ids if current.lower() in id.lower()
      ]

    
    
  


async def setup(bot):
  await bot.add_cog(SlashFeedback(bot), guilds=[discord.Object(id=665183274452254740)])