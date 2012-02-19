# Here you can create play commands that are specific to the module, and extend existing commands
import getopt
import tempfile
from play.utils import *
import play.commands.war
import subprocess
import shutil

MODULE = 'dotcloud'

# Commands that are specific to your module

COMMANDS = ['dotcloud:deploy']

def execute(**kargs):
    command = kargs.get("command")
    app = kargs.get("app")
    args = kargs.get("args")
    env = kargs.get("env")

    if command == "dotcloud:deploy":
        deployment = ""
        try:
            optlist, args2 = getopt.getopt(args, '', ['deployment='])
            for o, a in optlist:
                if o == '--deployment':
                    deployment = a

        except getopt.GetoptError, err:
            print "~ Error: %s" % str(err)
            print "~ "
            sys.exit(-1)
        
        retCode = -1
        try:
            retCode = subprocess.call(['dotcloud'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError, err:
            print "~ Error: dotcloud executable not installed or not in PATH variable"
            print "~ "
            sys.exit(-1)
        
        deploy(command, env, app, deployment)

# This will be executed before any command (new, run...)
def before(**kargs):
    command = kargs.get("command")
    app = kargs.get("app")
    args = kargs.get("args")
    env = kargs.get("env")


# This will be executed after any command (new, run...)
def after(**kargs):
    command = kargs.get("command")
    app = kargs.get("app")
    args = kargs.get("args")
    env = kargs.get("env")

    if command == "new":
        pass

def deploy(command, env, app, deployment = None):
    # check if everything is in place
    
    if app.conf == None:
        print "~ Error: not a valid Play! application"
        print "~ "
        sys.exit(-1)
    
    try:
        assert os.path.exists(os.path.join(app.path, 'conf', 'dotcloud.yml'))
    except AssertionError:
        print "~ Oops. conf/dotcloud.yml missing. Please consult with dotcloud's documentation on how to create one."
    
    if deployment == None or deployment == '':
        deployment = app.conf.get("dotcloud.deployment")
        if deployment == '':
            print "~ Error: no deployment given; use --deployment or specify it in application.conf as dotcloud.deployment"
            print "~ "
            sys.exit(-1)
            
    originalId = env['id']

    dotcloudId = app.conf.get("dotcloud.id")
    if dotcloudId != '':
      env['id'] = dotcloudId
    else:
      env['id'] = "prod"
            
    print "~ Deploying to \""+ deployment + "\" with id \"" + env['id'] + "\" (use dotcloud.id in application.conf to change)"
    
    # create WAR file
    print "~ Creating WAR file ..."
    tmpPath = tempfile.mkdtemp()
    warDirPath = os.path.join(tmpPath, "root")
    
    play.commands.war.execute(command=command, app=app, args=['--output', warDirPath, '--zip'], env=env)
    env['id'] = originalId
    
    shutil.rmtree(warDirPath)
    
    # copy conf/dotcloud.yml to tmpPath
    shutil.copyfile(os.path.join(app.path, 'conf', 'dotcloud.yml'), os.path.join(tmpPath, 'dotcloud.yml'))
    print tmpPath
    
    # push to dotcloud
    print "~ WAR file created, contacting dotcloud ..."
    try:
        retCode = subprocess.call(['dotcloud', 'push', deployment, tmpPath])
    except OSError, err:
        print "~ Error: dotcloud executable not installed or not in PATH variable"
        print "~ "
        sys.exit(-1)
    
    shutil.rmtree(tmpPath)
    print "~ Done! "
