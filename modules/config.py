# coding: utf-8
import sys
from yaml import load, safe_dump


class Config:
    def __init__(self):
        self.configuration_items = {}
        self.reload()

    def __getitem__(self, key):
        return self.configuration_items[key]

    def __setitem__(self, key, value):
        self.configuration_items[key] = value

    def __contains__(self, key):
        if key in self.configuration_items:
            return True
        else:
            return False

    def reload(self):
        try:
            if len(sys.argv) >= 1:
                with open(sys.argv[1]) as item_file:
                    self.configuration_items.update(load(item_file))
            else:
                print('Usage: main.py item_filepath.yml')
                exit(1)
        except IOError:
            with open('config.yml') as item_file:
                self.configuration_items = load(item_file)

    def write(self):
        with open(sys.argv[1], 'w') as outfile:
            safe_dump(self.configuration_items, outfile, default_flow_style=False)

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        self[key] = default
        return default


class MissingConfigurationItem(Exception):
    def __init__(self, key=''):
        # Call the base class constructor with the parameters it needs
        super().__init__(f'Missing configuration item: {key}')


config = Config()
