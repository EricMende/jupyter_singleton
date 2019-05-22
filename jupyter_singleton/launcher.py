import json
import os
import sys
import tempfile
import time
import threading
import uuid
import webbrowser

from ipykernel import kernelapp
from jupyter_client.launcher import launch_kernel


class JupyterSingleton:
    def __init__(self, callback, browser_name=None):
        JupyterSingleton.singleton_ids = []

        self.notebook_dir = tempfile.mkdtemp(prefix='jupyter_singleton_')
        self.callback = callback
        self.browser_name = browser_name

    def _start_callback(self):
        # poll until jupyter client ready
        started = False
        for _ in range(6000):
            if JupyterSingleton.client_started:
                started = True
                break
            time.sleep(0.1)
        if not started:
            raise IOError('client did not seem to start ... timed out')

        # TODO we should make sure that when errors occur in callback, they get printed to the consol
        self.callback(self.open_singleton)

    def open_singleton(self):
        """
        Opens a new browser-window running a single jupyter output-cell.
        After calling this function output printed via 'print' or displayed via 'IPython.display.display' will be shown
        in the output cell.

        NOTE: this function blocks until the browser window is started and ready to handle output

        :return:
        """
        server_info_path = os.path.join(self.notebook_dir, 'server_info.json')
        with open(server_info_path, "r") as f:
            server_info = json.load(f)
        singleton_id = str(uuid.uuid4())

        url_parts = [
            server_info['url'],
            'singletonnotebooks/',
            'Untitled.ipynb',
            '?token=',
            server_info['token'],
            '&singletonid=',
            singleton_id
        ]
        url = ''.join(url_parts)
        browser = webbrowser.get(self.browser_name)
        browser.open(url, new=1)

        # poll until output-cell active
        started = False
        for _ in range(6000):
            if singleton_id in JupyterSingleton.singleton_ids:
                started = True
                break
            time.sleep(0.1)
        if not started:
            raise IOError('display did not seem to start ... timed out')

    def _poll_and_read_kernel_info(self):
        path = os.path.join(self.notebook_dir, 'kernel_info.json')
        for _ in range(6000):
            if os.path.isfile(path):
                try:
                    with open(path, 'r') as f:
                        result = json.load(f)
                        return result
                except RuntimeError:
                    pass
            time.sleep(0.1)
        return None

    def launch_server(self, server_parameters=None):

        if server_parameters is None:
            server_parameters = dict()
        parameter_path = os.path.join(self.notebook_dir, 'parameters.json')
        with open(parameter_path, 'w') as parameter_fd:
            json.dump(server_parameters, parameter_fd)

        # start server
        cmd = [
            sys.executable,
            '-m', 'jupyter_singleton.serverlauncher',
            '--notebook-dir', self.notebook_dir,
        ]
        env = os.environ.copy()
        env.pop('PYTHONEXECUTABLE', None)
        launch_kernel(cmd, env=env)  # this function originally starts a kernel but can also be used to start the server

        # poll for the connection file to be written by server
        kernel_info = self._poll_and_read_kernel_info()

        if kernel_info:
            JupyterSingleton.client_started = False
            
            # start user callback
            threading.Thread(target=self._start_callback).start()

            # launch the actual jupyter client programm
            kernel_id = kernel_info['kernel_id']
            kernel_file = 'kernel-' + kernel_id + '.json'
            code_to_run = 'from jupyter_singleton.launcher import JupyterSingleton\n' + \
                          'JupyterSingleton.client_started=True'
            kernelapp.launch_new_instance(connection_file=kernel_file, code_to_run=code_to_run)
        else:
            raise IOError('kernel connection file was not written before timeout')


def launch(callback, browser_name=None, server_parameters=None):
    """
    This function launches both sides of a jupyter connection.
    First it launches an instance of a jupyter server in a subprocess.
    Then it also starts a jupyter client in the current thread and lets it connect to the server.
    However, before actually launching the client, this function calls the given callback in a new thread.
    The callback will be given a function that can be used to start a browser window with a singleton jupyter output
    cell. The remaining code in the callback will then be executed as if it where executed in the actual notebook
    itself. This means that output printed via 'print' or displayed via 'IPython.display.display' will be shown in the
    output cell.

    NOTE: This function does not return unless the jupyter_client gets killed!

    :param callback: function to be called when jupyter connection is made (Note that this 'launch' function does not
                     return)
    :param browser_name: name of the browser to be used when displaying the singleton output cell
    :param server_parameters parameters to forward to the main function of the jupyter server. See
           notebook.notebookapp.main.
    :return:
    """
    sd = JupyterSingleton(callback, browser_name=browser_name)
    sd.launch_server(server_parameters)
