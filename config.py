import yaml
from pathlib import Path

class Config:
    def __init__(self, config_path="config.yaml"):
        self.config = None
        self.config_path = Path(config_path)
        self.load_config()

    def load_config(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    @property
    def telegram_token(self):
        return self.config['telegram']['token']

    @property
    def jellyfin_token(self):
        return self.config['jellyfin']['api_token']

    @property
    def jellyfin_url(self):
        return self.config.get('jellyfin', {}).get('url')

    @property
    def ytdl_opts(self):
        return self.config['downloader'].get('ytdl_opts', {})

    @property
    def update_interval(self):
        return self.config['downloader']['update_interval']