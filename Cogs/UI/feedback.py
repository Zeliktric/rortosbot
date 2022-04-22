from discord import ui
import discord
from datetime import datetime

class Reject(ui.Modal, title="Reject Feedback Idea"):
  _reason = "Unspecified"
    
  reason = discord.ui.TextInput(
    label = "Reason",
    style = discord.TextStyle.long,
    max_length = 100
  )

  async def on_submit(self, interaction: discord.Interaction):
    self._reason = self.reason.value 
    await interaction.response.send_message("Deleting...", ephemeral=True)
  

class Feedback(ui.Modal, title="RFS Feedback Idea"):
  subject = discord.ui.TextInput(
    label = "Subject",
    style = discord.TextStyle.short,
    placeholder = "My Feature Request",
    required = True,
    max_length = 20,
  )
  
  feedback = discord.ui.TextInput(
    label = "Feedback Idea",
    style = discord.TextStyle.long,
    placeholder = "My feature request for RFS is...",
    required = True,
    max_length = 500,
  )


  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.send_message(f"Thanks for your feedback, {interaction.user}!", ephemeral=True)
    embed = await interaction.client.create_embed(f"{self.subject.value}", f"{self.feedback.value}", interaction.user, f"{interaction.user}'s Feedback Idea", True)
    x = await interaction.client.generate_id()
    embed.set_footer(
      text = f"ID: {x}"
    )
    channel = await interaction.guild.fetch_channel(665229048179326976)
    msg = await channel.send(embed=embed)
    await msg.add_reaction("<:Y_YES:715970721859239946>") 
    await msg.add_reaction("<:Y_Y_NO:715970748400926730>") 

    data = await interaction.client.getDBData("Feedback", "Feedbacks")
    try:
      xx = data[0]
    except:
      data.append({})

    try:
      p = data[0][str(interaction.user.id)]
      data[0][str(interaction.user.id)][x] = {
        "User ID": interaction.user.id,
        "Message ID": msg.id,
        "Subject": self.subject.value,
        "Feedback": self.feedback.value,
        "Time": datetime.utcnow(),
        "Approved": False
      }
    except:
      
      data[0][str(interaction.user.id)] = {
        x: {
          "User ID": interaction.user.id,
          "Message ID": msg.id,
          "Subject": self.subject.value,
          "Feedback": self.feedback.value,
          "Time": datetime.utcnow(),
          "Approved": False 
        }
      }

    await interaction.client.postDBData("Feedback", "Feedbacks", data)

    data = await interaction.client.getDBData("Feedback", "MessageIDs")
    try:
      o = data[0]
    except:
      data.append({})

    data[0][str(msg.id)] = x

    await interaction.client.postDBData("Feedback", "MessageIDs", data)

    data = await interaction.client.getDBData("Feedback", "MemberIDs")
    try:
      xx = data[0]
    except:
      data.append({})

    try:
      data[0][str(interaction.user.id)].append(x)
    except:
      data[0][str(interaction.user.id)] = [x]

    await interaction.client.postDBData("Feedback", "MemberIDs", data)

    data = await interaction.client.getDBData("Feedback", "FeedbackIDs")
    try:
      xx = data[0]
    except:
      data.append({})

    try:
      data[0][x] = str(interaction.user.id)
    except:
      data[0][x] = str(interaction.user.id)

    return await interaction.client.postDBData("Feedback", "FeedbackIDs", data)
    

  async def on_error(self, error: Exception, interaction: discord.Interaction) -> None:
    await interaction.response.send_message("Oops! Something went wrong.", ephemeral=True)

    # Make sure we know what the error actually is
    traceback.print_tb(error.__traceback__)