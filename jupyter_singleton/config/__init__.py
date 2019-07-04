import jupyter_singleton
import time

from jupyter_singleton.singletonapp import SingletonApp
from IPython.display import display as ipython_display


def launch(browser_name=None, server_parameters=None):
    """
    This function launches both sides of a jupyter connection.
    First it launches an instance of a jupyter server in a subprocess.
    Then it also starts a jupyter client in the current thread and lets it connect to the server.
    NOTE: this function returns immediately. It does NOT block until jupyter server and jupyter client are ready to
          display something. You will have to call wait_for_start() before you can use open_singleton() or display().
          Also ipywidget thinks it is not running inside jupyter before jupyter has started properly. So the call to
          wait_for_start must also be done BEFORE CONSTRUCTING ANY IPYWIDGET

    :param browser_name: name of the browser to be used when displaying the singleton output cell
    :param server_parameters parameters to forward to the main function of the jupyter server. See
           notebook.notebookapp.main.
    :return:
    """

    if jupyter_singleton.singleton_app is not None:
        return

    jupyter_singleton.singleton_app = SingletonApp(browser_name=browser_name)
    jupyter_singleton.singleton_app.launch(server_parameters)


def wait_for_start():
    """
    This function blocks until the jupyter client is properly started.
    This is important in two ways:
        1. open_singleton/display expects that the connection between server and client already works. Otherwise
           packages will be send over the network that no handler listens to
        2. ipywidget thinks it is not running inside of jupyter unless jupyter client is running properly. So widgets
           that are created before the client is done starting are corrupt and cannot be displayed in the cell. Therefor
           is is necessary to CALL THIS FUNCTION BEFORE CONSTRUCTING ANY IPYWIDGET!
    :return:
    """
    # poll until jupyter client ready
    started = False
    for _ in range(6000):
        if SingletonApp.client_started:
            started = True
            break
        time.sleep(0.1)
    if not started:
        raise IOError('client did not seem to start ... timed out')


def launch_and_wait(browser_name=None, server_parameters=None):
    """
    Launches the jupyter server and jupyter client and waits for them to be properly started.
    Note: This function blocks for some time which might be unnecessary if you have some processing to do before
          constructing your first ipywidget or calling open_singleton or display. You might want to consider calling
          launch() right at the beginning of your code and wait_for_start() before your first use of ipywidget,
          open_singleton and display, respectively. Then you won't need to call this function.

    :param browser_name: name of the browser to be used when displaying the singleton output cell
    :param server_parameters parameters to forward to the main function of the jupyter server. See
           notebook.notebookapp.main.
    :return:
    """
    launch(browser_name, server_parameters)
    wait_for_start()


def _check_started():
    if jupyter_singleton.singleton_app is None:
        raise RuntimeError("Never started jupyter. You have to call launch() or launch_and_wait() before this function")
    if not SingletonApp.client_started:
        raise RuntimeError("jupyter client might not have been started. You must call wait_for_start() before this " +
                           "function")


def open_singleton(debug_redirect=False):
    """
    Open up a new browser window and load an active jupyter notebook output cell.
    This output cell can then be interacted with: e.g. with IPython.display.display(my_widget)
    :return:
    """
    _check_started()
    if jupyter_singleton.singleton_app is not None:
        jupyter_singleton.singleton_app.open_singleton(debug_redirect=debug_redirect)


def display(widget):
    """
    Open up a new browser window and display widget in a jupyter notebook output cell
    :param widget: the widget to display
    :return:
    """
    _check_started()
    jupyter_singleton.singleton_app.open_singleton()
    ipython_display(widget)
