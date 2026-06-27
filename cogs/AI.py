import functools
import time
from MusicGameBot import GEMINI_API_KEY
from discord.ext import commands
from discord.ext.commands import Bot
from google import genai
from google.genai import types


class ChatCog(commands.Cog):
    SEARCH_MODEL_FALLBACKS = (
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    )
    NO_SEARCH_MODEL_FALLBACKS = (
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    )
    DEFAULT_SEARCH_ENABLED = True
    FALLBACK_RETRY_SECONDS = 60 * 60

    def __init__(self, bot: Bot):
        self.bot = bot
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.chats = {}
        self.search_settings = {}
        self.model_retry_after = {}

    def is_search_enabled(self, user_id: str) -> bool:
        return self.search_settings.get(user_id, self.DEFAULT_SEARCH_ENABLED)

    def get_model_fallbacks(self, user_id: str):
        if self.is_search_enabled(user_id):
            return self.SEARCH_MODEL_FALLBACKS
        return self.NO_SEARCH_MODEL_FALLBACKS

    def create_chat(self, model: str, search_enabled: bool, history=None):
        kwargs = {"model": model}
        if history:
            kwargs["history"] = history
        if search_enabled:
            grounding_tool = types.Tool(google_search=types.GoogleSearch())
            kwargs["config"] = types.GenerateContentConfig(tools=[grounding_tool])
        return self.client.chats.create(**kwargs)

    def get_chat(self, user_id: str, model: str):
        search_enabled = self.is_search_enabled(user_id)
        current = self.chats.get(user_id)
        if (
            current is not None
            and current["model"] == model
            and current["search_enabled"] == search_enabled
        ):
            return current["chat"]

        # A model fallback or search setting change must not discard the
        # conversation. Seed the replacement chat with the successful history
        # accumulated by the previous one.
        history = current["chat"].get_history() if current is not None else None
        chat = self.create_chat(model, search_enabled, history)
        self.chats[user_id] = {
            "chat": chat,
            "model": model,
            "search_enabled": search_enabled,
        }
        return chat

    def format_error(self, error: Exception) -> str:
        error_message = str(error)
        if GEMINI_API_KEY:
            error_message = error_message.replace(GEMINI_API_KEY, "[REDACTED]")
        if len(error_message) > 1500:
            error_message = f"{error_message[:1500]}..."
        return f"{type(error).__name__}: {error_message}"

    def is_quota_error(self, error: Exception) -> bool:
        error_text = f"{type(error).__name__}: {error}".lower()
        return any(
            keyword in error_text
            for keyword in ("quota", "resource_exhausted", "rate limit", "429")
        )

    def mark_model_quota_exhausted(self, user_id: str, model: str):
        self.model_retry_after[(user_id, model)] = (
            time.monotonic() + self.FALLBACK_RETRY_SECONDS
        )

    def get_available_models(self, user_id: str):
        now = time.monotonic()
        model_fallbacks = self.get_model_fallbacks(user_id)
        available_models = [
            model
            for model in model_fallbacks
            if self.model_retry_after.get((user_id, model), 0) <= now
        ]
        return available_models or [model_fallbacks[-1]]

    async def send_gemini_message(self, user_id: str, content):
        last_error = None
        available_models = self.get_available_models(user_id)
        for model in available_models:
            chat = self.get_chat(user_id, model)
            try:
                response = await self.bot.loop.run_in_executor(
                    None,
                    functools.partial(chat.send_message, content),
                )
                return response, model, None
            except Exception as e:
                last_error = e
                is_last_available_model = model == available_models[-1]
                if self.is_quota_error(e):
                    self.mark_model_quota_exhausted(user_id, model)
                if self.is_quota_error(e) and not is_last_available_model:
                    print(
                        f"Gemini quota reached on {model}. "
                        f"Falling back to the next model for 1 hour: {e}"
                    )
                    continue
                return None, model, e

        return None, available_models[-1], last_error

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if self.bot.user.mentioned_in(message) and self.bot.user in message.mentions:
            await self.handle_message(message)

    async def handle_message(self, message):
        user_id = str(message.author.id)
        content = message.content
        if self.bot.user in message.mentions:
            mention = f"<@!{self.bot.user.id}>"
            content = content.replace(mention, "").strip()
            mention = f"<@{self.bot.user.id}>"
            content = content.replace(mention, "").strip()

        async with message.channel.typing():
            try:
                image_bytes = None
                if message.attachments:
                    attachment = message.attachments[0]
                    if any(
                        attachment.filename.lower().endswith(ext)
                        for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]
                    ):
                        image_bytes = await attachment.read()

                if image_bytes:
                    image_part = types.Part.from_bytes(
                        data=image_bytes, mime_type=attachment.content_type
                    )
                    contents = [content, image_part]
                else:
                    contents = content

                response, model, error = await self.send_gemini_message(
                    user_id, contents
                )
                if error is not None:
                    error_message = self.format_error(error)
                    print(f"Error generating Gemini response with {model}: {error}")
                    await message.reply(
                        f"Gemini response generation failed.\n"
                        f"Model: {model}\n"
                        f"Cause: {error_message}"
                    )
                    return

                text_to_send = f"{response.text} ({model})"
                limit = 2000
                if len(text_to_send) <= limit:
                    await message.reply(text_to_send)
                else:
                    parts = []
                    while len(text_to_send) > 0:
                        parts.append(text_to_send[:limit])
                        text_to_send = text_to_send[limit:]
                    sent_message = await message.reply(parts[0])
                    for i in range(1, len(parts)):
                        sent_message = await sent_message.reply(parts[i])
            except Exception as e:
                print(f"Error generating Gemini response: {e}")
                await message.reply(
                    f"Gemini response generation failed.\n"
                    f"Cause: {self.format_error(e)}"
                )

    @commands.command(name="reset")
    async def reset_conversation(self, ctx):
        user_id = str(ctx.author.id)
        if user_id in self.chats:
            del self.chats[user_id]
            await ctx.send("Conversation reset.")
        else:
            await ctx.send("No active conversation to reset.")

    @commands.command(name="ai_search")
    async def ai_search(self, ctx, value: str = None):
        user_id = str(ctx.author.id)
        if value is None:
            status = "on" if self.is_search_enabled(user_id) else "off"
            await ctx.send(f"AI search is currently {status}.")
            return

        value = value.lower()
        if value == "on":
            self.search_settings[user_id] = True
            await ctx.send("AI search turned on.")
        elif value == "off":
            self.search_settings[user_id] = False
            await ctx.send("AI search turned off.")
        else:
            await ctx.send("Usage: !ai_search on / !ai_search off")


async def setup(bot: Bot):
    await bot.add_cog(ChatCog(bot))
