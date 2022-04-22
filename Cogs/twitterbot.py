import tweepy, os, asyncio, discord
from tweepy import Stream, OAuthHandler
from Cogs.SlashCommands.owner import SlashOwner

ck = os.environ.get("ck")
cks = os.environ.get("cks")
at = os.environ.get("at")
ats = os.environ.get("ats")

auth = tweepy.OAuthHandler(ck, cks)
auth.set_access_token(at, ats)

api = tweepy.API(auth)

class Listener(tweepy.Stream):

  def on_connect(self):
    print("Connected!")

  def on_error(self, status):
    if status == 420:
      return False

  def on_status(self, status):
    tweet_text = status.text
    
    if "RT @" in tweet_text or "@rortos" in tweet_text.lower() or status.in_reply_to_status_id:
      return

    tweet_media = False
    try:
      video_info = status.extended_entities["media"][0]["video_info"]
      tweet_media = video_info["variants"][0]["url"]
    except:
      pass

    try:
      media_details = response.includes["media"][0]["data"]["url"]
    except:
      return

    try:
      t = tweet_text.index("https://")
      url = tweet_text[t:]
      tweet_text = tweet_text[:t].strip()
    except:
      pass
    if len(tweet_text) > 256:
      embed = discord.Embed(
        title = "New Post",
        description = tweet_text,
        url = url,
        colour = discord.Colour.blue()
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
    asyncio.run(SlashOwner.postTweet(embed, tweet_media))


async def listen():
  twitter_stream = Listener(ck, cks, at, ats)
  twitter_stream.filter(follow=["558562910"], threaded=True)

  while (True):
    if not twitter_stream.running:
      await asyncio.sleep(5)
      twitter_stream = Listener(ck, cks, at, ats)
      twitter_stream.filter(follow=["558562910"], threaded=True)
    else:
      await asyncio.sleep(5)