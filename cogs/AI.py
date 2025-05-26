from MusicGameBot import GEMINI_API_KEY
from discord.ext import commands
from discord.ext.commands import Bot
from google import genai


class ChatCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.chats = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        await self.bot.process_commands(message)
        if self.bot.user.mentioned_in(message):
            await self.handle_message(message)

    async def handle_message(self, message):
        user_id = str(message.author.id)
        if user_id not in self.chats:
            self.chats[user_id] = self.client.chats.create(
                model="gemini-2.5-flash-preview-05-20"
            )
        chat = self.chats[user_id]
        content = message.content
        async with message.channel.typing():
            try:
                if self.bot.user in message.mentions:
                    mention = f"<@!{self.bot.user.id}>"
                    content = content.replace(mention, "").strip()
                response = chat.send_message(content)
                await message.reply(response.text)
            except Exception as e:
                print(f"Error generating Gemini response: {e}")
                await message.reply("Error generating response.")

    @commands.command(name="reset")
    async def reset_conversation(self, ctx):
        user_id = str(ctx.author.id)
        if user_id in self.chats:
            del self.chats[user_id]
            await ctx.send("Conversation reset.")
        else:
            await ctx.send("No active conversation to reset.")


async def setup(bot: Bot):
    await bot.add_cog(ChatCog(bot))
