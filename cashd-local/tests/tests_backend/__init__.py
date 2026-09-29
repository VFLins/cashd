import toga

if toga.backend == "toga_gtk":
    from .gtk import *
elif toga.backend == "toga_winforms":
    from .winforms import *
else:
    raise NotImplementedError(f"No tests specified for backend {toga.backend}")