#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests, os, stat, subprocess # type: ignore
from platform import system as pl # type: ignore
from sys import argv as args_parser # type: ignore

name = 'pkm'
version = '1.0.2'
prefix = 'pkm'
update_url = 'https://raw.githubusercontent.com/VBPROGER/pkm/main/src/pkm.py'

pl = str(str(pl()).lower())
if pl == 'linux':
    pkm_local_path = os.path.join(os.path.expanduser('~'), '.config', 'pkm')
    execution_path = os.path.join(os.path.expanduser('~'), '.local', 'bin', 'pkm')
elif pl == 'windows':
    pkm_local_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'PKM File Manager')
    execution_path = os.path.expanduser('~')
else:
    pkm_local_path = os.path.join(os.path.expanduser('~'), '.config', 'pkm')
pkm_local_packages_path = os.path.join(str(pkm_local_path), 'packages')
pkm_local_cache_path = os.path.join(str(pkm_local_path), 'cache')
pkm_local_logs_path = os.path.join(str(pkm_local_path), 'logs')

def get_current_version(*args):
    url = 'https://raw.githubusercontent.com/VBPROGER/pkm/main/VERSION'
    response = requests.get(url)
    if response.ok:
        version = response.text.replace('\n', '')
        return version
    else:
        return False
def get_url_paths(url, ext='', params={}, *args):
    response = requests.get(url, params=params)
    if response.ok:
        response_text = response.text
    else:
        return response.raise_for_status()
    soup = BeautifulSoup(response_text, 'html.parser')
    parent = [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
    return parent
def setup(*args):
    paths = []
    if pl != 'windows':
        paths = [
            os.path.join(os.path.expanduser('~'), '.config'),
            os.path.join(os.path.expanduser('~'), '.config', 'pkm'),
            pkm_local_path,
            pkm_local_packages_path,
            pkm_local_cache_path,
            pkm_local_logs_path,
            os.path.join(os.path.expanduser('~'), '.local'),
            os.path.join(os.path.expanduser('~'), '.local', 'bin')
        ]
    else:
        paths = [
            os.path.join(os.path.expanduser('~'), 'AppData'),
            os.path.join(os.path.expanduser('~'), 'AppData', 'Local'),
            os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'PKM File Manager'),
            os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'PKM File Manager', 'packages'),
            pkm_local_cache_path,
            pkm_local_logs_path,
        ]
    for path in paths:
        os.system('mkdir -p '+str(path))
def check_version(warn_on_old: bool = True, exit_on_old: bool = False, auto_update: bool = False, *args):
    try:
        available_version = get_current_version()
        available_version = str(available_version)
        log('Available version: ' + available_version)
        log('Current version: ' + version)
        if warn_on_old == True:
            if version != available_version:
                if auto_update:
                    log('Autoupdate is enabled!')
                    self_update()
                    log('Updated. Now start the program again.')
                    exit(0)
                elif exit_on_old:
                    logerror('To keep using '+str(name.lower())+', please update it.')
                    exit(0)
                else: pass
            else:
                log('Your ' + str(name.lower() + ' is up-to-date.'))
        print('======================================')
    except BaseException as e:
        logerror('Failed to check if update needed!')
        log('It may be an error.')
        log('Error code:')
        print(str(e))
def no_run_flag_create(*args):
    with open(os.path.join(pkm_local_cache_path, 'norun.flag'), 'w') as f:
        f.write('# This program is running currently, so do not let other programs run this program again (until program ends)')
        f.close()
def logs_create(*args):
    with open(os.path.join(pkm_local_logs_path, 'last-log.log'), 'w') as f:
        f.write('Created logs')
        f.close()
def log(string = '', *args):
    if string:
        CONTENT = str(name) + ': ' + str(string)
        print(CONTENT)
        with open(os.path.join(pkm_local_logs_path, 'last-log.log'), 'a+') as f:
            f.write(CONTENT)
            f.close()
def logerror(string = '', *args):
    if not string == '' or string == None:
        CONTENT = str(name)+'.error: '+str(string)
        print(CONTENT)
        with open(os.path.join(pkm_local_logs_path, 'last-log.log'), 'a+') as f:
            f.write(CONTENT)
            f.close()
def logsuccess(string = '', *args):
    if not string == '' or string == None:
        CONTENT = str(name)+'.success: '+str(string)
        print(CONTENT)
        with open(os.path.join(pkm_local_logs_path, 'last-log.log'), 'a+') as f:
            f.write(CONTENT)
            f.close()
def downloadpkg(name = '0b', *args):
    log('Searching for package "'+name+'"...')
    name = str(name)
    link = 'https://raw.githubusercontent.com/VBPROGER/pkm/main/download/'+str(name.replace(' ','-'))+'.pkmfile'
    log('Reading content of package "'+name+'"...')
    try:
        f = requests.get(link)
    except BaseException:
        log('Package "'+name+'" was not found on server')
        log('Your internet connection may be off or is poor')
        return False
    content = str(f.text)
    if content.replace('\n', '') == '404: Not Found':
        log('Package "'+name+'" was not found on server')
        return False
    f.close()
    log('Saving package "'+name+'" to local installed packages folder...')
    file_name = str(os.path.join(pkm_local_path, 'packages', name+'.pkmfile'))
    with open(file_name, 'w') as f:
        f.write(content)
        f.close()
    st = os.stat(file_name)
    log('Giving execute permissions to package "'+name+'"... (final step)')
    os.chmod(file_name, st.st_mode | stat.S_IEXEC)
    log('Done, the package "'+name+'" was successfully installed')
    return True
def runpkg(pkg = '0b', local_package = True, shell = True, *args):
    try:
        pkg = str(pkg)
        pkg += '.pkmfile'
        pkg_pkmfile = pkg
        log('Attempting to execute package "'+pkg_pkmfile+'"')
        if local_package == True:
            pkg = os.path.join(str(pkm_local_packages_path), pkg)
        else: pkg = pkg
        if os.path.isfile(pkg) and os.path.exists(pkg):
            subprocess.call(pkg, shell = shell)
            logsuccess('Executed package "'+pkg_pkmfile+'" successfully')
            return True
        else:
            logerror('Error while attempting to execute package "'+pkg_pkmfile+'"'+": this package doesn't exist or not installed")
            return False
    except BaseException:
        logerror('Failed to execute package "'+pkg_pkmfile+'"')
        return False
def uninstallpkg(pkg, *args):
    try:
        pkg = os.path.join(str(pkm_local_packages_path), str(pkg))
        pkg += '.pkmfile'
        pkg_pkmfile = pkg
        log('Attempting to uninstall package "'+pkg_pkmfile+'"')
        if os.path.isfile(pkg) and os.path.exists(pkg):
            os.remove(pkg)
            logsuccess('Uninstalled package "'+pkg_pkmfile+'" successfully')
            return True
        else:
            logerror('Error while attempting to uninstall package "'+pkg_pkmfile+'"'+": this package is not installed")
            return False
    except BaseException:
        logerror('Failed to uninstall package "'+pkg_pkmfile+'"')
        return False
def get_installed_packages_list(*args):
    try:
        log('Getting packages list...')
        packages = os.scandir(str(pkm_local_packages_path))
        packagesFound = 0
        for package in packages:
            if package.is_dir() or package.is_file():
                if str(package.name).endswith('.pkmfile'):
                    log('Found package "'+str(package.name)+'"')
                    packagesFound += 1
        logsuccess('Done, finished getting packages list. Total count of packages: '+str(packagesFound))
    except BaseException:
        logerror('Failed to get list of installed packages')
        return False
def self_update(confirmation: bool = False, custom_path: str = '', *args):
    if confirmation:
        log('Updating...')
        try:
            f = requests.get(update_url)
            CONTENT = str(f.text)
            f.close()
        except BaseException as e:
            log('Failed to download update.')
            log('Your internet connection may be off or is poor!')
            log('This may be an error: '+str(e))
            return False
        if pl != 'windows':
            file_name = os.path.join(os.path.expanduser('~'), '.local', 'bin', 'pkm')
            with open(file_name, 'w') as f:
                f.write(str(CONTENT))
                f.close()
            st = os.stat(file_name)
            os.chmod(file_name, st.st_mode | stat.S_IEXEC)
        else:
            file_name = os.path.join(os.path.expanduser('~'), 'pkm')
            with open(file_name, 'w') as f:
                f.write(str(CONTENT))
                f.close()
            st = os.stat(file_name)
            os.chmod(file_name, st.st_mode | stat.S_IEXEC)
        logsuccess('Finished downloading update!')
def argument_parser(*args) -> None:
    if len(args_parser) <= 1:
        log('Invalid command! Type "'+str(name)+' --help" for more info.')
        return False
    try:
        Arg1 = args_parser[1]
        Arg1 = Arg1.lower()
        Arg2 = args_parser[2]
        Arg2 = Arg2.lower()
        Arg3 = args_parser[3]
        Arg3 = Arg3.lower()
        Arg4 = args_parser[4]
        Arg4 = Arg4.lower()
    except BaseException: pass
    if Arg1 == '--help' or Arg1 == '-h' or Arg1 == '--h':
        n = 'Command: ' + str(name) + ''
        print(str(name)+'.help: List of aviable commands')
        print(f''' - LIST -
{n} install <package-name> - download package by name (*2) (*1)
{n} uninstall <package-name> - delete package from current PC by name (*1)
{n} run <package-name> - run package by name (*1)
{n} runhere <path-to-package> - run package by name (in current folder or /path/to/file.pkmfile) (*1)
{n} installed_list - get installed packages list
{n} aviable_list - get aviable packages list (*2)
{n} clear_logs - clear all unused logs of pkm

*1 = argument required
*2 = internet required
- LIST END -''')
        return True
    try:
        if Arg1 == 'install':
            downloadpkg(Arg2)
            return True
        elif Arg1 == 'run':
            runpkg(pkg = Arg2, local_package = True, shell = True)
        elif Arg1 == 'runhere':
            runpkg(pkg = Arg2, local_package = False, shell = True)
        elif Arg1 == 'uninstall':
            uninstallpkg(pkg = Arg2)
        elif Arg1 == 'installed_list':
            get_installed_packages_list()
        elif Arg1 == 'available_list':
            url = 'https://github.com/VBPROGER/pkm/tree/main/download'
            log('You can view aviable packages on GitHub:')
            print('Copy and paste this in new tab: ' + str(url))
        elif Arg1 == 'clear_logs':
            log('Clearing logs, please wait...')
            os.remove(str(os.path.join(pkm_local_logs_path, 'last-log.log')))
            print(str(name)+'.success: Finished clearing logs, now your memory is more free')
        elif Arg1 == 'update':
            log('Updating PKM...')
            self_update(confirmation = True)
        else:
            log('Invalid command! Type "'+str(name)+' --help" for more info.')
            return False
    except BaseException as e:
        log('Uncompleted or invalid command! Type "'+str(name)+' --help" for more info.')
        log('This may be an error: '+str(e))
        return False
setup()
if not os.path.isfile(str(os.path.join(pkm_local_cache_path, 'norun.flag'))):
    no_run_flag_create()
    logs_create()
    check_version(exit_on_old = False, warn_on_old = True, auto_update = False)
    argument_parser()
    os.remove(str(os.path.join(pkm_local_cache_path, 'norun.flag')))
    exit(0)
else:
    exit(0)