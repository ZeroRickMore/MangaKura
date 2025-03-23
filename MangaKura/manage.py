#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from MangaKura import settings as GLOBAL_SETTINGS

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
    
    # When executing from mobile, I simply run this script with no args.
    # That being said, we consider the scenario where if len(sys.argv) == 1, we are on mobile, straight up.
    # So, we go into LAZY mode, which is a mode that skips heavy calculations like the manga stats, to be mobile-friendly.
        
    if len(sys.argv) >= 2:
        if sys.argv[1] == 'lazy':
            # Consume the argument and then run the program normally
            GLOBAL_SETTINGS.LAZY = True
            print("RUNNING AS LAZY")
            sys.argv.remove('lazy')

    execute_from_command_line(sys.argv)



if __name__ == '__main__':
    main()