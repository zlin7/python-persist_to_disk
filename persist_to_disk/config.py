import os
from pathlib import Path
import configparser

from .myfilelock import FileLock
from . import _utils

SETTING_PATH = os.path.join(Path.home(), '.persist_to_disk')
_utils.make_dir_if_necessary(SETTING_PATH)
DEFAULT_PERSIST_PATH = os.path.join(SETTING_PATH, 'cache')
# DEFAULT_PERSIST_PATH = 'C:/Users/zhen7/Desktop/gitRes/persist_to_disk/.persist_to_disk'
CONFIG_PATH = os.path.join(SETTING_PATH, 'config.ini')


def _read_project_pid(project_path, sep='||'):
    assert sep not in project_path
    project_path = os.path.normpath(project_path)
    meta_file = os.path.join(SETTING_PATH, 'project_to_pids.txt')
    return _utils.retrieve_id(meta_file, project_path, sep=sep)


def _record_project_persist_path(persist_path, pid, sep='||'):
    assert sep not in persist_path
    meta_file = os.path.join(SETTING_PATH, 'pid_to_persist_dirs.txt')
    with FileLock(meta_file):
        curr_dict, lines = {}, []
        if os.path.isfile(meta_file):
            with open(meta_file, 'r', encoding='utf-8') as fin:
                lines = fin.readlines()
            for line in lines:
                line = line.strip().split(sep)
                curr_dict[line[0]] = set(line[1:])
        if pid not in curr_dict:
            curr_dict[pid] = set([persist_path])
            with open(meta_file, 'a', encoding='utf-8') as fout:
                fout.write(
                    f"{pid}{sep}{sep.join(list(curr_dict[pid]))}\n")
        elif persist_path not in curr_dict[pid]:
            for i, line in enumerate(lines):
                if line.strip().split(sep)[0] == pid:
                    lines[i] = f"{line.strip()}{sep}{persist_path}"
                with open(meta_file, 'w', encoding='utf-8') as fout:
                    fout.writelines(lines)


class Config(dict):
    """Global config for this project.
    """

    def __init__(self) -> None:
        global_config = configparser.ConfigParser()
        if not os.path.isfile(CONFIG_PATH):
            global_config.add_section('global_settings')
            global_config['global_settings']['persist_path'] = DEFAULT_PERSIST_PATH
            global_config['global_settings']['hashsize'] = '500'

            # List to add:
            # 1. Whether to automatically clear a folder if hashsize changes
        else:
            global_config.read(CONFIG_PATH)
        self.global_config = global_config
        # worksapce_config
        self.config = {'persist_path': None,
                       'project_path': os.path.normpath(os.getcwd())}
        for key in ['hashsize']:
            self.config[key] = self.global_config['global_settings'][key]

    def generate_config(self):
        with open(CONFIG_PATH, 'w', encoding='utf-8') as fout:
            self.global_config.write(fout)
        print(f"Settings written to {CONFIG_PATH}")

    def set_persist_path(self, path, project_name=None):
        path = os.path.normpath(path)
        _utils.make_dir_if_necessary(path)
        if project_name is None:
            project_path = self.config['project_path']
            pid = _read_project_pid(project_path)
            persist_path = os.path.join(
                path, f"{os.path.basename(project_path)}-{pid}")
            _record_project_persist_path(persist_path, pid)
        else:
            persist_path = os.path.join(path, project_name)
        _utils.make_dir_if_necessary(persist_path)
        self.config['persist_path'] = persist_path
        # self.config['project_name'] = project_name or pid
        return persist_path

    def set_hashsize(self, hashsize=500):
        self.config['hashsize'] = hashsize
        return hashsize

    def set_alternative_readonly_persist_paths(self, paths):
        raise NotImplementedError()

    def get_alternative_roots(self):
        return None

    def get_persist_path(self):
        persist_path = self.config.get('persist_path', None)
        if persist_path is None:
            persist_path = self.set_persist_path(
                self.global_config['global_settings']['persist_path'])
        return persist_path

    def get_project_path(self):
        return self.config['project_path']

    def get_hashsize(self):
        return int(self.config['hashsize'])
