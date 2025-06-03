import sys
import re
import ast
import shutil
import colorama as Col
import subprocess as subps
from requests import get
from threading import Thread
from json import dumps, loads
from os import path, mkdir, getcwd, _exit
from time import sleep
from utilities.info import Config, Commands
from utilities.helpers import package_installation_loader, initializePackage
from utilities.lint_module import analyzePySourceFiles

class PyProject(object):
    """
    commands for package manager!
    
    init <project-name> initializes a new project, and creates a package.json file!
    install - installs all dependencies provided in the package.json file!
    add <python-package-name> - installs a specific python package!
    remove <python-package-name> - removes a specific python package!
    clean - removes all the dependencies including the deps folder for deployment, the dependency data will be stored in the package.json file
    run <main-project-file> without the extension. - Runs a python script which has the prefix name as the argument! 
    """
    def __init__(self, project_name: str=path.split(getcwd())[-1]):
        self.project_name = project_name
        self.dependency = {
          "name": self.project_name,
          "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
          "dependencies": []
        }

    def initializeProject(self):
        if len(sys.argv) <= 2:
            print(f"{Col.Fore.RED}ERRO:{Col.Fore.WHITE} project name not provided!")
            _exit(1)
        self.project_name = sys.argv[2]
        if path.exists(self.project_name) == True:
            print(f"{Col.Fore.RED}ERROR:{Col.Fore.WHITE} The project already exist.")
            _exit(1)
        mkdir(self.project_name)
        py_file = path.join(self.project_name, "main.py")
        if path.exists(py_file) == False:
            with open(py_file, "w") as f1:
                f1.write(Config.INIT_PY.value)
        with open(path.join(self.project_name, Config.DEPS_FILE.value), "w") as f1:
            package_json = dumps(self.dependency, indent=2)
            f1.write(f"{package_json}\n")
        print(f"{Col.Fore.CYAN}project {Col.Fore.GREEN}'{self.project_name}'{Col.Fore.CYAN} initialized at {path.join(getcwd(), self.project_name)}{Col.Fore.WHITE}")
        return

    def removeDependency(self):
        if len(sys.argv) <= 2:
            print(f"{Col.Fore.RED}ERROR:{Col.Fore.RED} Package not specified, must be {Col.Fore.CYAN} `pym remove package_name`{Col.Fore.WHITE}")
            return
        if not path.exists(Config.DEPS_FILE.value):
            print(f"{Col.Fore.RED}ERROR:{Col.Fore.YELLOW} `package.json` file not found{Col.Fore.WHITE}")
            return
        with open(Config.DEPS_FILE.value, "r") as f1:
            self.dependency = loads(f1.read())
        try:
            for folders in shutil.os.listdir(Config.DEPS_FOLDER.value):
                if re.match(sys.argv[2], folders) is not None:
                    shutil.rmtree(path.join(Config.DEPS_FOLDER.value, folders))
            modules = list(filter(lambda item: re.match(sys.argv[2], item) != None, self.dependency["dependencies"]))
            for item in modules:
                self.dependency["dependencies"].remove(item)
            sleep(1)
            with open(Config.DEPS_FILE.value, "w") as f2:
                f2.write(dumps(self.dependency, indent=2))
            print(f"{Col.Fore.GREEN}package '{sys.argv[2]}' removed successfully!{Col.Fore.GREEN}")
        except ValueError:
            print(f"{Col.Fore.RED}ERROR:{Col.Fore.BLUE}No package '{sys.argv[2]}' exists!")
        except FileNotFoundError:
            print(f"{Col.Fore.RED}ERROR:{Col.Fore.WHILE} libs folder is missing!")

    def addDependency(self, install_recursively: bool=True):
        downloading_progress = [True]
        if len(sys.argv) == 2:
            print(f"{Col.Fore.RED}ERROR:{Col.Fore.YELLOW} Package not specified, must be {Col.Fore.CYAN} `pym add package_name`{Col.Fore.WHITE}")
            _exit(1)
        if not path.exists(Config.DEPS_FOLDER.value):
            mkdir(Config.DEPS_FOLDER.value)
        def installDependency():
            dependency, version_no = sys.argv[2], None
            if path.exists(path.join(Config.DEPS_FOLDER.value, dependency)):
                downloading_progress[0] = False
                print(f"{Col.Fore.BLUE}'{dependency}' package already exists!")
                return
            repository_link = f"https://pypi.org/pypi/{dependency}/json"
            get_repo = get(repository_link).json()
            if "message" in get_repo:
                if get_repo["message"] == "Not Found":
                    print(f"{Col.Fore.RED}Package {dependency} not found{Col.Fore.WHITE}")
                    return 
            package_repos, target_repo_version = get_repo["releases"], None
            if len(sys.argv) == 4:
                if re.match(r"--version=*", sys.argv[3]) is not None:
                    print(f"{Col.Fore.YELLOW}fourth arg should be '--version=x.x.x'{Col.Fore.WHITE}")
                    return
                [_, version] = sys.argv[3].split("=")
                if re.match(r"\d+.\d+.\d+", version) is not None:
                    print(f"{Col.Fore.RED}ERROR:{Col.Fore.CYAN} invalid version no.{Col.Fore.WHITE}")
                version_no = version
                for keys in package_repos.keys():
                    if keys == version:
                        target_repo_version = package_repos[keys]
                        break
                if target_repo_version is None:
                    print(f"{Col.Fore.RED}ERROR:{Col.Fore.CYAN} package '{dependency}' of version - {version} not found!")
                    return
            else:
                version_no = list(package_repos.keys())[-2]
                target_repo_version = package_repos[version_no]
            initializePackage(target_repo_version[1]["url"], version_no)
            downloading_progress[0] = False
            print(f"{Col.Fore.BLUE}installation success!{Col.Fore.WHITE}")
            if install_recursively:
                self.dependency["dependencies"].append(f"{dependency}-{version_no}")
                with open(Config.DEPS_FILE.value, "w") as f2:
                    f2.write(dumps(self.dependency, indent=2))
            return
        if not path.exists(Config.DEPS_FILE.value):
            print(f"{Col.Fore.RED}ERROR: {Col.Fore.YELLOW}'package.json' file not found{Col.Fore.WHITE}")
            print(f"{Col.Fore.GREEN}Solution: {Col.Fore.CYAN}initialize the project with init {'{project-name}'}{Col.Fore.WHITE}")
            return
        thread_1 = Thread(target=installDependency, args=())
        thread_2 = Thread(target=package_installation_loader, args=(downloading_progress, sys.argv[2]))
        thread_2.start()
        thread_1.start()
        thread_1.join()
        thread_2.join()
        return

    def runScript(self):
        if not path.exists(Config.DEPS_FILE.value):
            print("{Col.Fore.RED}ERROR:{Col.Fore.WHITE}project not initialized!")
            _exit(1)
        if len(sys.argv) == 2 or sys.argv[2] == "--help":
            print(f"Run the python project with the following command {Col.Fore.GREEN}`pyyum run <filename>`{Col.Fore.WHITE} without providing file extension.")
            _exit(0)
        if not path.exists(f"{sys.argv[2]}.py"):
            print(f"The '{sys.argv[2]}.py' file not found!")
            _exit(1)
        if len(sys.argv) == 4:
            if sys.argv[3] == "--no-warning":
                analyzePySourceFiles(ignore_warning=True)
        else:
            analyzePySourceFiles()
        if sys.platform == "win32":
            subps.run(['python', f'{sys.argv[2]}.py'])
            return
        subps.run(["python3", f"{sys.argv[2]}.py"])
        
    def showDependencies(self):
        print(f"{Col.Fore.GREEN}installed dependencies!{Col.Fore.WHITE}\n")
        with open(Config.DEPS_FILE.value, "r") as f1:
            self.dependency = loads(f1.read())
        for dep in self.dependency["dependencies"]:
            print(f"{Col.Fore.CYAN}{dep}{Col.Fore.WHITE}")
       
    def installFromPackageJSON(self):
        if not path.exists(Config.DEPS_FILE.value):
            print(f"{Col.Fore.RED}ERROR:{Col.Fore.RED} package.json file not found!")
            _exit(1)
        with open(Config.DEPS_FILE.value, "r") as f1:
            self.dependency = loads(f1.read())
        if len(self.dependency["dependencies"]) == []:
            _exit(1)
        sys.argv[1] = "add"
        sys.argv.append("")
        for deps in self.dependency["dependencies"]:
            pattern = re.match(r"\w+-\d+.\d+.\d+", deps)
            if pattern is not None:
                if pattern.span()[-1] == len(deps):
                    lib, version = deps.split("-")
                    sys.argv[2] = lib
                    sys.argv.append(f"--version={version}")
            else:
                sys.argv[2] = deps    
            self.addDependency(install_recursively=False)
        return

    def cleanDependencies(self):
        shutil.rmtree(Config.DEPS_FOLDER.value)
        print(f"{Col.Fore.GREEN}All Dependencies Cleaned successfully!{Col.Fore.WHITE}")
        return 

def main():
    if len(sys.argv) == 1:
        print("mypackage manager is a special utility that allows you to install packages!")
        return
    project = PyProject()
    match sys.argv[1]:
        case Commands.INIT.value:
            project.initializeProject()
        case Commands.ADD.value:
            project.addDependency()
        case Commands.REMOVE.value:
            project.removeDependency()
        case Commands.RUN.value:
            project.runScript()
        case Commands.LIST.value:
            project.showDependencies()
        case Commands.INSTALL.value:
            project.installFromPackageJSON()
        case Commands.CLEAN.value:
            project.cleanDependencies()
        case Commands.HELP.value:
            print(PyProject.__doc__)
        case _:
            print(f"{Col.Fore.RED}ERROR:{Col.Fore.CYAN}no command '{sys.argv[1]}' found!{Col.Fore.WHITE}")

if __name__ == "__main__":
    main()


