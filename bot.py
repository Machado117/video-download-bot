# Adapted from https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot.py
import logging
import asyncio
import time
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

class DownloadBot:
    def __init__(self, config, downloader, jellyfin):
        self.config = config
        self.downloader = downloader
        self.jellyfin = jellyfin
        self.lock = asyncio.Lock()

    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        await update.message.reply_html(
            rf"Hi {user.mention_html()}! Send me a video URL to download.",
            reply_markup=ForceReply(selective=True),
    )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        help_text = """
                    Available commands:
                    /start - Start the bot
                    /help - Show this help message
                    
                    Simply send a video URL to start downloading. I'll keep you updated on the progress!
                    """
        await update.message.reply_text(help_text)

    async def handle_download(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle video download requests."""
        progress_message = await update.message.reply_text("Starting download...", quote=True)
        last_update = 0

        async def progress_hook(d):
            nonlocal last_update
            current_time = time.time()

            async with self.lock:
                if current_time - last_update < self.config.update_interval:
                    return

                status = d['status']
                message = None

                if status == 'downloading':
                    downloaded = d.get('downloaded_bytes', 0)
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                    if total_bytes:
                        percentage = (downloaded / total_bytes) * 100
                        message = f"{percentage:.1f}% of {total_bytes/1048576:.2f}MiB"
                        last_update = current_time
                elif status == 'finished':
                    message = "Download completed! Processing file..."
                if message:
                    await progress_message.edit_text(message)

        try:
            success = await self.downloader.download(update.message.text, progress_hook)

            if success:
                self.jellyfin.refresh()
                final_message = "Download completed!"
            else:
                final_message = "Download failed!"
            async with self.lock:
                await progress_message.edit_text(final_message)

        except Exception as e:
            async with self.lock:
                await progress_message.edit_text(f"Download failed with error: {str(e)}")

    def run(self) -> None:
        """Start the bot."""
        application = Application.builder().token(self.config.telegram_token).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_download))

        application.run_polling(allowed_updates=Update.ALL_TYPES)
