import run_with_args

def main():
    run_with_args.run(args=['../manage.py', 'runserver', 'offline'])


if __name__ == '__main__':
    main()