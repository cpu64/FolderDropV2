from app.models.settings import SettingsDB, Settings


class SettingsController:
    def __init__(self):
        self.db = SettingsDB()

    def get_settings(self) -> Settings:
        return self.db.get()

    def update_settings(self, settings: Settings):
        self.db.update(settings)
