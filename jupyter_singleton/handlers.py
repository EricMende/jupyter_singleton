import jinja2
import os
import site

from tornado import web
from typing import Optional, Awaitable
from notebook.base.handlers import (
    IPythonHandler, path_regex,
)

HTTPError = web.HTTPError


class SingletonNotebookHandler(IPythonHandler):

    TEMPLATE_FILE = "wrapper.html"
    SEARCH_PATH = os.path.join(site.getsitepackages()[0], 'jupyter_singleton')  # TODO could it happen that there are more than one site-package here, how do I select the right ones -> handle list

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    @web.authenticated
    def get(self, path):
        path = path.strip('/')

        template_loader = jinja2.FileSystemLoader(searchpath=self.SEARCH_PATH)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template(self.TEMPLATE_FILE)
        output_text = template.render(path=path)
        self.write(output_text)


class StartKernelHandler(IPythonHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    @web.authenticated
    def get(self, path):

        # start the kernel
        self.kernel_manager.start_kernel()

        # create a notebook that is bound to the kernel
        info = self.contents_manager.new_untitled(type='notebook', ext='ipynb')
        model = self.contents_manager.get(info['name'])
        kernelspec = {
            "display_name": "singletonkernel",
            "language": "python",
            "name": "singleton_kernel"
        }
        model['content']['metadata']['kernelspec'] = kernelspec
        self.contents_manager.save(model, model['name'])

# -----------------------------------------------------------------------------
# URL to handler mappings
# -----------------------------------------------------------------------------


default_handlers = [
    (r"/singletonnotebooks%s" % path_regex, SingletonNotebookHandler),
    (r"/startkernel%s" % path_regex, StartKernelHandler),
]
