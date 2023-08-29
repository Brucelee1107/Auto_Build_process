import os
import subprocess
import requests
import yaml

class AutoBuild:
    @staticmethod
    def package_installation():
        try:
            # Packages install from the given path using yaml
            yaml_file_path = "https://raw.githubusercontent.com/Brucelee1107/Auto_Build_process/main/packages_to_install.yaml"
            response = requests.get(yaml_file_path)
            response.raise_for_status()
            packages_data = yaml.safe_load(response.text)

            packages_to_install = packages_data.get('packages', [])
            for package in packages_to_install:
                subprocess.run(['sudo', 'apt', 'install', '-y', package], check=True)

            package_generation = packages_data.get('generation', [])
            for generate in package_generation:
                subprocess.run(['sudo', generate], check=True)
        except Exception as e:
            print(f'Error: {e}')

        AutoBuild.creating_dir()

    @staticmethod
    def creating_dir():
        try:
            # Creating a new directory for the build process
            current_dir = os.getcwd()
            machine_name_dir = os.path.join(current_dir, "machine_name")

            if not os.path.exists(machine_name_dir):
                os.makedirs(machine_name_dir)

            AutoBuild.cloning_and_build_env(machine_name_dir)
        except Exception as e:
            print(f'Error: {e}')

    @staticmethod
    def cloning_and_build_env(file_path):
        try:
            # Clone reference distribution poky
            os.chdir(file_path)
            subprocess.run(['git', 'clone', 'git://git.yoctoproject.org/poky'], check=True)

            # Clone OE
            os.chdir('poky')
            subprocess.run(['git', 'clone', 'http://git.openembedded.org/meta-openembedded'], check=True)

            # Clone specified target machine
            subprocess.run(['git', 'clone', 'https://git.yoctoproject.org/meta-raspberrypi'], check=True)

            # Create an environment to build
            build_path = os.path.join(file_path, 'poky')
            init_env_script = os.path.join(build_path, 'oe-init-build-env')
            command = f'source {init_env_script} {os.path.join(build_path, "build")}'
            subprocess.run(command, shell=True, executable='/bin/bash', env=os.environ, check=True)
        except Exception as e:
            print(f'Error: {e}')

        AutoBuild.add_machine_layer(file_path, build_path)

    @staticmethod
    def add_machine_layer(file_path, build_path):
        try:
            target_machine_layer = os.path.join(build_path, 'meta-raspberrypi')
            bblayers_path = os.path.join(file_path, 'poky', 'build', 'conf', 'bblayers.conf')

            with open(bblayers_path, 'r') as file:
                bblayers_content = file.readlines()

            for i, line in enumerate(bblayers_content):
                if line.startswith("BBLAYERS"):
                    machine_layer = f'  {target_machine_layer} \\\n'
                    bblayers_content[i] = machine_layer

            with open(bblayers_path, 'w') as file:
                file.writelines(bblayers_content)

            AutoBuild.change_machine_name(file_path)
        except Exception as e:
            print(f'Error: {e}')

    @staticmethod
    def change_machine_name(file_path):
        try:
            local_conf_path = os.path.join(file_path, 'poky', 'build', 'conf', 'local.conf')

            with open(local_conf_path, 'r') as file:
                local_conf_content = file.readlines()

            for i, line in enumerate(local_conf_content):
                if line.startswith("MACHINE"):
                    target_machine_name = 'raspberrypi'
                    local_conf_content[i] = f'MACHINE ?= "{target_machine_name}"\n'

            with open(local_conf_path, 'w') as file:
                file.writelines(local_conf_content)

            AutoBuild.bitbake_tool(file_path)
        except Exception as e:
            print(f'Error: {e}')

    @staticmethod
    def bitbake_tool(file_path):
        try:
            bitbake_path = os.path.join(file_path, "poky", "build")
            bitbake_cmd = ["bitbake", "core-image-minimal"]
            
            if not os.path.exists(bitbake_path):
                print("Path not exists:", bitbake_path)
                print("Current Environment variable:", os.environ)
                return
            
            print("Command:", " ".join(bitbake_cmd))
            subprocess.run(bitbake_cmd, cwd=bitbake_path, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

# Call the starting method to initiate the build process
AutoBuild.package_installation()

