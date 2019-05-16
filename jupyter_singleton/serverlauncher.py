import json
import os
import sys
import time
import threading
import urllib

from notebook.notebookapp import main


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

    # collect parameters
    info_file = os.path.join(notebook_dir, 'server_info.json')
    connection_file = os.path.join(notebook_dir, 'connection_file.json')
    params = {
        'extra_services': ['jupyter_singleton.handlers'],
        'info_file': info_file,
        'connection_file': connection_file,
        'connection_dir': notebook_dir,
        'kernel_manager_class': 'jupyter_singleton.singletonkernelmanager.SingletonKernelManager'
    }

    # start kernel connector
    threading.Thread(target=start_kernel_connection, args=(info_file, )).start()

    # start jupyter server
    sys.exit(main(**params))
