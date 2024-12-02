from textual.app import App

from app.screens.welcome import WelcomeScreen


class CmsInstaller(App):
    def on_mount(self) -> None:
        self.push_screen(WelcomeScreen())


app = CmsInstaller()
app.run()
