import subprocess
from data.data import ASSET
import os

def __do_command(command_array):
    script_dir = os.path.dirname(os.path.abspath(__file__)) # TODO: Optimization
    print(script_dir)
    result = subprocess.run(command_array, capture_output=True, text=True, cwd=script_dir)
    print(f"\033[33m{' '.join(command_array)}\033[0m: {result.stdout}")

def zip_file(): 
    zip_command = [
        "zip", "-j" , "./data/sTest/sTest.zip", "./data/sTest/package.json", "./data/sTest/sTest.py"
    ]
    __do_command(zip_command)

def copy_zip():
    copy_command = [
            "docker", "cp", "./data/sTest/sTest.zip",
            "docker-dev-charging-1:/business-ecosystem-charging-backend/src"
        ]
    __do_command(copy_command)

def load_plugin():
    load_command = [
            "docker", "exec", "docker-dev-charging-1",
            "python3", "/business-ecosystem-charging-backend/src/manage.py", "loadplugin", "/business-ecosystem-charging-backend/src/sTest.zip"
        ]
    __do_command(load_command)


def remove_plugin():
    remove_command = [
            "docker", "exec", "docker-dev-charging-1",
            "python3", "/business-ecosystem-charging-backend/src/manage.py", "removeplugin", f"{ASSET['resourceType'].lower().replace(' ', '-')}"
        ]
    __do_command(remove_command)

def remote_delete_zip():
    delete_command = [
            "docker", "exec", "docker-dev-charging-1",
            "rm", "./business-ecosystem-charging-backend/src/sTest.zip"
        ]
    __do_command(delete_command)

def delete_zip():
    delete_command = [
            "rm", "./data/sTest/sTest.zip"
        ]
    __do_command(delete_command)


# zip_file()
# copy_zip()
load_plugin()
# delete_zip()
# remote_delete_zip()
# remove_plugin()
