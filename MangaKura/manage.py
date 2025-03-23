#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MangaKura.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # START OF EXTRA ARGS HANDLING ======================================================

    if 'lazy' in sys.argv:
        print("\n")
        # Consume the argument and then run the program normally
        sys.argv.remove('lazy')
        os.environ['LAZY'] = "1"
        print("\t] RUNNING AS LAZY")
        print("\n")

    if 'offline' in sys.argv:
        print("\n")
        # Consume the argument and then run the program normally
        sys.argv.remove('offline')
        os.environ['OFFLINE'] = "1"
        print("\t] RUNNING AS OFFLINE")
        print("\n")

     
    # END OF EXTRA ARGS HANDLING ======================================================

    execute_from_command_line(sys.argv)



if __name__ == '__main__':
    main()