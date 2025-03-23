import sys
import os

def run(args : list):
    
    if not isinstance(args, list):
        exit("Give a list.")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    # Add parent directory to sys.path
    sys.path.insert(0, parent_dir)
    import manage

    os.chdir(script_dir)
    sys.argv = args
    manage.main()