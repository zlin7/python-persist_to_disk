import os
from pathlib import Path
from setuptools import setup, find_packages


def create_setting_folder():
    """Create the setting folder
    """
    SETTING_PATH = os.path.join(Path.home(), '.persist_to_disk')
    if not os.path.isdir(SETTING_PATH):
        os.makedirs(SETTING_PATH)


with open('README.md', encoding='utf-8') as readme_file:
    README = readme_file.read()

with open('HISTORY.md', encoding='utf-8') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='persist_to_disk',
    version='0.0.1',
    description='Persist expensive operations on disk.',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    packages=find_packages(),
    author='Zhen Lin',
    author_email='zhenlin4@illinois.edu',
    keywords=['Cache', 'Persist'],
    url='https://github.com/zlin7/python-persist_to_disk',
    # download_url='https://pypi.org/project/elastictools/'
)

install_requires = [
    'filelock==3.9.0',
    'six>=1.16'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
    create_setting_folder()
