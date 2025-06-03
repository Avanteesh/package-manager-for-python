import re
import sys
import shutil
import tarfile
import colorama as Col
import subprocess as subps
from time import sleep
from utilities.info import Config

def package_installation_loader(progress: list[bool], package_name: str):
    print(f"{Col.Fore.CYAN}looking for the package '{package_name}'...{Col.Fore.CYAN}")
    sleep(2)
    print(f"{Col.Fore.GREEN}Gathering binaries{Col.Fore.GREEN}")
    sleep(2)
    print(f"{Col.Fore.YELLOW}installing {package_name}...{Col.Fore.YELLOW}")
    while progress[0]:
        sleep(2)

def initializePackage(url: str, version: str):
    subps.run(["wget", f"{url}"],capture_output=True)
    if re.search(r"\.whl", url) is not None:
        subps.run(["unzip", f"{sys.argv[2]}*.whl"],capture_output=True)
        shutil.move(f"{sys.argv[2]}-{version}.dist-info", Config.DEPS_FOLDER.value)
        shutil.move(f"{sys.argv[2]}", Config.DEPS_FOLDER.value)
    elif re.search(r"\.tar.gz", url) is not None:
        with tarfile.open(f"{sys.argv[2]}-{version}.tar.gz", "r") as t1:
            t1.extractall(Config.DEPS_FOLDER.value)
    curr_folder = shutil.os.listdir(".")
    for files in curr_folder:
        if (re.search(r"\.whl", files) is not None) or (re.search(r"\.tar.gz", files) is not None):
            shutil.os.remove(files)

