class DisplayDataHook:
    """
    NOTE: this is a quick'n'dirty solution to be able to send the correct parent_header to the browser in the few
    circumstances I use. It is not tested for multi-threads and the use of 'update_display_data'
    This is related to the github-issue #113 of the ipykernel project. However I have to admit that I don't fully
    understand the topic discussed there.
    """

    parent_header = None

    def set_parent(self, parent):
        if parent is None or 'header' not in parent:
            self.parent_header = None
        else:
            self.parent_header = parent['header']

    def reset_parent(self):
        self.parent_header = None

    def __call__(self, msg):
        if msg is None:
            return None

        if 'msg_type' not in msg or msg['msg_type'] not in ['update_display_data', 'display_data']:
            return msg

        if self.parent_header is None:
            return None

        msg['parent_header'] = self.parent_header
        return msg
