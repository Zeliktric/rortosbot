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

class SlashStaff(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(
    name = "approve"
  )
  @app_commands.describe(suggestion_id="The suggestion ID to approve")
  @app_commands.checks.has_any_role(671297395413221377, 665183525925945372, 665206100697808937)
  async def _approve(self, interaction, suggestion_id: str):
    data = await interaction.client.getDBData("Feedback", "MemberIDs")
    data2 = await interaction.client.getDBData("Feedback", "Feedbacks")
    data3 = await interaction.client.getDBData("Feedback", "FeedbackIDs")

    try:
      user_id = data3[0][suggestion_id]
    except:
      await self.bot.logData(interaction.user, f"approve", f"Could not find suggestion with ID: {suggestion_id}")
      return await interaction.response.send_message(f"Could not find suggestion with ID: {suggestion_id}", ephemeral=True)

    try:
      messageid = data2[0][user_id][suggestion_id]["Message ID"]
      subject = data2[0][user_id][suggestion_id]["Subject"]
      feedback = data2[0][user_id][suggestion_id]["Feedback"]
      userid = data2[0][user_id][suggestion_id]["User ID"]
    except:
      await self.bot.logData(interaction.user, f"approve", f"Could not find suggestion with ID: {suggestion_id}")
      return await interaction.response.send_message(f"Could not find suggestion with ID: {suggestion_id}", ephemeral=True)

    if(data2[0][user_id][suggestion_id]["Approved"]):
      await self.bot.logData(interaction.user, f"approve", f"Cannot approve an approved suggestion!")
      return await interaction.response.send_message(f"Cannot approve an approved suggestion!", ephemeral=True)
    
    data2[0][user_id][suggestion_id]["Approved"] = True
    

    


    guild = await self.bot.guild()
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

    await self.bot.logData(interaction.user, f"approve", f"Approved {subject} with ID: {suggestion_id}")

    try:
      return await interaction.response.send_message(f"Approved {subject} with ID: {suggestion_id}", ephemeral=True)
    except:
      return await interaction.followup.send(f"Approved {subject} with ID: {suggestion_id}", ephemeral=True)

  @app_commands.command(
    name = "mod-delete"
  )
  @app_commands.describe(suggestion_id="The suggestion ID to delete")
  @app_commands.describe(reason="Reason of deletion")
  @app_commands.checks.has_any_role(671297395413221377, 665183525925945372, 665206100697808937)
  async def _mod_delete(self, interaction, suggestion_id: str, reason: str="Unspecified"):
    data = await interaction.client.getDBData("Feedback", "MemberIDs")
    data2 = await interaction.client.getDBData("Feedback", "Feedbacks")
    data3 = await interaction.client.getDBData("Feedback", "FeedbackIDs")
    data1 = await interaction.client.getDBData("Feedback", "MessageIDs")

    try:
      user_id = data3[0][suggestion_id]
    except:
      await self.bot.logData(interaction.user, f"mod-delete", f"Could not find suggestion with ID: {suggestion_id}")
      return await interaction.response.send_message(f"Could not find suggestion with ID: {suggestion_id}", ephemeral=True)

    try:
      messageid = data2[0][user_id][suggestion_id]["Message ID"]
      subject = data2[0][user_id][suggestion_id]["Subject"]
      feedback = data2[0][user_id][suggestion_id]["Feedback"]
      userid = data2[0][user_id][suggestion_id]["User ID"]
    except:
      await self.bot.logData(interaction.user, f"mod-delete", f"Could not find suggestion with ID: {suggestion_id}")
      return await interaction.response.send_message(f"Could not find suggestion with ID: {suggestion_id}", ephemeral=True)

    if(data2[0][user_id][suggestion_id]["Approved"]):
      await self.bot.logData(interaction.user, f"mod-delete", f"Cannot delete an approved suggestion!")
      return await interaction.response.send_message(f"Cannot delete an approved suggestion!", ephemeral=True)

    data[0][user_id].remove(suggestion_id)
    data2[0][user_id].pop(suggestion_id)
    data1[0].pop(str(messageid))
    data3[0].pop(suggestion_id)

    await interaction.client.postDBData("Feedback", "MemberIDs", data)
    await interaction.client.postDBData("Feedback", "Feedbacks", data2)
    await interaction.client.postDBData("Feedback", "FeedbackIDs", data3)
    await interaction.client.postDBData("Feedback", "MessageIDs", data1)

    guild = await self.bot.guild()
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

    await self.bot.logData(interaction.user, f"mod-delete", f"Deleted {subject} with ID: {suggestion_id}\nReason: {reason}")
    
    try:
      return await interaction.response.send_message(f"Deleted {subject} with ID: {suggestion_id}", ephemeral=True)
    except:
      return await interaction.followup.send(f"Deleted {subject} with ID: {suggestion_id}", ephemeral=True)


async def setup(bot):
  await bot.add_cog(SlashStaff(bot), guilds=[discord.Object(id=665183274452254740)])