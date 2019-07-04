# jupyter-singleton


## Introduction

jupyter-singleton is a wrapper for the jupyter notebook that allows using output cells from outside of the `jupyter notebook` environment. Thus it enables you to use `ipywidgets` and *Grammar of Graphics* packages whilst programming in your favorite IDE.


## Usage

### Example 1

You can use the jupyter-singleton `display` function similar to the IPython `display` function. However, here the result will be shown in a new browser window.

```
from ipywidgets import Label
from jupyter_singleton.direct import display

display(Label('I will be displayed in a browser window'))
display(Label('I will be displayed in another browser window'))
```

### Example 2

You can also use jupyter-singletons `open_singleton` function to activate a jupyter output-cell in a new browser window. Than you can use the traditional IPython `display` function to show your widgets, as well as ipywidgets `interact` function.

```
from IPython.display import display
from ipywidgets import interact, Label
from jupyter_singleton.direct import open_singleton


def f(x):
    return x


open_singleton()
interact(f, x=10)
display(Label('I will be displayed in the same browser window as the interact-slider'))

```


## Dependencies

- `ipykernel` (version >= 5.1.1)
- `IPython` (version >= 7.5.0)
- `jinja2` (version >= 2.10.1)
- `jupyter_client` (version >= 5.2.4)
- `jupyter_nbextensions_configurator` (version >= 0.4.1)
- `notebook` (version >= 5.7.8)
- `tornado` (version >= 6.0.2)


## Installation

```
$ pip install jupyter-singleton
```


## License

This software is licensed under the MIT license. See the [LICENSE](LICENSE) file
for details.
