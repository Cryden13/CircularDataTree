try:
    from .gui import GUI
except ImportError:
    from pathlib import Path
    from subprocess import run
    pth = Path(__file__).parent
    run(['py', '-m', pth.name], cwd=pth.parent)
    raise SystemExit


def main():
    GUI().mainloop()


if __name__ == '__main__':
    main()
