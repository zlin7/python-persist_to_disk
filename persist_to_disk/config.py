import configparser
import os
from pathlib import Path

from . import _utils
from .myfilelock import FileLock

SETTING_PATH = os.path.join(Path.home(), '.cache', 'persist_to_disk')
_utils.make_dir_if_necessary(SETTING_PATH)
DEFAULT_PERSIST_PATH = os.path.join(SETTING_PATH, 'cache')
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

            # global, func, call
            global_config['global_settings']['lock_granularity'] = 'func'

            # List to add:
            # 1. Whether to automatically clear a folder if hashsize changes
        else:
            global_config.read(CONFIG_PATH)
        self.global_config = global_config
        # worksapce_config
        self.config = {'persist_path': None,
                       'project_path': os.path.normpath(os.getcwd())}
        self.set_persist_path(
                self.global_config['global_settings']['persist_path'])

        self._private_config = {'_persist_path': {}}
        for key in ['hashsize', 'lock_granularity']:
            self.config[key] = self.global_config['global_settings'][key]
        assert self.config['lock_granularity'] in {"call", "func", "global"}

    def generate_config(self):
        with open(CONFIG_PATH, 'w', encoding='utf-8') as fout:
            self.global_config.write(fout)
        print(f"Settings written to {CONFIG_PATH}")

    def set_project_path(self, path: str):
        self.config['project_path'] = os.path.normpath(os.path.abspath(path))
        return self.config['project_path']

    def set_persist_path(self, path):
        self.config['persist_path'] = os.path.normpath(os.path.abspath(path))
        return self.config['persist_path']

    def set_hashsize(self, hashsize=500):
        self.config['hashsize'] = hashsize
        return hashsize

    def set_alternative_readonly_persist_paths(self, paths):
        raise NotImplementedError()

    def get_alternative_roots(self):
        return None

    def _compute_and_save_actual_persist_path(self):
        persist_path = self.get_persist_path()
        project_path = self.get_project_path()

        if (persist_path, project_path) not in self._private_config['_persist_path']:
            pid = _read_project_pid(project_path)
            final_path = os.path.join(persist_path, f"{os.path.basename(project_path)}-{pid}")
            _record_project_persist_path(final_path, pid)
            _utils.make_dir_if_necessary(final_path)
            self._private_config['_persist_path'][(persist_path, project_path)] = final_path
        return self._private_config['_persist_path'][(persist_path, project_path)]

    def get_persist_path(self):
        return self.config['persist_path']

    def get_project_persist_path(self):
        return self._compute_and_save_actual_persist_path()

    def get_project_path(self):
        return self.config['project_path']

    def get_hashsize(self):
        return int(self.config['hashsize'])
