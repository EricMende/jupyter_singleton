from ipykernel.ipkernel import IPythonKernel


class SingletonIPythonKernel(IPythonKernel):
    display_data_hook = None

    def __init__(self, **kwargs):
        super(SingletonIPythonKernel, self).__init__(**kwargs)

    def set_parent(self, ident, parent):
        if parent is not None and 'msg_type' in parent and parent['msg_type'] == 'execute_request' and \
                self.display_data_hook is not None:

            self.display_data_hook.set_parent(parent)

        super(SingletonIPythonKernel, self).set_parent(ident, parent)

    def set_displaydatahook(self, display_data_hook):
        self.display_data_hook = display_data_hook

    def reset_parent(self):
        if self.display_data_hook is not None:
            self.display_data_hook.reset_parent()
