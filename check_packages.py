import subprocess
import requests
import yaml

def is_package_installed(package_name):
    try:
        # Run the command to check if the package is installed
        subprocess.check_output(['dpkg', '-l', package_name], stderr=subprocess.STDOUT)
        return True  # Package is installed
    except subprocess.CalledProcessError:
        return False  # Package is not installed

def package_installation():
    try:
        # packages install from the given path using yaml
        yaml_file_path = "https://raw.githubusercontent.com/Brucelee1107/Auto_Build_process/main/packages_to_install.yaml"
        response = requests.get(yaml_file_path)
        response.raise_for_status()
        yaml_content = response.text
        values = yaml.safe_load(yaml_content)
        
        packages_to_install = values.get('packages', [])
        packages_not_installed = []

        for package in packages_to_install:
            if not is_package_installed(package):
                packages_not_installed.append(package)
        
        if packages_not_installed:
            print("Packages not installed:", packages_not_installed)
            print("Installing missing packages...")
            for package in packages_not_installed:
                command = ['sudo', 'apt', 'install', '-y', package]
                subprocess.run(command, check=True)
        else:
            print("All packages are already installed.")
        
        package_generation = values.get('generation', [])
        for generate in package_generation:
            command = ['sudo', generate]
            subprocess.run(command, check=True)
        
        print("Packages installation completed.")
    except Exception as e:
        print(f'Error: {e}')

# Call the function to start the package installation process
package_installation()

