import json
import os
import sys

from notebook.services.kernels.kernelmanager import MappingKernelManager


def get_class(inner_class):

    if not issubclass(inner_class, MappingKernelManager):
        raise ValueError("inner class must be MappingKernelManager or sub-class")

    class SingletonKernelManager(inner_class):
        def start_kernel(self, kernel_id=None, path=None, **kwargs):
            kernel_id = None
            for kernel in self.list_kernels():
                if 'id' in kernel:
                    kernel_id = kernel['id']

            save_kernel_id = False
            if kernel_id is None:
                # this is were the standalone client expects the connection file
                # self.connection_dir = self.root_dir

                # prepare our special kernel
                self.kernel_spec_manager.kernel_dirs = [self.root_dir]
                kernel_name = 'singleton_kernel'
                kwargs['kernel_name'] = kernel_name
                kernel_dir = os.path.join(self.root_dir, kernel_name)
                os.mkdir(kernel_dir)
                kernel_spec = {
                    'argv': [sys.executable, '-m', 'jupyter_singleton.dummylauncher'],
                    'display_name': 'singleton_kernel',
                    'language': 'python'
                }
                kernel_path = os.path.join(kernel_dir, 'kernel.json')
                with open(kernel_path, 'w') as fp:
                    json.dump(kernel_spec, fp)

                save_kernel_id = True

            kernel_id = super(SingletonKernelManager, self).start_kernel(kernel_id, path, **kwargs)
            if save_kernel_id:
                kernel_id.add_done_callback(self.save_kernel_id)
            return kernel_id

        def save_kernel_id(self, kernel_id):
            path = os.path.join(self.root_dir, 'kernel_info.json')
            kernel_info = {
                'connection_dir': self.connection_dir,
                'kernel_id': kernel_id.result()
            }
            with open(path, 'w') as fp:
                json.dump(kernel_info, fp)

    return SingletonKernelManager
