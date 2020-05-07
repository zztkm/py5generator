import cmd
import argparse
import glob
from pathlib import Path

import py5_tools


parser = argparse.ArgumentParser(description="py5 command tool",
                                 epilog="this is the epilog")


LIBRARY_TEMPLATE = """[{id}] Name: {name}
Author: {authors}
{sentence}
{categories}
{paragraph}"""


class Py5Cmd(cmd.Cmd):

    def __init__(self):
        super().__init__()
        self._libraries = py5_tools.ProcessingLibraryInfo()

    prompt = 'py5: '
    intro = "Welcome to the py5 command tool."

    def _print_library_info(self, info):
        info = info.T.to_dict()[info.index[0]]

        return LIBRARY_TEMPLATE.format(**info)

    def do_list_categories(self, line):
        for c in self._libraries.categories:
            print(c)

    def do_show_category(self, line):
        category_libraries = self._libraries.get_library_info(category=line).sort_values('id')

        for _, info in category_libraries.iterrows():
            print(LIBRARY_TEMPLATE.format(**info).strip() + '\n')

    def complete_show_category(self, text, line, begidx, endidx):
        if not text:
            completions = self._libraries.categories
        else:
            completions = [c for c in self._libraries.categories if c.startswith(text)]

        return completions

    def do_run_sketch(self, line):
        if line:
            try:
                py5_tools.run.run_sketch(line)
            except Exception as e:
                print(e)

    def complete_run_sketch(self, text, line, begidx, endidx):
        path = line[10:].strip()
        completions = []
        for p in glob.glob(path + '*'):
            completions.append(p[(len(path) - len(text)):] + ('/' if Path(p).is_dir() else ''))
        return completions

    def do_get_library(self, line):
        try:
            self._libraries.download_zip('jars', library_name=line)
        except Exception as e:
            print(e)

    def complete_get_library(self, text, line, begidx, endidx):
        if not text:
            completions = self._libraries.names
        else:
            completions = [n for n in self._libraries.names if n.startswith(text)]

        return completions

    def do_EOF(self, line):
        return True


def main():
    # args = parser.parse_args()
    py5cmd = Py5Cmd()
    py5cmd.cmdloop()


if __name__ == '__main__':
    main()