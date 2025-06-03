from enum import Enum

"""
following library contains grammar or command arguments for 
PM
"""

class Config(Enum):
    INIT_PY = """def main():\n\tprint("hello world!")\n\nif __name__ == "__main__":\n\tmain()\n"""
    DEPS_FOLDER = "pylibs"   # folder where all dependencies will be stored!  
    DEPS_FILE = "package.json"   # name of the file which stores information about the python project!
    
class Commands(Enum):
    INIT = "init"
    INSTALL = "install"
    ADD = "add"
    REMOVE = "remove"
    LIST = "list"
    RUN = "run"
    HELP = "--help"
    CLEAN = "clean"

