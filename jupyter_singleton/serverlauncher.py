import json
import os
import sys
import time
import threading
import urllib

from jupyter_singleton import singletonkernelmanager

from notebook.notebookapp import NotebookApp


def start_kernel_connection(server_info_file):
    server_info = None
    for _ in range(600):
        try:
            with open(server_info_file, 'r') as f:
                server_info = json.load(f)
                break
        except IOError:
            time.sleep(0.1)

    if server_info:
        if 'token' not in server_info:
            raise IOError('token not in server info file')

        if 'url' not in server_info:
            raise IOError('url not in server info file')

        server_url = server_info['url'].strip('/')
        url = server_url + '/startkernel?token=' + server_info['token']

        contents = urllib.request.urlopen(url)

        print(contents)
    else:
        raise IOError('server info file was not written before timeout')


def _set_parameter_if_absent(parameter_map, parameter_name, parameter_value):
    if parameter_name not in parameter_map:
        parameter_map[parameter_name] = parameter_value


if __name__ == '__main__':
    # find notebook directory in arguments
    argv = sys.argv
    notebook_dir = None
    while argv:
        if argv[0] == '--notebook-dir':
            if len(argv) > 1:
                notebook_dir = argv[1]
                break
        argv = argv[1:]
    if notebook_dir is None:
        raise ValueError('no notebook directory given')
    if not os.path.isdir(notebook_dir):
        raise IOError('given notebook directory does not exist')

    # read parameters from file
    parameter_path = os.path.join(notebook_dir, 'parameters.json')
    if not os.path.isfile(parameter_path):
        raise IOError('parameter file does not exist: ' + parameter_path)
    with open(parameter_path, 'r') as parameter_fd:
        parameters = json.load(parameter_fd)

    # set further parameters
    info_file = os.path.join(notebook_dir, 'server_info.json')
    connection_file = os.path.join(notebook_dir, 'connection_file.json')
    _set_parameter_if_absent(parameters, 'extra_services', ['jupyter_singleton.handlers'])
    _set_parameter_if_absent(parameters, 'info_file', info_file)
    _set_parameter_if_absent(parameters, 'connection_file', connection_file)
    _set_parameter_if_absent(parameters, 'connection_dir', notebook_dir)
    _set_parameter_if_absent(parameters, 'open_browser', False)
    _set_parameter_if_absent(parameters, 'notebook_dir', notebook_dir)

    # start kernel connector, telling the server to connect to **the** client immediately after start
    threading.Thread(target=start_kernel_connection, args=(info_file, )).start()

    # wrap the kernel manager
    notebook_app = NotebookApp(**parameters)
    singleton_kernel_manager_class = singletonkernelmanager.get_class(notebook_app.kernel_manager_class)
    notebook_app.kernel_manager_class = singleton_kernel_manager_class

    # start the jupyter server
    notebook_app.initialize(argv=[])
    notebook_app.start()




