import asyncio
import requests
from yt_dlp import YoutubeDL
from functools import partial

class VideoDownloader:
    def __init__(self, config):
        self.config = config
        self.loop = asyncio.get_event_loop()

    async def download(self, url, progress_callback):

        def _download():
            ytd_opts = {
                'progress_hooks': [
                    lambda d: self.loop.call_soon_threadsafe(
                        partial(asyncio.create_task, progress_callback(d))
                    )
                ],
                **self.config.ytdl_opts
            }

            try:
                with YoutubeDL(ytd_opts) as ydl:
                    return ydl.download([url]) == 0
            except Exception as e:
                print("Exception:", e)
                return False

        return await self.loop.run_in_executor(None, _download)

class JellyfinClient:
    def __init__(self, config):
        self.config = config

    def refresh(self):
        if self.config.jellyfin_url:
            try:
                requests.post(
                    f"{self.config.jellyfin_url}/Library/Refresh",
                    headers={"X-MediaBrowser-Token": self.config.jellyfin_token},
                    timeout=5,
                )
            except requests.RequestException as e:
                print(f"An error occurred while refreshing the library: {e}")