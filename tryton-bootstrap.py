#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Inicialitzador de projecte

Inicialitza un projecte creant l'estructura de directoris necessària i
obtenint el codi dels repositoris.
Pot ser executat des del directori del repositori 'tryton-buildout' o
descarregant-se el fitxer i executant-lo des del directori base del projecte
de client.
"""

from datetime import date
import os
import sys
from optparse import OptionParser
from path import path

USAGE = '''\
[INICIALITZADOR PROJECTES TRYTON] tryton-buildout.py [options]

Inicialitza un projecte Tryton.

Executa aquest script des d'un respositori 'tryton-buildout' o des del
directori base del nou projecte.

hg clone ssh://hg@hg.bitbucket.org/nantic/tryton-buildout buildout
pushd buildout
pip install -r requirements.txt
python bootstrap.py
./build/bin/buildout -c base.cfg
./build/bin/buildout -c buildout.cfg
popd
'''

INITIAL_PATH = path.getcwd()


def _ask_ok(prompt, default_answer=None):
    ok = raw_input(prompt) or default_answer
    if ok in ('y', 'ye', 'yes'):
        return True
    if ok in ('n', 'no', 'nop', 'nope'):
        return False
    print "Yes or no, please"


def _exit(message):
    if path.getcwd() != INITIAL_PATH:
        os.chdir(INITIAL_PATH)
    sys.exit(message)


def _check_required_file(filename, directory_name, directory_path):
    if not directory_path.joinpath(filename).exists():
        _exit('%s file not found in %s directory: %s' % (filename,
                directory_name, directory_path))


def activate_virtualenv(options):
    virtualenv = os.environ.get('VIRTUAL_ENV')
    if virtualenv:
        return
    if not options.virtualenv and 'WORKON_HOME' in os.environ:
        # virtualenvwrapper avilable. confirm don't activate virtualenv
        if _ask_ok('You have available the "virtualenvwrapper". Are you '
                'sure you don\'t whant to prepare project in a virtualenv? '
                'Answer "yes" to continue without activate a virtualenv. '
                '[Yes/no (activate)] ', 'y'):
            return

    if 'WORKON_HOME' not in os.environ:
        _exit('ERROR: To could activate a virtualenv it\'s required the '
            '"virtualenvwrapper" installed and configured.')

    virtualenv_path = path(os.environ['WORKON_HOME']).joinpath(
        options.project_name)
    if not virtualenv_path.exists() or not virtualenv_path.isdir():
        _exit('ERROR: Do not exists a virtualenv for project "%s" in '
            'workon directory: %s. Create it with "mkvirtualenv" tool.'
            % (options.project_name, virtualenv_path))

    activate_this_path = virtualenv_path.joinpath('bin/activate_this.py')
    print "Activating virtualenv %s" % options.project_name
    execfile(activate_this_path, dict(__file__=activate_this_path))


def clone_buildout(options):
    if options.buildout_path.exists():
        return
    if not options.clone_buildout:
        if not _ask_ok('Are you in the customer project directory? '
                'Answer "yes" to clone the "tryton-buildout" repository '
                'and bootstrap it. [Y/n] ', 'y'):
            _exit('ERROR: nan-bootstrap.py must to be called from '
                '"buildout" or customer directory')
    from sh import hg
    print ('Cloning ssh://hg@hg.bitbucket.org/nantic/tryton-buildout '
        'repository in "buildout" directory.')
    hg('clone', 'ssh://hg@hg.bitbucket.org/nantic/tryton-buildout',
        str(options.buildout_path), _out=options.output, _err=sys.stderr)
    print ""


def install_requirements(options):
    if not options.requirements:
        return
    from sh import pip
    print 'Installing dependencies.'
    _check_required_file('requirements.txt', 'buildout', path.getcwd())
    if options.upgrade:
        pip.install('--upgrade', '-r', 'requirements.txt',
            _out=options.output, _err=sys.stderr)
    else:
        pip.install('-r', 'requirements.txt', _out=options.output,
            _err=sys.stderr)
    print ""


def prepare_local(options):
    local_path = options.project_path.joinpath('local.cfg')
    if local_path.exists() and not options.force_local:
        return
    if not options.modules:
        ask_modules_msg = ('Write the list (separated by coma) of the '
            'customer\'s specific modules [%s]: ' % options.project_name)
        options.modules = map(str.strip, raw_input(ask_modules_msg).split(','))
        if options.modules == ['']:
            options.modules = [options.project_name]
    if options.userdoc:
        if not options.userdoc_title:
            options.userdoc_title = (
                raw_input('Write the title for the user documentation: '
                    '[Tryton] ') or 'Tryton user\'s manual')
        if not options.userdoc_author:
            options.userdoc_author = (
                raw_input('The author of user documentation: [NaN·tic] ') or
                'NaN·tic')
        if not options.userdoc_copyright:
            default = 'NaN·tic, Projectes de programari lliure'
            options.userdoc_copyright = (
                raw_input('The name for copyright in user documentation: [%s] '
                    % default) or default)
    module_sources = []
    userdoc_modules = []
    for module in options.modules:
        if not module:
            continue
        module_sources.append(
            '%s = hg ssh://hg@hg.nan-tic.com/trytond-%s egg=False'
            % (module, module))
        userdoc_modules.append("    '%s'," % module)
    with open(str(local_path), 'w') as local_file:
        local_file.write("""[buildout]
auto-checkout += *

[sources]
%s
""" % ("\n".join(module_sources)))
        if not options.userdoc:
            return
        local_file.write("""
[userdoc-config]
project_title = u'%s'
author = u'%s'
copyright = u'%s, %s'
module_list =
%s
""" % (options.userdoc_title, options.userdoc_author, date.today().year,
            options.userdoc_copyright, "\n".join(userdoc_modules)))


def bootstrap_buildout(options):
    if not options.bootstrap_buildout:
        return
    from sh import python
    print 'Calling Buildout bootstrap.py script.'
    _check_required_file('bootstrap.py', 'buildout', path.getcwd())
    try:
        python('bootstrap.py', _out=options.output, _err=sys.stderr)
    except:
        _exit("Error executing 'bootstrap.py' script from %s" % path.getcwd())
    print ""


def buildout(options):
    if not options.buildout:
        return
    import sh
    print 'Executing buildout.'
    _check_required_file('./build/bin/buildout', 'buildout', path.getcwd())
    buildout_sh = sh.Command('./build/bin/buildout')

    _check_required_file('base.cfg', 'buildout', options.buildout_path)
    buildout_sh('-c', 'base.cfg', _out=options.output, _err=sys.stderr)

    _check_required_file('buildout.cfg', 'buildout', options.buildout_path)
    buildout_sh('-c', 'buildout.cfg', _out=options.output, _err=sys.stderr)

    if options.userdoc:
        _check_required_file('userdoc.cfg', 'buildout', options.buildout_path)
        buildout_sh('-c', 'userdoc.cfg', _out=options.output, _err=sys.stderr)


def prepare_symlinks(options):
    import sh
    print "Preparing symlinks."
    bin_path = options.project_path.joinpath('bin')
    if not bin_path.exists():
        bin_path.mkdir()
    script_list = (options.buildout_path.joinpath('build/bin').listdir() +
        options.buildout_path.listdir('*.sh') +
        options.project_path.joinpath('utils').listdir('*.py'))
    for script in script_list:
        symlink = bin_path.joinpath(script.basename())
        if symlink.exists():
            continue
        bin_path.relpathto(script).symlink(symlink)
        if options.verbose:
            print "Created symlink in %s to %s" % (symlink, script)
    if not options.project_path.joinpath('modules').exists():
        path('trytond/trytond/modules').symlink(
            options.project_path.joinpath('modules'))


def prepare_userdoc(options):
    import sh
    if not options.userdoc:
        return
    print "Preparing user documentation system."
    options.userdoc_path = options.project_path.joinpath('userdoc')
    if not options.userdoc_path.exists():
        sys.exit('"userdoc" directory doesn\'t exits in project\'s root '
            'directory. Please, execute buildout with userdoc.cfg file.')
    sh.Command('./create-doc-symlinks.sh')(_out=options.output,
        _err=sys.stderr)
    os.chdir(options.userdoc_path)
    install_requirements(options)
    from sh import make
    make(_out=options.output, _err=sys.stderr)


if __name__ == '__main__':
    parser = OptionParser(usage=USAGE)
    parser.add_option('-e', '--virtualenv', action='store_true', default=False,
        help='Install project in a virtualenv. If virtualenv is not active, '
        'it try to activate a virtualenv with the name of project directory '
        'before install dependencies).')
    parser.add_option('-c', '--clone-buildout', action='store_true',
        default=False,
        help='If "buildout" directory is not found, it clones the '
        '"tryton-buildout" repository in new "buildout" directory.')
    parser.add_option('', '--no-requirements', dest='requirements',
        action='store_false', default=True,
        help='Don\'t install the packages using requirements.txt')
    parser.add_option('-u', '--upgrade', action='store_true',
        help='Install requirements forcing versions (call '
        'pip install --upgrade -r requirements.txt)')
    parser.add_option('-l', '--force-local', action='store_true',
        help='Creates a new local.cfg file.')
    parser.add_option('', '--no-userdoc', dest='userdoc', action='store_false',
        default=True, help='Don\'t prepare user documentation system.')
    parser.add_option('-m', '--module', dest='modules', action='append',
        help='Customer\'s specific module. It will be added in "local.cfg" '
        'file and in user documentation.')
    parser.add_option('', '--userdoc-title',
        help='Title for the user documentation')
    parser.add_option('', '--userdoc-author',
        help='Author for the user documentation')
    parser.add_option('', '--userdoc-copyright',
        help='Author for the copyright advice of user documentation')
    parser.add_option('', '--no-bootstrap', dest='bootstrap_buildout',
        action='store_false', default=True,
        help='Don\t execute buildout\'s bootstrap.py script.')
    parser.add_option('', '--no-buildout', dest='buildout',
        action='store_false', default=True,
        help='Don\t execute buildout.')

    parser.add_option('-q', '--quite', action='store_true',
        help="Don't print the output of called commands")
    parser.add_option('-v', '--verbose', action='store_true',
        help="Show more messages on standard output")

    options, args = parser.parse_args()

    if options.quite:
        options.output = None
    else:
        options.output = sys.stdout

    if INITIAL_PATH.basename() == 'buildout':
        options.project_path = INITIAL_PATH.parent
        options.buildout_path = INITIAL_PATH
    else:
        options.project_path = INITIAL_PATH
        options.buildout_path = INITIAL_PATH.joinpath('buildout')

    options.project_name = str(options.project_path.basename())
    if options.verbose:
        print "project_name=%s" % options.project_name

    activate_virtualenv(options)
    clone_buildout(options)

    if path.getcwd() != options.buildout_path:
        os.chdir(options.buildout_path)

    install_requirements(options)
    prepare_local(options)
    bootstrap_buildout(options)
    buildout(options)
    prepare_symlinks(options)
    prepare_userdoc(options)

    if path.getcwd() != INITIAL_PATH:
        os.chdir(INITIAL_PATH)
    print "OK"
