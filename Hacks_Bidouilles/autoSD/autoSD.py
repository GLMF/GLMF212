#!/usr/bin/python3

import pystache
import subprocess
import os
from termcolor import cprint
import shutil


def clearWork(all=False):
    subprocess.Popen('sudo rm -Rf work/deploy/*', shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cprint(u'\u2713', 'green', end=' ')
    print('work/deploy directory cleared')
    
    if all:
        if subprocess.call(['sudo', 'rm', '-Rf', 'work']) == 0:
            cprint(u'\u2713', 'green', end=' ')
        else:
            cprint(u'\u2717', 'red', end=' ')
        print('work/ directory cleared')
    

def copyPiGen():
    error = 0
    if not os.path.isfile('work/build.sh'):
        if subprocess.call(['cp', '-R', 'pi-gen', 'work']) == 0:
            cprint(u'\u2713', 'green', end=' ')
        else:
            cprint(u'\u2717', 'red', end=' ')
            error = 1
        print('Copy of pi-gen/ to work/')
    return error
        

def copyTemplate(template, args={}):
    with open('templates/' + template, 'r') as fic_r:
        content = fic_r.read()
    with open('work/' + template, 'w') as fic_w:
        fic_w.write(pystache.render(content, args))


def chgUser(id='pi', pwd='raspberry', root_pwd='root'):
    copyTemplate('stage1/01-sys-tweaks/00-run.sh',
        { 
            'user_id' : id, 
            'user_pwd' : pwd, 
            'root_pwd' : root_pwd
        }
    )
    copyTemplate('stage2/01-sys-tweaks/01-run.sh',
        { 
            'user_id' : id
        }
    )
    cprint(u'\u2713', 'green', end=' ')
    print('user id and password changed')
    cprint(u'\u2713', 'green', end=' ')
    print('root password changed')


def chgHostname(hostname='raspberrypi'):
    copyTemplate('stage1/02-net-tweaks/files/hostname',
        { 
            'hostname' : hostname 
        }
    )
    copyTemplate('stage1/02-net-tweaks/00-patches/01-hosts.diff',
        { 
            'hostname' : hostname 
        }
    )
    cprint(u'\u2713', 'green', end=' ')
    print('hostname changed to', hostname)
 

def postrun(cmd, files=[]):
    copyTemplate('postrun.sh',
        {
            'commands' : cmd,
            'files' : files,
            'filesLength' : True if len(files) else False,
        }
    )
    subprocess.call(['chmod', 'ugo+x', 'work/postrun.sh'])
    cprint(u'\u2713', 'green', end=' ')
    print('postrun script copied')


def localesToFr():
    shutil.copyfile('templates/stage0/01-locale/00-debconf', 'work/stage0/01-locale/00-debconf')
    shutil.copyfile('templates/stage2/01-sys-tweaks/00-debconf', 'work/stage2/01-sys-tweaks/00-debconf')
    cprint(u'\u2713', 'green', end=' ')
    print('Locales set to french')


def buildImage(imageName, stage):
    with open('work/config', 'w') as fic_w:
        fic_w.write('IMG_NAME=' + imageName)

    if stage < 5:
        subprocess.call(['touch', 'work/stage5/SKIP'])
        subprocess.call(['rm', 'work/stage5/EXPORT_IMAGE'])
        subprocess.call(['rm', 'work/stage5/EXPORT_NOOBS'])
    if stage < 4:
        subprocess.call(['touch', 'work/stage4/SKIP'])
        subprocess.call(['rm', 'work/stage4/EXPORT_IMAGE'])
    if stage < 3:
        subprocess.call(['touch', 'work/stage3/SKIP'])
    if stage < 2:
        subprocess.call(['touch', 'work/stage2/SKIP'])
    if stage < 1:
        subprocess.call(['touch', 'work/stage1/SKIP'])
        
    os.chdir('work')
    subprocess.call(['sudo', './build.sh'])
    os.chdir('..')


def addPackage(package, filename):
    with open(filename, 'a') as fic_w:
        fic_w.write('\n' + package)
    cprint(u'\u2713', 'green', end=' ')
    print('Package {} added to {}'.format(package, filename))


if __name__ == '__main__':
    clearWork()
    if copyPiGen() != 0:
        print('Process aborted - no image created')
    chgUser('tristan', 'GLMF', 'p4ssw0rd')
    chgHostname('MonPiAMoi')

    postrun(cmd=[
        'userdel -r pi;',
        'chown -R tristan:tristan /home/tristan/Bureau',
    ],
            files=[
        '/home/tristan/Bureau /mnt/home/tristan',
    ])
    localesToFr()
    addPackage('gammu', 'work/stage2/01-sys-tweaks/00-packages')
    buildImage('MyRaspbian', 2)
