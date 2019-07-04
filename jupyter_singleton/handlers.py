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
        cells = [{  # TODO this can break easily in new jupyter versions, the cell should be added via jupyter functions
            "cell_type": "code",
            "execution_count": 1,
            "metadata": {},
            "outputs": [
                {
                    "data": {
                        "image/jpeg": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAIBAQEBAQIBAQECAgICAgQDAgICAgUEBAMEBgUGBgYFBgYGBwkIBgcJBwYGCAsICQoKCgoKBggLDAsKDAkKCgr/2wBDAQICAgICAgUDAwUKBwYHCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgr/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD+f+iiigD/2Q==\n",
                        "text/plain": [
                            "<IPython.core.display.Image object>"
                        ]
                    },
                    "execution_count": 1,
                    "metadata": {},
                    "output_type": "execute_result"
                }
            ],
            "source": [
                "# this is a reload check -> a pixel should be reloaded in output area"
            ]
        }]

        model['content']['metadata']['kernelspec'] = kernelspec
        model['content']['cells'] = cells
        self.contents_manager.save(model, model['name'])

# -----------------------------------------------------------------------------
# URL to handler mappings
# -----------------------------------------------------------------------------


default_handlers = [
    (r"/singletonnotebooks%s" % path_regex, SingletonNotebookHandler),
    (r"/startkernel%s" % path_regex, StartKernelHandler),
]
