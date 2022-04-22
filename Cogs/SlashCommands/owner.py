import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.utils import get, find
from discord.ext.commands import has_permissions, MissingPermissions, is_owner
from discord import app_commands

import os, json
import asyncio
from datetime import datetime
from glob import glob

#from easypymongodb import DB
import tweepy

ck = os.environ.get("ck")
cks = os.environ.get("cks")
at = os.environ.get("at")
ats = os.environ.get("ats")

auth = tweepy.OAuthHandler(ck, cks)
auth.set_access_token(at, ats)

api = tweepy.API(auth)
client = tweepy.Client(bearer_token = os.environ.get("bearer"))

class SlashOwner(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  async def postTweet(self, embed, tweet_media):
    channel = self.bot.get_channel(889449016138563634) #change
    msg = await channel.send(embed=embed)
    if tweet_media:
      msgg = await channel.send(tweet_media)
      await msg.publish()
      return await msgg.publish()
    return await msg.publish()

  async def postManual(self):
    response = client.get_users_tweets(id="558562910", tweet_fields=[
        "attachments", "author_id", "conversation_id", "created_at",
        "entities", "geo", "id", "in_reply_to_user_id", "lang",
        "possibly_sensitive", "referenced_tweets", "source", "text", "withheld"
    ], expansions=["attachments.media_keys"], media_fields=["type", "url"])
    rortos = response.data

    tweet = rortos[0].data
    tweet_text = tweet["text"]

    if "RT @" in tweet_text or "@rortos" in tweet_text:
      return
      
    tweet_media = False
    try:
      video_info = tweet.extended_entities["media"][0]["video_info"]
      tweet_media = video_info["variants"][0]["url"]
    except:
      pass

    media_details = response.includes["media"][0]["data"]["url"]
    
    try:
      t = tweet_text.index("https://")
      url = tweet_text[t:]
      tweet_text = tweet_text[:t].strip()
    except:
      pass

    try:
      rere = url.index(" ")
      url = url[:rere]
    except:
      pass
    if len(tweet_text) > 256:
      embed = discord.Embed(
        title = "New Post",
        description = tweet_text,
        url = url,
        colour = discord.Colour.blue()
      )
      embed.set_image(
        url = media_details
      )
    else:
      embed = discord.Embed(
        title = tweet_text,
        url = url,
        colour = discord.Colour.blue()
      )
      embed.set_image(
        url = media_details
      )
      #channel = self.bot.get_channel(889449016138563634) #change

    return await self.postTweet(embed, tweet_media)


 

  @commands.command(
    name = "sug"
  )
  @is_owner()
  async def _sug(self, ctx, message):
    embed = discord.Embed(
      description = message
    )
    msg = await ctx.send(embed=embed)
    return await ctx.send(msg.id)

  @commands.command(
    name = "image"
  )
  @is_owner()
  async def _image(self, ctx, messageid):
    message = await ctx.message.channel.fetch_message(messageid)
    embed = discord.Embed(
      description = message.embeds[0].description
    )
    
    imageurl = ctx.message.attachments[0].url
    embed.set_image(
      url = imageurl
    )
    return await message.edit(content="", embed=embed)





  
  @commands.command(
    name = "sync"
  )
  @is_owner()
  async def _sync(self, ctx):
    await self.bot.wait_until_ready()
    await self.bot.tree.sync(guild=discord.Object(665183274452254740))
    return await ctx.message.add_reaction("👍")

  @app_commands.command(
    name = "post"
  )
  @app_commands.checks.has_role(953961694403645471)
  async def _post(self, interaction):
    await self.postManual()
    return await interaction.response.send_message("Posted", ephemeral=True)

  @app_commands.command(
    name = "post-video"
  )
  @app_commands.describe(url="The video url")
  @app_commands.checks.has_role(953961694403645471)
  async def _post_video(self, interaction, url: str):
    channel = self.bot.get_channel(889449016138563634)
    msg = await channel.send(url)
    await msg.publish()
    return await interaction.response.send_message("Posted")
    
    
    
async def setup(bot):
  await bot.add_cog(SlashOwner(bot), guilds=[discord.Object(id=665183274452254740)])