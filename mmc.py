
from typing import Set
from zipfile import ZipFile
from colorama import init, Fore, Back, Style
import os, shutil, glob
from tabulate import tabulate

init(autoreset=True)

version = '0.3.0'

logo = ('''                                                                   
    _____ _____ _____ _____ _____ _____ _____ _____
   |     |  _  |_   _| __  |     |   __|  |  |  _  | Matroska Mod Compiler
   | | | |     | | | |    -|  |  |__   |    -|     | [Version {}]         
   |_|_|_|__|__| |_| |__|__|_____|_____|__|__|__|__|                      
    _____ _____ ____      _____ _____ _____ _____ _____ __    _____ _____  
   |     |     |    \    |     |     |     |  _  |     |  |  |   __| __  |
   | | | |  |  |  |  |   |   --|  |  | | | |   __|-   -|  |__|   __|    -|
   |_|_|_|_____|____/    |_____|_____|_|_|_|__|  |_____|_____|_____|__|__|
'''.format(version))

os.system('title MMC [Version {}]'.format(version))

def cls():
    os.system('cls')

def line():
    print("  ","═"*75)

important_files = ['.pem']

dead_critical_files = ['.pyd']

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
        'from enum import': 'from enum_lib import',
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
    important = []
    dead = []

    for y in important_files:
        important.append(
            [os.path.join(dp, f) for dp, 
            dn, 
            filenames in os.walk("./mods/{}".format(mod_name)) for f in filenames if os.path.splitext(f)[1] == y]
    )
    old_important = important
    important = []
    for imp in old_important:
        for impx in imp:
            important.append(impx)

    for y in dead_critical_files:
        dead.append(
            [os.path.join(dp, f) for dp, 
            dn, 
            filenames in os.walk("./mods/{}".format(mod_name)) for f in filenames if os.path.splitext(f)[1] == y]
    )
    old_dead = dead
    dead = []
    for ded in old_dead:
        for dedx in ded:
            dead.append(dedx)

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
    recusive_files['important'] = important
    recusive_files['deadfiles'] = dead
    
    return recusive_files

def nuke(mod_name):
    """Re-install virtualenv"""
    print( Settings.spacer + "> Nuking {}...".format(mod_name))
    dirtypaths = [
        './mods/{}/__pycache__'.format(mod_name), 
        './mods/{}/Lib'.format(mod_name),
        './mods/{}/Scripts'.format(mod_name),
    ]
    for x in dirtypaths:
        try: shutil.rmtree(x)
        except: pass
    print( Settings.spacer + "> Creating Virtualenv for {}...".format(mod_name))
    os.system("virtualenv ./mods/{} >> nul".format(mod_name))
    

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
    errored_files = []

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
                    fileAsLines = filecontents.split("\n")

                    for patch in Settings.sims4_patches.keys():
                        if patch in filecontents:
                            patchThisFile = True
                            break
                        else:
                            patchThisFile = False

                    if patchThisFile:
                        line_number = 0
                        newfile = ""
                        
                        for fileline in fileAsLines:
                            line_number += 1
                            lineIsPatched = False
                            if Settings.debug:
                                print(Settings.spacer+"{}. {}".format(line_number, fileline))
                            for patch in Settings.sims4_patches.keys():
                                if fileline == patch:
                                    lineIsPatched = True
                                    if Settings.debug:
                                        print(Fore.BLUE+ Settings.spacer + "{}. {} --> {}".format(line_number, fileline, Settings.sims4_patches[patch]))
                                    else:
                                        print(Fore.BLUE+ Settings.spacer + "--> Patching: {}, Line: {}".format(xz.replace("\\","/"), line_number))
                                    newfile += Settings.sims4_patches[patch] + "\n"
                                    #filecontents = filecontents.replace(patch,Settings.sims4_patches[patch])
                                    oldpyfiles.append(xz)
                            
                            if lineIsPatched == False:
                                newfile += fileline + "\n"
                
                        with open(xz, 'w') as pyfile:
                            pyfile.write(newfile)

            except Exception as e:
                print(Fore.YELLOW+ Settings.spacer + "--> {}".format(xz.split("\\",1)[-1]))
                errored_files.append(xz)
                
            #! Compiler
            try:
                os.system("python.exe -m py_compile {}".format(xz))
                print(Fore.LIGHTBLUE_EX+ Settings.spacer + "--> {}".format(xz.split("\\",1)[-1]))
            except:
                print(Fore.LIGHTRED_EX+ Settings.spacer + "--> Error: {}".format(xz.split("\\",1)[-1]))

    pycfiles = UpdateFileLists(mod_name)['pyc']
    pyfiles = UpdateFileLists(mod_name)['py']
    
    for xz in pycfiles:
        backonefolder = xz.replace("\\__pycache__\\","\\").replace("cpython-37.","")
        shutil.move(src="{}".format(xz), dst="{}".format(backonefolder))
    
    pycfiles = UpdateFileLists(mod_name)['pyc']
    compiled_mod_name = "./mods/{}/{}.ts4script".format(mod_name,mod_name)
    filestocompile = glob.glob("./mods/{}/*.*".format(mod_name))
    importantfiles = UpdateFileLists(mod_name)['important']
    
    #print(Fore.GREEN + Settings.spacer + "* {} | {}".format(compiled_mod_name,filestocompile))
    print(Fore.GREEN + Settings.spacer + "* Building Mod Archive...")
    with ZipFile(compiled_mod_name, 'w') as zip:   
        
        if importantfiles != []:
            print(Fore.GREEN + Settings.spacer + "-- Packing {} important files.".format(len(importantfiles)))
            for imp in importantfiles:
                targ_buffer = imp.split("\\",3)
                targ_buffer = targ_buffer[-1]
                name_in_archive = imp.split("\\")[-1]
                zip.write(
                    imp, arcname=targ_buffer
                )

        try:
            print(Fore.GREEN + Settings.spacer + "-- Packing {} pyc files.".format(len(pycfiles)))
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
                print(Fore.GREEN + Settings.spacer + "-- Packing {} py files.".format(len(pyfiles)))
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
        except Exception as e:
            print(Fore.RED+ Settings.spacer + "{}".format(e))
    
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
    
    line()
    
    deadfiles = UpdateFileLists(mod_name)['deadfiles']
    if len(deadfiles)>=1:
        print(Fore.RED+ Settings.spacer + "WARNING: Your mod contains imports that Sims 4 can't interpret.")
        print(Fore.RED+ Settings.spacer + "As a result, your mod might not function properly.")
        print(Fore.RED+ Settings.spacer + "Number of dead imports: {}".format(len(deadfiles)))
        print(Fore.RED+ Settings.spacer + "(Dead imports are files like .pyd files.)")
        line()

    totalfiles = len(deadfiles) + len(pyfiles) + len(pycfiles) + len(importantfiles) + len(errored_files)
    dead_imports = totalfiles - (len(deadfiles)*8) - (len(errored_files))
    probability = (dead_imports / totalfiles) * 100
    
    #print(Fore.GREEN+Settings.spacer+"Total Files: {} ".format(totalfiles))
    #print(Fore.GREEN+Settings.spacer+"Dead Files: {} ".format(dead_imports))
    print(Fore.GREEN+Settings.spacer+"Compiled "+mod_name)
    print(Fore.LIGHTCYAN_EX+Settings.spacer+"{} has a {}% chance of working without any issues.".format(mod_name,round(probability,2)))
    line()
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
print("   ║ Installation:                           ║  * Changed the patching method.          ║▓")
print("   ║ -------------                           ║  * Added Nuke Function.                  ║▓")
print("   ║ 1. Make sure you have python 3.7        ║  * Some more bug fixes.                  ║▓")
print("   ║    installed and set as default.        ║  * Added some new warnings.              ║▓")
print("   ║                                         ║                                          ║▓")
print("   ║ 2. Make sure that you have installed    ║                                          ║▓")
print("   ║    virtualenv via                       ║                                          ║▓")
print("   ║    pip install --user virtualenv        ║  WARNING: The patcher might be slightly  ║▓")
print("   ║                                         ║  more destructive, but it's a lot more   ║▓")
print("   ║ 3. Create a new mod by entering the     ║  accurate.                               ║▓")
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
    mods = []
    commands = []
    for x in sims4mods:
        mods.append(Fore.LIGHTBLUE_EX + "{}. Compile: {} ".format(counter,x.split('\\')[-1].replace(".modname","")+Fore.WHITE))
        modcounter.append(x.split('\\')[-1].replace(".modname",""))
        counter += 1
    
    commands.append(Fore.LIGHTRED_EX + "{}. {}".format("C","(C)reate New Mod."))
    commands.append(Fore.LIGHTRED_EX + "{}. {}".format("D","Enable/Disable (D)ebug Build Mode."))
    commands.append(Fore.LIGHTRED_EX + "{}. {}".format("M","Install (M)odules with virtualenv."))
    commands.append(Fore.LIGHTRED_EX + "{}. {}".format("N","Re-install virtualenv for a mod."))
    
    uitable = (tabulate({"Mods": mods,
        "Commands": commands},
        headers=['Mods (Enter number to compile)',
        'Commands'], tablefmt="presto"))

    for x in uitable.split("\n"):
        print(Settings.spacer + x)
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
        #print(Fore.LIGHTRED_EX+Settings.spacer+"PATH: {}".format(activator_path))
        print(Fore.LIGHTRED_EX+Settings.spacer+"Type 'exit' to return to MMC. Use pip to install modules.")
        os.system('cmd /k "{}"'.format(activator_path))

    elif number.lower() == "n": 
        print(Fore.RED + Settings.spacer + "WARNING. YOU ARE ABOUT TO RE-INSTALL VIRTUALENV")
        number = input(Settings.spacer+"Mod Number: ")
        mod_name = (sims4mods[int(number) - 1].split('\\')[-1].replace(".modname",""))
        line()
        nuke(mod_name)


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