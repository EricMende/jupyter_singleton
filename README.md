# jupyter-singleton

## Introduction

jupyter-singleton is a wrapper for the jupyter notebook that allows using output cells from outside of the `jupyter notebook` environment. Thus it enables you to use `ipywidgets` and *Grammar of Graphics* packages whilst programming in your favorite IDE.

## Usage

```
import ipywidgets as widgets

from IPython.display import display
from jupyter_singleton.launcher import launch


def test_fun(open_singleton):
    open_singleton()
    print('this will be shown in browser window')
    label = widgets.Label(value='this too')
    display(label)

    open_singleton()
    print('this will be shown in another browser window')


if __name__ == '__main__':
    launch(test_fun)

    # this will never be reached unless jupyter client gets killed

```

## Dependency

- `notebook` (version >= 5.7.8)

## Installation

```
$ pip install jupyter-singleton
```

## License

This software is licensed under the MIT license. See the [LICENSE](LICENSE) file
for details.
