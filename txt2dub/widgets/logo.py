from textual.widgets import Static


LOGO = r"""
  __             __   ________      .___       ___.
_/  |_ ___  ____/  |_ \_____  \   __| _/ __ __ \_ |__
\   __\\  \/  /\   __\ /  ____/  / __ | |  |  \ | __ \
 |  |   >    <  |  |  /       \ / /_/ | |  |  / | \_\ \
 |__|  /__/\_ \ |__|  \_______ \\____ | |____/  |___  /
             \/               \/     \/             \/
"""

class Logo(Static):
    """The txt2dub logo."""

    def render(self):
        return LOGO[1:-1]
