import json
import jupyter_singleton
import os
import sys
import tempfile
import time
import threading
import urllib
import uuid
import webbrowser

from IPython.core.interactiveshell import InteractiveShell
from ipykernel.kernelapp import IPKernelApp
from jupyter_client.launcher import launch_kernel
from jupyter_singleton.displaydatahook import DisplayDataHook

from tornado.platform.asyncio import AsyncIOLoop


class SingletonApp:

    kernel_app = None
    display_data_hook = DisplayDataHook()

    def __init__(self, browser_name=None):
        SingletonApp.singleton_ids = []
        SingletonApp.client_started = False

        self.notebook_dir = tempfile.mkdtemp(prefix='jupyter_singleton_')
        self.browser_name = browser_name

    def open_singleton(self, debug_redirect=False):
        """
        Opens a new browser-window running a single jupyter output-cell.
        After calling this function output printed via 'print' or displayed via 'IPython.display.display' will be shown
        in the output cell.

        NOTE: this function blocks until the browser window is started and ready to handle output

        :return:
        """

        # first register displayhook, so that the correct message parent is set in messages send to the browser
        thread_local_data = threading.local()
        if not hasattr(thread_local_data, 'has_displayhook') or not thread_local_data.has_displayhook:
            InteractiveShell.instance().display_pub.register_hook(self.display_data_hook)
            thread_local_data.has_displayhook = True

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

        if debug_redirect:
            url_parts = [
                'file://',
                os.path.abspath(os.path.join(os.path.abspath(jupyter_singleton.__file__), '..', 'debugredirect.html')),
                '?',
                'url=',
                urllib.parse.quote(url)
            ]
            url = ''.join(url_parts)

        browser = webbrowser.get(self.browser_name)
        browser.open(url, new=1)

        # poll until output-cell active
        started = False
        for _ in range(6000):
            if singleton_id in SingletonApp.singleton_ids:
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

    def _launch_server(self, server_parameters=None):
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

        return kernel_info

    def _launch_client(self, kernel_id):
        # we have to create the event-loop explicitly here since IOLoop.current() is prohibited outside of the main
        # thread
        AsyncIOLoop(make_current=True)

        # prepare parameters
        kernel_file = 'kernel-' + kernel_id + '.json'
        code_to_run = 'from jupyter_singleton.singletonapp import SingletonApp\n' + \
                      'SingletonApp.client_started=True'
        kernel_class = 'jupyter_singleton.singletonipkernel.SingletonIPythonKernel'

        parameters = {
            'connection_file': kernel_file,
            'code_to_run': code_to_run,
            'quiet': False,
            'kernel_class': kernel_class
        }

        # start jupyter client
        self.kernel_app = IPKernelApp(**parameters)
        self.kernel_app.initialize([])
        if hasattr(self.kernel_app.kernel, 'set_displaydatahook'):
            self.kernel_app.kernel.set_displaydatahook(self.display_data_hook)
        self.kernel_app.start()

    def _launch(self, server_parameters):
        kernel_info = self._launch_server(server_parameters)
        if kernel_info:
            threading.Thread(target=self._launch_client, args=(kernel_info['kernel_id'],)).start()
        else:
            raise IOError('kernel connection file was not written before timeout')

    def launch(self, server_parameters):
        """
        Launches the jupyter server and afterwards the jupyter client in a new thread
        The server will be launched in a new subprocess while the client will be launched in a new thread in the current
        process.
        NOTE: this function returns immediately. It does NOT block until jupyter server and jupyter client are ready to
              display something
        :param server_parameters: parameters to pass to the jupyter server
        :return:
        """
        threading.Thread(target=self._launch, args=(server_parameters,)).start()
