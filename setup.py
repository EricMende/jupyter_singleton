from setuptools import setup

long_description=open('README.md').read()

setup(
    name='jupyter_singleton',
    version='0.0.1',
    packages=['jupyter_singleton',],
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
        'notebook >= 5.7.8',
    ],
    include_package_data=True
)
