from setuptools import setup

long_description = open('README.md').read()

setup(
    name='jupyter_singleton',
    version='0.1.0',
    packages=[
        'jupyter_singleton',
        'jupyter_singleton/config',
        'jupyter_singleton/direct',
    ],
    author='Eric Mende',
    author_email='em@bc-potsdam.de',
    url='https://github.com/EricMende/jupyter_singleton',
    license='MIT License',
    python_requires=">=3.6",
    description='jupyter notebook wrapper for making output cells available outside of notebook',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    install_requires=[
        'ipykernel >= 5.1.1',
        'IPython >= 7.5.0',
        'jinja2 >= 2.10.1',
        'jupyter_client >= 5.2.4',
        'jupyter_nbextensions_configurator >= 0.4.1',
        'notebook >= 5.7.8',
        'tornado >= 6.0.2',
    ],
    include_package_data=True
)
