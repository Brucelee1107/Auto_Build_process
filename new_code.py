# jai sree ram
import os
import yaml
import subprocess
import requests
import fileinput
import sys

class Auto_build:
    @staticmethod
    def is_installed_packages(package_name):
        try:
            subprocess.check_output(['dpkg','-l',package_name],stderr=subprocess.STDOUT)
            return True
        except subprocess.CalledProcessError as e:
            return False
    @staticmethod
    def package_installation():
        try:
            yaml_file_path = "https://raw.githubusercontent.com/Brucelee1107/Auto_Build_process/main/packages_to_install.yaml"
            response = requests.get(yaml_file_path)
            response.raise_for_status()
            yaml_content = response.text
            values = yaml.safe_load(yaml_content)

            packages_to_install = values.get('packages',[])
            packages_not_installed = []

            for package in packages_to_install:
                if not Auto_build.is_installed_packages(package):
                    packages_not_installed.append(package)
            if packages_not_installed:
                print("Installing missing packages...")
                for package in packages_not_installed:
                    command = ["sudo","apt","-y","install",package]
                    subprocess.run(command,check=True)
            else:
                print("All packages are already installed")
            package_generation = values['generation']
            for generate in package_generation:
                command = ['sudo',generate]
        except Exception as e:
            print(f'Error as {e}')
        Auto_build.creating_dir()
    @staticmethod
    def creating_dir():
        # creating new directory for build process
        current_dir = subprocess.run('pwd',stdout = subprocess.PIPE,text=True,shell=True).stdout.strip()
        # checks whether the path is already present or not before start building
        machine_name = str(sys.argv[1])
        if os.path.exists(current_dir + machine_name):
            file_path = current_dir + machine_name
            Auto_build.cloning_and_build_env(file_path,machine_name)
        else:
            file_path = os.path.join(current_dir,machine_name)
            os.makedirs(file_path)
            print(file_path)
            Auto_build.cloning_and_build_env(file_path,machine_name)
    @staticmethod
    def cloning_and_build_env(file_path,machine_name):
        try:
            # clone reference distribution poky
            os.chdir(file_path)
            #os.path.join(file_path,"poky")
            
            if os.path.exists(os.path.join(file_path,'poky')):
                print("poky already exists")
            else:
                git_clone_poky = ['git','clone','git://git.yoctoproject.org/poky']
                subprocess.run(git_clone_poky)
            # clone OE 
            os.chdir('poky')
            if os.path.exists(os.path.join(file_path,"poky","meta-openembedded")):
                print("OpenEmbedded already exists")
            else:
                git_clone_OE = ['git','clone','http://git.openembedded.org/meta-openembedded']
                subprocess.run(git_clone_OE)
            
            # clone specified target machine
            git_clone_target_machine = ['git','clone',f'https://git.yoctoproject.org/meta-{machine_name}']
            subprocess.run(git_clone_target_machine)
        except Exception as e:
            print(f'Error as {e}')
        build_path = file_path + "/poky"
        Auto_build.setup_yocto_environment(file_path,build_path,machine_name)
    @staticmethod
    def setup_yocto_environment(file_path,build_path,machine_name):
        init_env_script = os.path.join(file_path, 'poky', 'oe-init-build-env')
        source_command = f'source {init_env_script} {os.path.join(build_path, "build")}'
        env_script = f'echo "{source_command}" | /bin/bash'

        try:
            completed_process = subprocess.run(['/bin/bash', '-c', env_script],stdout=subprocess.PIPE,shell=False,executable='/bin/bash',env=os.environ,universal_newlines=True)

            if completed_process.returncode == 0:
                print("Yocto environment set up successfully.")
            else:
                print("Yocto environment setup failed.")
                print("Error:", completed_process.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Error as {e}")
        os.system("pwd")
        Auto_build.add_machine_layer(file_path,build_path,machine_name)
    @staticmethod
    def add_machine_layer(file_path,build_path,machine_name):
        target_machine_layer = build_path + f'/meta-{machine_name}'
        bblayers_path = file_path + '/poky/build/conf/bblayers.conf' 
        with open(bblayers_path,'r') as file:
            bblayers_content = file.readlines()
        for i,line in enumerate(bblayers_content):
            if line.startswith("BBLAYERS"):
                meta_oe_layer = '  '+ build_path + '/meta-openembedded/meta-oe' +' \\'+'\n'
                machine_layer = meta_oe_layer + '  '+ target_machine_layer +' \\' + '\n' +'\"'
                #bblayers_content[-1] = meta_oe_layer
                bblayers_content[-1] = machine_layer
                break
        with open(bblayers_path,'w') as file:
            file.writelines(bblayers_content)
        Auto_build.change_machine_name(file_path,machine_name)
    @staticmethod
    def change_machine_name(file_path,machine_name):
        local_conf_path = file_path + '/poky/build/conf/local.conf'
    
        with open(local_conf_path, 'r') as file:
            local_conf_content = file.readlines()

        for i, line in enumerate(local_conf_content):
            if line.startswith("MACHINE"):
                target_machine_name = machine_name
                local_conf_content[i] = 'MACHINE ?= "{}"\n'.format(target_machine_name)
                break

        with open(local_conf_path, 'w') as file:
            file.writelines(local_conf_content)
        
        Auto_build.bitbake_tool()
    @staticmethod
    def bitbake_tool():
        image = "core-image-sato"
        bitbake_cmd = f"bitbake {image}"
        try:
            os.system( bitbake_cmd)
        except Exception as e:
            print(f"Error as {e}")

Auto_build.package_installation()
