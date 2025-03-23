import manage
import sys
import os

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    sys.argv = ['./manage.py', 'lazy', 'runserver']
    manage.main()


if __name__ == '__main__':
    main()