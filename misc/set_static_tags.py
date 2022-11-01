
import argparse

from pathlib import Path

STATIC_FILE_TYPES = ('css', 'js', 'images')


def _add_static(line, pattern):
    pattern_index = line.index(pattern)
    string_list = list(line)
    string_list[pattern_index:pattern_index] = 'static/'
    return ''.join(string_list)

def add_static_into_url(folders):
    for filepath in Path(folders).iterdir():
        if str(filepath).endswith('.html'):
            with open(filepath, 'r', encoding='UTF-8') as file:
                lines = file.readlines()

            newlines = []
            for line in lines:
                newline = line
                for static_file_type in STATIC_FILE_TYPES:
                    if static_file_type in newline:
                        newline = _add_static(newline, static_file_type)
                newlines.append(newline)

            newlines = ''.join(newlines)

            with open(filepath, 'w', encoding='UTF-8') as file:
                file.write(newlines)
    print('Successfully add "static/" into all static file paths.')


def replace_static_tags(folders):
    for filepath in Path(folders).iterdir():
        if str(filepath).endswith('.html'):
            with open(filepath, 'r', encoding='UTF-8') as file:
                filedata = file.read()
                has_static = 'static' in filedata
                lines = filedata.split('\n')

            if has_static and '{% load static %}' not in lines:
                lines.insert(0, '{% load static %}')

            newlines = []
            for line in lines:
                newline = line
                if 'app/static/' in line:
                    line_splited_by_static = line.split('app/static/')

                    # Add ' %}" to the part after 'static/'.
                    line_splited_by_static[1] = '\' %}"'.join(line_splited_by_static[1].split('"', 1))

                    # Add {% static ' to the replace the 'static/'.
                    newline = '{% static \''.join(line_splited_by_static)

                    # Then the newline will be like this:
                    # ~~~~somethings src="{% static 'path_to_static_file' %}" somethings~~~~
                newlines.append(newline)

            newlines = '\n'.join(newlines)

            with open(filepath, 'w', encoding='UTF-8') as file:
                file.write(newlines)

    print('Successfully replace all static file path to the "static tags".')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set static tags for all static files used in these .html files.')

    parser.add_argument('paths', metavar='paths', type=str, nargs='+',
                        help='path list')

    args = parser.parse_args()
    for path in args.paths:
        # add_static_into_url(path)
        replace_static_tags(path)
