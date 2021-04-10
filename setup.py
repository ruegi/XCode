from cx_Freeze import setup, Executable

base = None    

executables = [Executable("XCode_process_mitliste.py", base=base)]

packages = ["idna", "PyQt5.QtWidgets", "PyQt5.QtCore", "PyQt5.QtGui", "math", "timeit", "datetime", "logger", "sys", "os", "shutil"]
options = {
    'build_exe': {    
        'packages':packages,
    },    
}

setup(
    name = "<any name>",
    options = options,
    version = "1.0",
    description = 'Konertiert Video *.ts Dateien aus dem Ordner C:\ts in Video *.mkv mit MPeg4 Format in den Ordner E:\Filme\schnitt',
    executables = executables
)
