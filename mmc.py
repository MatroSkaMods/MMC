
from zipfile import ZipFile
from colorama import init, Fore, Back, Style
import os, shutil, glob
init(autoreset=True)


logo = ('''
 ███╗   ███╗███╗   ███╗ ██████╗ ---------------------
 ████╗ ████║████╗ ████║██╔════╝ Matroska Mod Compiler
 ██╔████╔██║██╔████╔██║██║      for .ts4Script files
 ██║╚██╔╝██║██║╚██╔╝██║██║      ---------------------
 ██║ ╚═╝ ██║██║ ╚═╝ ██║██║      ---------------------
 ██║     ██║██║     ██║██║      [Ver 0.1] 
 ██║     ██║██║     ██║╚██████╗ 
 ╚═╝     ╚═╝╚═╝     ╚═╝ ╚═════╝ ''')


modpath = "C:\\Users\\{}\\Documents\\Electronic Arts\\The Sims 4\\Mods\\".format(
    os.getlogin()
)

sims4_patches = {
    'import enum': 'import enum_lib as enum',
    'from enum import': 'from enum_lib import'
}

hello_world = """from sims4.commands import Command, CommandType, CheatOutput

# Adds a new cheat can be called with "hello".

@Command('hello', command_type=CommandType.Live)
def sayhello(_connection=None):
    output = CheatOutput(_connection)
    output('Hello, world!')
"""

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

def cleaner(mod_name):
    dirty_files_pyc = glob.glob("./{}/*.pyc".format(mod_name))
    dirty_files_ts4 = glob.glob("./{}/*.ts4script".format(mod_name))
    try:
        for x in dirty_files_pyc:
            print(x)
            os.remove(x)
        for x in dirty_files_ts4:
            os.remove(x)
    except Exception as e:
        print(e)
def softcleaner(mod_name):
    dirty_files_pyc = glob.glob("./{}/*.pyc".format(mod_name))
    try:
        for x in dirty_files_pyc:
            os.remove(x)
    except Exception as e:
        print(e)

os.system('title MatroSka Mod Compiler 0.1')

os.system('cls')
print(logo)
print(" ╔═════════════════════════════════════════╗")
print(" ║    Welcome to MatroSka Mod Compiler!    ║▓ Changelog:")
print(" ╠═════════════════════════════════════════╣▓ ----------")
print(" ║ Installation:                           ║▓ * Added patching feature")
print(" ║ -------------                           ║▓   - MMC now does basic patches")
print(" ║ 1. Make sure you have python 3.7        ║▓     to allow modules to be")
print(" ║    installed and set as default.        ║▓     a little more compatible")
print(" ║                                         ║▓     with Sims4.")
print(" ║ 2. Make sure that you have installed    ║▓  ")
print(" ║    virtualenv via                       ║▓ * Added virtualenv as requirement")
print(" ║    pip install --user virtualenv        ║▓")
print(" ║                                         ║▓ * Added Hello World script on")
print(" ║ 3. Create a new mod by entering the     ║▓   mod creation")
print(" ║    number corresponding to              ║▓")
print(" ║    'Create new Mod'.                    ║▓")
print(" ╚═════════════════════════════════════════╝▓")
print("  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
os.system("pause >> nul")

while 1:
    os.system('cls')
    print(logo)
    print("","-"*55)
    sims4mods = glob.glob("./*/*.modname")

    counter = 1
    modcounter = []
    for x in sims4mods:
        print(Fore.LIGHTBLUE_EX + " {}. Compile {}".format(counter,x.split('\\')[-1].replace(".modname","")))
        modcounter.append(x.split('\\')[-1].replace(".modname",""))
        counter += 1
    print("","-"*55)
    print(Fore.LIGHTRED_EX + " {}. {}".format(counter,"Create New Mod"))
    
    print("","-"*55)
    number = input(" MMC>> ")
    try:
        mod_name = (sims4mods[int(number) - 1].split('\\')[-1].replace(".modname",""))
        
        old_mod_name = mod_name
        cleaner(old_mod_name)

        mod_files = glob.glob("./{}/*.*".format(
            mod_name
        ))
        for scanner in mod_files:
            if scanner.endswith(".modname"):
                mod_name = scanner
                mod_files.remove(scanner)
        #! clean files here
        #print("MOD_FILES:",mod_files)
        print(" Attempting to Compile {}".format(old_mod_name))
        pyfiles = [os.path.join(dp, f) for dp, dn, filenames in os.walk("./{}".format(old_mod_name)) for f in filenames if os.path.splitext(f)[1] == '.py']
        oldpyfiles = []
        for xz in pyfiles:
            #! Patcher
            for ign in ignorelist:
                if ign in xz:
                    #print(Fore.CYAN+ " --> IGNORE: {}".format(xz))
                    ignore = True
                    break
                else:
                    ignore = False

            if ignore == False:
                try:
                    with open(xz, 'r') as pyfile:
                        filecontents = pyfile.read()
                        for patch in sims4_patches.keys():
                            if patch in filecontents:
                                print(Fore.BLUE+" --> Patching: {}".format(xz))
                                filecontents = filecontents.replace(patch,sims4_patches[patch])
                                oldpyfiles.append(xz)
                    with open(xz, 'w') as pyfile:
                        pyfile.write(filecontents)
                except Exception as e:
                    print(Fore.YELLOW+ " --> Patching Error: {}".format(e))
                    
                #! Compiler
                try:
                    os.system("python.exe -m py_compile {}".format(xz))
                    print(Fore.LIGHTBLUE_EX+" --> Compiled: {}".format(xz))
                except:
                    print(Fore.LIGHTRED_EX+ " --> Error compiling: {}".format(xz))

        pycfiles = [os.path.join(dp, f) for dp, dn, filenames in os.walk("./{}".format(old_mod_name)) for f in filenames if os.path.splitext(f)[1] == '.pyc']  
        for xz in pycfiles:
            backonefolder = xz.replace("\\__pycache__\\","\\").replace("cpython-37.","")
            shutil.move(src="{}".format(xz), dst="{}".format(backonefolder))
        
        pycfiles = [os.path.join(dp, f) for dp, dn, filenames in os.walk("./{}".format(old_mod_name)) for f in filenames if os.path.splitext(f)[1] == '.pyc']  
        pyfiles = [os.path.join(dp, f) for dp, dn, filenames in os.walk("./{}".format(old_mod_name)) for f in filenames if os.path.splitext(f)[1] == '.py']  
        
        compiled_mod_name = "./{}/{}.ts4script".format(old_mod_name,old_mod_name)
        filestocompile = glob.glob("./{}/*.*".format(old_mod_name))
        
        print(Fore.GREEN+" * Building Mod Archive...")

        with ZipFile(compiled_mod_name, 'w') as zip:
            for y in pycfiles:
                for ign in ignorelist:
                    if ign in y:
                        ignore = True
                        break
                    else:
                        ignore = False
                if ignore == False:
                    targ_buffer = y.split("\\",3)
                    targ_buffer = targ_buffer[-1]
                    #print(targ_buffer)
                    name_in_archive = y.split("\\")[-1]
                    #print(".", end="")
                    zip.write(
                        y, arcname=targ_buffer
                    )
                    os.remove(y)

            """
            for z in pyfiles:
                for ign in ignorelist:
                    if ign in z:
                        ignore = True
                        break
                    else:
                        ignore = False
                if ignore == False:
                    targ_buffer = z.split("\\",3)
                    targ_buffer = targ_buffer[-1]
                    #print(targ_buffer)
                    name_in_archive = z.split("\\")[-1]
                    #print(".", end="")
                    zip.write(
                        z, arcname=targ_buffer
                    )
            """
        
        print(Fore.GREEN+" * Rolling back patches...")
        
        for xz in oldpyfiles:        
            try:
                with open(xz, 'r') as pyfile:
                    filecontents = pyfile.read()
                    for patch in sims4_patches.keys():
                        if sims4_patches[patch] in filecontents:
                            filecontents = filecontents.replace(sims4_patches[patch], patch)
                            print(Fore.BLUE+" --> Un-Patching: {}".format(xz))
                with open(xz, 'w') as pyfile:
                    pyfile.write(filecontents)
            except:
                pass
        
        try:
            try: os.remove(modpath+old_mod_name+".ts4script")
            except: pass
            shutil.copy(compiled_mod_name, modpath+old_mod_name+".ts4script")
            print(Fore.GREEN+" * Copied '{}.ts4script' to Sims Mods folder".format(old_mod_name))
        except Exception as e:
            print(e)
            pass

        print(Fore.GREEN+"\n Compiled!")
        print(" Press Enter to Continue.")
        softcleaner(old_mod_name)
        os.system('pause >> nul')

    except Exception as e:
        try:
            if int(number) == len(modcounter)+1:
                modname = input(" MMC>>Mod_Name: ")
                print(" > Creating new Mod...")
                if not os.path.exists(r"{}".format(modname)):
                    os.system("virtualenv ./{} >> nul".format(modname))
                    #    os.makedirs(modname)
                    with open("./{}/hello_world.py".format(modname), 'w') as hwfile:
                        hwfile.write(hello_world)

                    with open("./{}/{}.modname".format(
                        modname, 
                        modname
                    ), 'w') as modfile:
                        modfile.write("")
                else:
                    pass
        except Exception as e:
            pass