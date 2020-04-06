import re

from setuptools import setup

# load version from module (without loading the whole module)
with open('chat.py') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cli-chat',
    version=version,
    description='CLI Chat',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Daniyar Kussainov',
    author_email='ohw0sseug@gmail.com',
    url="https://github.com/guesswh0/cli_chat",
    py_modules=['chat'],
    install_requires=[
        'click~=7.1.0'
    ],
    entry_points={
        'console_scripts':
            [
                'chat=chat:chat',
            ]
    },
    classifiers=[
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Operating System :: OS Independent',
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6'
)
