try:
    from os import scandir
except ImportError:
    from scandir import scandir  # use scandir PyPI module on Python < 3.5

def scantree(path):
    """Recursively yield DirEntry objects for given directory."""
    for entry in scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)  # see below for Python 2.x
        else:
            yield entry


def test_scantree():
    import sys
    for entry in scantree(sys.argv[1] if len(sys.argv) > 1 else '.'):
        print(entry.path)

if __name__ == '__main__':
    Y = 1
    N = 0
    Choose_Item =eval(input("Are you sure to delete these files[Y/N]:"))
