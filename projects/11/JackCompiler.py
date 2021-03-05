from CompilationEngine import *
import os
import sys


def main():
    if len(sys.argv) != 2:
        print("Usage: JackAnalyzer.py fileName.jack/directoryName")
        sys.exit(1)

    in_put = sys.argv[1]

    # Creates a list with all the jack files and
    # saves the path where xml files are going to be created
    if os.path.isfile(in_put):
        jack_files = [in_put]
        in_path = os.path.abspath(in_put)
        in_path = in_path[:in_path.rfind('/')]
    elif os.path.isdir(in_put):
        jack_files = [file for file in os.listdir(in_put) if '.jack' in file]
        in_path = os.path.abspath(in_put)

    # Creates a directory for the xml files
    xml_path = os.path.join(in_path, 'xml')
    try:
        os.mkdir(xml_path)
    except FileExistsError:
        pass

    # Runs the Jack Analyzer for every jack file, and create each corresponding xml and vm file
    for jack_file in jack_files:
        xml_filepath = os.path.join(xml_path, jack_file.split('.')[0] + '.xml')
        vm_path = os.path.join(in_path, jack_file.split('.')[0] + '.vm')
        # Opens each out file and writes xml and vm code
        with open(os.path.join(in_path, jack_file), 'r') as in_file:
            xml_file = open(xml_filepath, 'w')
            CompilationEngine(in_file, xml_file, vm_path).run()
            xml_file.close()

main()
