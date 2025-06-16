from catena4j.bootstrap import register_entry_point
from catena4j.util import find_path

def main():
    print('TODO')
    print('Build the toolkit')
    print('Generate the startup script')
    print('Add executable to PATH')

register_entry_point(main)

if __name__ == '__main__':
    from catena4j.bootstrap import system
    system.start
