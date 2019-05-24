import jupyter_singleton
from jupyter_singleton import config as singleton_config

if jupyter_singleton.singleton_app is None:
    singleton_config.launch_and_wait()

# alias
open_singleton = singleton_config.open_singleton
display = singleton_config.display
