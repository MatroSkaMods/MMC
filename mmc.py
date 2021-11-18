
from typing import Set
from zipfile import ZipFile
from subprocess import Popen
from colorama import init, Fore, Back, Style
import os, shutil, glob
init(autoreset=True)

logo = ('''
   _______ _______ _______  ______  _____  _______ _     _ _______  
   |  |  | |_____|    |    |_____/ |     | |______ |____/  |_____| Matroska Mod Compiler
   |  |  | |     |    |    |    \_ |_____| ______| |    \_ |     | [Version 0.2]
   _______  _____  ______    _______  _____  _______  _____  _____        _______  ______
   |  |  | |     | |     \   |       |     | |  |  | |_____]   |   |      |______ |_____/
   |  |  | |_____| |_____/   |_____  |_____| |  |  | |       __|__ |_____ |______ |    \_
''')

os.system('title MMC [Version 0.2]')

def cls():
    os.system('cls')

def line():
    print("  ","═"*86)

class Settings():
    """General hard-coded settings"""
    debug = False
    ignorelist = [
        '\\setuptools\\',
        '\\pip\\', 
        'easy_install.py',
        '_virtualenv.py',
        '\\pkg_resources\\',
        '\\wheel\\',
        'activate_this.py',
        '\\_distutils_hack\\'
        ]
    
    spacer = "   "

    modpath = "C:\\Users\\{}\\Documents\\Electronic Arts\\The Sims 4\\Mods\\".format(
        os.getlogin()
    )

    sims4_patches = {
        'import enum': 'import enum_lib as enum',
        'from enum import': 'from enum_lib import'
    }

templates = {
    'hello_world': """from sims4.commands import Command, CommandType, CheatOutput

# Adds a new cheat can be called with "hello".

@Command('hello', command_type=CommandType.Live)
def sayhello(_connection=None):
    output = CheatOutput(_connection)
    output('Hello, world!')
"""}


def UpdateFileLists(mod_name):
    """Update the lists of files recursively."""
    recusive_files = {}
    
    pycfiles = [os.path.join(dp, f) for dp, 
        dn, 
        filenames in os.walk("./mods/{}".format(mod_name)) for f in filenames if os.path.splitext(f)[1] == '.pyc']
    
    pyfiles = [os.path.join(dp, f) for dp,
        dn,
        filenames in os.walk("./mods/{}".format(mod_name)) for f in filenames if os.path.splitext(f)[1] == '.py'] 

    tsfiles = [os.path.join(dp, f) for dp,
        dn,
        filenames in os.walk("./mods/{}".format(mod_name)) for f in filenames if os.path.splitext(f)[1] == '.ts4script'] 
    
    recusive_files['py'] = pyfiles
    recusive_files['pyc'] = pycfiles
    recusive_files['ts4'] = tsfiles
    
    return recusive_files

def clean(mod_name):
    """Clean all the compiled files."""
    dirty_files = UpdateFileLists(mod_name)
    try:
        for x in dirty_files['pyc']:
            os.remove(x)
        #for x in dirty_files['ts4']:
        #    os.remove(x)
    except Exception as e:
        print(e)

def Compile_Mod(mod_name, debug):
    """Compile a mod."""
    mod_name = mod_name.split("\\")[-1].replace(".modname","")
    
    print(Settings.spacer+"* Cleaning '{}'".format(mod_name))
    clean(mod_name)

    print(Settings.spacer+"* Attempting to Compile '{}'".format(mod_name))
    try:
        _files = UpdateFileLists(mod_name)
        pyfiles = _files['py']
        oldpyfiles = []
    except Exception as e:
        print(Settings.spacer+"* Failed to Compile: {}".format(e))
    for xz in pyfiles:
        #print(Settings.spacer+"* Py File {}".format(xz))
        #! Patcher
        for ign in Settings.ignorelist:
            if ign in xz:
                #print(Settings.spacer+"* Igoring: {}".format(ign))
                ignore = True
                break
            else:
                ignore = False

        if ignore == False:
            try:
                with open(xz, 'r') as pyfile:
                    filecontents = pyfile.read()
                    for patch in Settings.sims4_patches.keys():
                        if patch in filecontents:
                            print(Fore.BLUE+ Settings.spacer + "--> Patching: {}".format(xz.replace("\\","/")))
                            filecontents = filecontents.replace(patch,Settings.sims4_patches[patch])
                            oldpyfiles.append(xz)
                with open(xz, 'w') as pyfile:
                    pyfile.write(filecontents)
            except Exception as e:
                print(Fore.YELLOW+ Settings.spacer + "Patching Error: {}".format(e))
                
            #! Compiler
            try:
                os.system("python.exe -m py_compile {}".format(xz))
                print(Fore.LIGHTBLUE_EX+ Settings.spacer + "--> Compiled: {}".format(xz.replace("\\","/")))
            except:
                print(Fore.LIGHTRED_EX+ Settings.spacer + "--> Error compiling: {}".format(xz))

    pycfiles = UpdateFileLists(mod_name)['pyc']
    pyfiles = UpdateFileLists(mod_name)['py']
    
    for xz in pycfiles:
        backonefolder = xz.replace("\\__pycache__\\","\\").replace("cpython-37.","")
        shutil.move(src="{}".format(xz), dst="{}".format(backonefolder))
    
    pycfiles = UpdateFileLists(mod_name)['pyc']

    compiled_mod_name = "./mods/{}/{}.ts4script".format(mod_name,mod_name)
    filestocompile = glob.glob("./mods/{}/*.*".format(mod_name))
    
    #print(Fore.GREEN + Settings.spacer + "* {} | {}".format(compiled_mod_name,filestocompile))
    print(Fore.GREEN + Settings.spacer + "* Building Mod Archive...")

    with ZipFile(compiled_mod_name, 'w') as zip:
        for y in pycfiles:
            for ign in Settings.ignorelist:
                if ign in y:
                    ignore = True
                    break
                else:
                    ignore = False
            if ignore == False:
                targ_buffer = y.split("\\",3)
                targ_buffer = targ_buffer[-1]
                name_in_archive = y.split("\\")[-1]
                zip.write(
                    y, arcname=targ_buffer
                )
                os.remove(y)
        
        if Settings.debug:
            for z in pyfiles:
                for ign in Settings.ignorelist:
                    if ign in z:
                        ignore = True
                        break
                    else:
                        ignore = False
                if ignore == False:
                    targ_buffer = z.split("\\",3)
                    targ_buffer = targ_buffer[-1]
                    name_in_archive = z.split("\\")[-1]
                    zip.write(
                        z, arcname=targ_buffer
                    )
        
    
    print(Fore.GREEN+ Settings.spacer + "* Rolling back patches...")
    
    for xz in oldpyfiles:        
        try:
            with open(xz, 'r') as pyfile:
                filecontents = pyfile.read()
                for patch in Settings.sims4_patches.keys():
                    if Settings.sims4_patches[patch] in filecontents:
                        filecontents = filecontents.replace(Settings.sims4_patches[patch], patch)
                        print(Fore.BLUE+ Settings.spacer + "--> Un-Patching: {}".format(xz.replace("\\","/")))
            with open(xz, 'w') as pyfile:
                pyfile.write(filecontents)
        except:
            pass
    
    try:
        try: os.remove(Settings.modpath+mod_name+".ts4script")
        except: pass
        shutil.copy(compiled_mod_name, Settings.modpath+mod_name+".ts4script")
        print(Fore.GREEN+ Settings.spacer + "* Copied '{}.ts4script' to Sims Mods folder".format(mod_name))
    except Exception as e:
        print(e)
        pass

    print(Fore.GREEN+"\n{}Compiled!".format( Settings.spacer ))
    print( Settings.spacer + "Press Enter to Continue.")
    clean(mod_name)
    os.system('pause >> nul')

def CreateMod(mod_name, _template):
    """Create a new mod."""
    print( Settings.spacer + "> Creating new Mod...")
    if not os.path.exists(r'./mods/'):
        os.mkdir('./mods')

    if not os.path.exists(r"./mods/{}".format(modname)):
        os.system("virtualenv ./mods/{} >> nul".format(modname))
        with open("./mods/{}/hello_world.py".format(modname), 'w') as hwfile:
            hwfile.write(_template)

        with open("./mods/{}/{}.modname".format(
            modname, 
            modname
        ), 'w') as modfile:
            modfile.write("")
    else:
        pass
    pass


cls()
print(logo)
print("   ╔═════════════════════════════════════════╦══════════════════════════════════════════╗")
print("   ║    Welcome to MatroSka Mod Compiler!    ║  Changelog:                              ║▓")
print("   ╠═════════════════════════════════════════╣  ----------                              ║▓")
print("   ║ Installation:                           ║  * Cleaned up the code a little.         ║▓")
print("   ║ -------------                           ║  * Added debug compile mode.             ║▓")
print("   ║ 1. Make sure you have python 3.7        ║  * Added Ease-Of-Access virtualenv-      ║▓")
print("   ║    installed and set as default.        ║    activator.                            ║▓")
print("   ║                                         ║                                          ║▓")
print("   ║ 2. Make sure that you have installed    ║                                          ║▓")
print("   ║    virtualenv via                       ║                                          ║▓")
print("   ║    pip install --user virtualenv        ║                                          ║▓")
print("   ║                                         ║                                          ║▓")
print("   ║ 3. Create a new mod by entering the     ║                                          ║▓")
print("   ║    number corresponding to              ║                                          ║▓")
print("   ║    'Create new Mod'.                    ║                                          ║▓")
print("   ╚═════════════════════════════════════════╩══════════════════════════════════════════╝▓")
print("    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
os.system("pause >> nul")

#! Main loop here

while 1:
    cls()
    print(logo)
    print(Fore.CYAN+ Settings.spacer + "Debug Build Mode: {}".format(Settings.debug))
    line()
    sims4mods = glob.glob("./mods/*/*.modname")

    counter = 1
    modcounter = []
    for x in sims4mods:
        print(Fore.LIGHTBLUE_EX + Settings.spacer + "{}. Compile: '{}'".format(counter,x.split('\\')[-1].replace(".modname","")))
        modcounter.append(x.split('\\')[-1].replace(".modname",""))
        counter += 1
    
    line()
    print(Fore.LIGHTRED_EX + Settings.spacer + "{}. {}".format("C","(C)reate New Mod."))
    print(Fore.LIGHTRED_EX + Settings.spacer + "{}. {}".format("D","Enable/Disable (D)ebug Build Mode (Includes Py Files in mod)."))
    print(Fore.LIGHTRED_EX + Settings.spacer + "{}. {}".format("M","Use Virtualenv to Install Python (M)odules for a mod."))
    line()

    number = input( Settings.spacer + "MMC>> ")

    if number.lower() == "c":
        modname = input("   MMC>>Mod_Name: ")
        CreateMod(modname, templates['hello_world'])

    elif number.lower() == "d":
        if Settings.debug: Settings.debug = False
        else: Settings.debug = True

    elif number.lower() == "m":
        print(Fore.CYAN + Settings.spacer + "Entering virtualenv mode...")
        number = input(Settings.spacer+"Mod Number: ")
        mod_name = (sims4mods[int(number) - 1].split('\\')[-1].replace(".modname",""))
        #python = '"./mods/{}/Scripts/python.exe"'.format(mod_name)
        activator_path = os.path.abspath("./mods/{}/Scripts/activate.bat".format(mod_name))
        #activator = '"./mods/{}/Scripts/activate_this.py"'.format(mod_name)
        line()
        print(Fore.LIGHTRED_EX+Settings.spacer+"Virtualenv active on '{}'.".format(mod_name))
        print(Fore.LIGHTRED_EX+Settings.spacer+"Type 'exit' to return to MMC. Use pip to install modules.")
        os.system("cmd /k {}".format(activator_path))

    else:
        try:
            mod_name = (sims4mods[int(number) - 1].split('\\')[-1].replace(".modname",""))

            mod_files = glob.glob("./{}/*.*".format(
                mod_name
            ))
            for scanner in mod_files:
                if scanner.endswith(".modname"):
                    mod_name = scanner
                    mod_files.remove(scanner)
            Compile_Mod(mod_name, Settings.debug)

        except Exception as e:
            pass
            #print( Settings.spacer + "{}".format(e))
            #os.system("pause >> nul")