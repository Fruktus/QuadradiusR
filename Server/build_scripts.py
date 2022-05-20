import os

from PyInstaller import __main__ as pyinstaller_main


def pyinstaller():
    cwd = os.getcwd()
    build_dir = os.path.join(cwd, 'build/pyinstaller')
    work_dir = os.path.join(build_dir, 'work')

    args = [
        '--noconfirm',
        '--onefile',
        '--name', 'quadradiusr_server',
        '--hidden-import', 'aiosqlite',
        '--collect-submodules', 'quadradiusr_server.rest',
        '--specpath', build_dir,
        '--workpath', work_dir,
        'src/quadradiusr_server/__main__.py'
    ]

    pyinstaller_main.run(args)
