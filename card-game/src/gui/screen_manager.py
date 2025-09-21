from pygame import display, event

class ScreenManager:
    def __init__(self):
        self.screens = {}
        self.current_screen = None

    def add_screen(self, name, screen):
        self.screens[name] = screen

    def set_screen(self, name):
        if name in self.screens:
            self.current_screen = self.screens[name]
            self.current_screen.on_enter()

    def update(self):
        if self.current_screen:
            self.current_screen.update()

    def draw(self, surface):
        if self.current_screen:
            self.current_screen.draw(surface)

    def handle_events(self):
        for e in event.get():
            if e.type == event.QUIT:
                display.quit()
            if self.current_screen:
                self.current_screen.handle_events(e)