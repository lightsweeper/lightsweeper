from __future__ import print_function

print("Welcome to the LightSweeper installer!")

import sys

def bail(mess):
    print("\n{:s}".format(mess))
    sys.exit()
    
if __name__ != "__main__":
    print("Oh no! Something went terribly wrong!")
    bail("Please run installer.py directly.")

if sys.hexversion < 0x030200a1:
    print("LightSweeper requires python 3.2 or higher but your current python version is:")
    print(sys.version)
    bail("Please upgrade your python interpreter and try again.")

import os
import shutil
import tempfile

from urllib.request import urlopen
from zipfile import ZipFile

def main():

    print("Checking for LightSweeper API... ", end="")
    try:
        import lightsweeper
    except:
        print("not installed.")
        print("The LightSweeper API is not installed.")
        if YESno("Would you like me to fetch it from the internet and install it?"):
            try:
                lsApiArchive = fetch_ls_api()
            except Exception as e:
                print("Failed to fetch archive.")
                bail("Please ensure you have an active internet connection and try again.")
            install_ls_api(lsApiArchive)
            lsApiArchive.close()
            restarter()
        else:
            bail("Please install the LightSweeper API then try again.")
    print("installed.")


    from lightsweeper import lsconfig

    sysPath = os.path.abspath("/LightSweeper")
    localPath = os.path.abspath(os.path.expanduser("~/.lightsweeper"))

    scopes = ["System-wide", "For the local user only"]
    installScope = lsconfig.userSelect(scopes, "\nHow would you like to install the LightSweeper environment?")

    if (installScope == scopes[0]):
        configDir = sysPath
        local=False
    else:
        configDir = localPath
        local=True

    basePath = os.path.expanduser("~") if local else sysPath

    gamesDir = chooseDir("Where would you like to store your games?", os.path.join(basePath, "lightsweeper-games" if local else "games"))

    if local:
        utilsDir = chooseDir("Where would you like to store the LightSweeper utilities?", os.path.join(basePath, "lightsweeper-utilities"))
    else:
        utilsDir = os.path.join(basePath, "util")

    examplesDir = os.path.join(os.path.join(basePath, ".lightsweeper") if local else basePath, "examples")

    check_dir(configDir, "configuration")
    check_dir(gamesDir, "games")
    check_dir(utilsDir, "utilities")
    check_dir(examplesDir, "examples")

    print("Copying some data... ", end="")

    try:
        shutil.copy2(sane_root("LightSweeper.py"), basePath)
        copy_directory(sane_root("games"), gamesDir)
        copy_directory(sane_root("util"), utilsDir)
        copy_directory(sane_root("examples"), examplesDir)
    except Exception as e:
        bail("Error copying data: {:s}".format(e))

    print("done.")

    config = os.path.join(configDir, "lightsweeper.conf")
    print("Generating lightsweeper.conf... ", end="")
    if os.path.exists(config):
        shutil.copy2(config, "{:s}.bak".format(config))

    f = open(config, "w")
    f.write("GAMESDIR = {:s}\n".format(gamesDir))
    
    f.close()
    print("okay.")
    
    print("Okay have fun!")

def check_dir(path, name):
    from lightsweeper import lsconfig
    if not os.path.exists(path):
        print("Creating {:s} directory... ".format(name), end="")
        try:
            os.mkdir(path)
        except PermissionError:
            print("failed.")
            print("Could not create folder: {:s}".format(path))
            bail("Please check your permissions and try again.")
        print(path)
    else:
        if os.path.isdir(path):
            if not lsconfig.yesNO("{:s} already exists, would you like to install anyway? (This may clobber data)".format(path)):
                bail("Please move the folder at {:s} and try again.".format(path))
        else:
            print("{:s} already exists.".format(path))
            bail("Please move or rename the file at {:s} and try again.".format(path))

def copy_directory(sourceDir, destDir):
    for fileName in os.listdir(sourceDir):
        source = os.path.join(sourceDir, fileName)
        dest = os.path.join(destDir, fileName)
        if os.path.isdir(source):
          #  copy_directory(source, dest)
            try:
                shutil.copytree(source, dest, False, None)
            except FileExistsError:
                copy_directory(source, dest)
        else:
            shutil.copy2(source, dest)

def sane_root(path):
    return(os.path.abspath(os.path.join(sys.path[0], path)))

def fetch_ls_api():
    url = "https://github.com/lightsweeper/lightsweeper-api/archive/master.zip"
    print("Fetching source from {:s}...".format(url))
    file_name = url.split('/')[-1]
    u = urlopen(url)
    f = tempfile.TemporaryFile()
    meta = u.info()
    file_size = int(meta.get("Content-Length"))

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = "{:d} bytes [{:.2f}%]".format(file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print(status, end="")
    print("")

    return(f)

def install_ls_api(archiveFile):
    backArgs = sys.argv[:]
    backDir = os.getcwd()
    with tempfile.TemporaryDirectory() as td:
        archive = ZipFile(archiveFile)
        archive.extractall(td)
        setupPath = os.path.join(td, "lightsweeper-api-master")
        os.chdir(setupPath)
        setupScript = open("setup.py").read()
        lsapiSetup = compile(setupScript, "setup.py", "exec")
        sys.argv = ["setup.py", "install"]
        exec(lsapiSetup)
    os.chdir(backDir)
    sys.argv = backArgs

def restarter():
        args = sys.argv[:]
        print("\nRestarting: {:s}".format(" ".join(args)))
        args.insert(0, sys.executable)
        if sys.platform == "win32":
            args = ["\"{:s}\"".format(arg) for arg in args]
        os.execv(sys.executable, args)

def YESno(message, default="Y"):
  yesses = ("yes", "Yes", "YES", "y", "Y")
  nos = ("no", "No", "NO", "n", "N")
  if default in yesses:
    answer = input("{:s} [Y/n]: ".format(message))
  elif default in nos:
    answer = input("{:s} [y/N]: ".format(message))
  else:
      raise ValueError("Default must be some form of yes or no")
  if answer is "":
      answer = default
  if answer in yesses:
      return True
  elif answer in nos:
      return False
  else:
      print("Please answer Yes or No.")
      return YESno(message)

def chooseDir(message, default):
    fileName = input("{:s} [{:s}] ".format(message, default))
    if fileName == "":
        fileName = default
    return(fileName)

main()
