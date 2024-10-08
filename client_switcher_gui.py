import os
import requests
import re
import json
import tarfile
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
import tkinter as tk
from tkinter import filedialog, font

import redistribute_multifactor_distance

# Change to the home folder
os.chdir(os.path.expanduser("~"))

# Check sudo privileges
print("Checking sudo privileges")
try:
    subprocess.run(['sudo', '-v'], check=True)
    print("Sudo credentials authenticated.")
except subprocess.CalledProcessError:
    print("Failed to verify sudo credentials.")
    exit(1)

############# GUI CODE #######################

# Define a variable to store data
saved_data = []

def submit():
    eth_network = network_var.get()
    execution_client_delete = execution_delete_var.get()
    execution_client_install = execution_install_var.get()
    saved_data.extend([eth_network, execution_client_delete, execution_client_install])
    root.destroy()
    
    return eth_network, execution_client_delete, execution_client_install

root = tk.Tk()
root.title("Ethereum Client Switcher")
root.configure(background="#282C34")

network_var = tk.StringVar()
execution_delete_var = tk.StringVar()
execution_install_var = tk.StringVar()

label_font = font.nametofont("TkDefaultFont").copy()
label_font.config(size=20)

# Ethereum network selection
network_label = tk.Label(root, text="Ethereum network:", bg="#282C34", fg="#ABB2BF", font=label_font, anchor='e')
network_label.grid(column=0, row=0, padx=30, pady=30, sticky='e')

networks = ('Mainnet', 'Goerli', 'Sepolia', 'Holesky')
network_menu = tk.OptionMenu(root, network_var, *networks)
network_menu.config(bg="#4CAF50", fg="#FFFFFF", activebackground="#8BC34A", activeforeground="#FFFFFF", font=label_font, takefocus=True)
network_menu["menu"].config(bg="#4CAF50", fg="#FFFFFF", activebackground="#8BC34A", activeforeground="#FFFFFF", font=label_font)
network_menu.grid(column=1, row=0, padx=30, pady=30, ipadx=40, ipady=10)

# Execution client selection (to delete)
execution_delete_label = tk.Label(root, text="Execution Client to DELETE:", bg="#282C34", fg="#ABB2BF", font=label_font, anchor='e')
execution_delete_label.grid(column=0, row=1, padx=30, pady=30, sticky='e')

execution_clients = ('Nethermind', 'Besu', 'Geth', 'None')
execution_delete_menu = tk.OptionMenu(root, execution_delete_var, *execution_clients)
execution_delete_menu.config(bg="#2196F3", fg="#FFFFFF", activebackground="#64B5F6", activeforeground="#FFFFFF", font=label_font, takefocus=True)
execution_delete_menu["menu"].config(bg="#2196F3", fg="#FFFFFF", activebackground="#64B5F6", activeforeground="#FFFFFF", font=label_font)
execution_delete_menu.grid(column=1, row=1, padx=30, pady=30, ipadx=40, ipady=10)

# Recommendation
recommendation = redistribute_multifactor_distance.recommendation()
receommended_exe_client = str(recommendation[0]).upper()
receommended_con_client = str(recommendation[1]).upper()
recommendation_text = "Based on our recommendation algorithm, to improve the diversity of the Ethereum network we recommend " + receommended_exe_client + " for your Execution Client."
recommendation_text_2 = "Additionally, we recommend " + receommended_con_client + " for your Consensus Client."


    
recommended_label = tk.Label(
    root,
    text=recommendation_text+"\n"+recommendation_text_2,
    bg="#282C34",
    fg="#ABB2BF",
    font=label_font,
    anchor="center",
)
recommended_label.grid(column=0, row=2, columnspan=2, padx=30, pady=10)

# Execution client selection (to install)
execution_install_label = tk.Label(root, text="Execution Client to INSTALL:", bg="#282C34", fg="#ABB2BF", font=label_font, anchor='e')
execution_install_label.grid(column=0, row=3, padx=30, pady=30, sticky='e')

execution_install_menu = tk.OptionMenu(root, execution_install_var, *execution_clients)
execution_install_menu.config(bg="#FF9800", fg="#FFFFFF", activebackground="#FFA726", activeforeground="#FFFFFF", font=label_font, takefocus=True)
execution_install_menu["menu"].config(bg="#FF9800", fg="#FFFFFF", activebackground="#FFA726", activeforeground="#FFFFFF", font=label_font)
execution_install_menu.grid(column=1, row=3, padx=30, pady=30, ipadx=40, ipady=10)

# Submit button
submit_button = tk.Button(root, text="Install", command=submit, bg="#282C34", fg="#ABB2BF", activebackground="#61AFEF", activeforeground="#282C34", font=label_font, takefocus=True)
submit_button.grid(column=1, row=4, padx=30, pady=60)

root.mainloop()

eth_network, execution_client_delete, execution_client_install = saved_data

# Define User Input Variables
eth_network = saved_data[0]
execution_client_delete = saved_data[1]
execution_client_install = saved_data[2]

# Print User Input Variables
print("\n##### User Selected Inputs #####")
print(f"Ethereum Network: {eth_network}")
print(f"Execution Client to DELETE: {execution_client_delete}")
print(f"Execution Client to INSTALL: {execution_client_install}\n")

######## VALIDATE USER INPUTS #########################

# Define valid execution clients and networks in uppercase
valid_clients = ['GETH', 'BESU', 'NETHERMIND', 'ERIGON' 'NONE']
valid_networks = ['MAINNET', 'GOERLI', 'SEPOLIA', 'HOLESKY']

# Convert user inputs to uppercase
eth_network = eth_network.upper()
execution_client_delete = execution_client_delete.upper()
execution_client_install = execution_client_install.upper()

# Validate user inputs
if eth_network not in valid_networks:
    raise ValueError(f"Invalid Ethereum Network: {eth_network}")

if execution_client_delete not in valid_clients:
    raise ValueError(f"Invalid Execution Client to DELETE: {execution_client_delete}")

if execution_client_install not in valid_clients:
    raise ValueError(f"Invalid Execution Client to INSTALL: {execution_client_install}")

# Convert validated inputs to lowercase
eth_network = eth_network.lower()
execution_client_delete = execution_client_delete.lower()
execution_client_install = execution_client_install.lower()

# Print validated inputs
print("##### Validated User Inputs #####")
print(f"Ethereum Network: {eth_network}")
print(f"Execution Client to DELETE: {execution_client_delete}")
print(f"Execution Client to INSTALL: {execution_client_install}\n")

######### REMOVE OLD CLIENT ###################
# Removal commands for different clients
geth_cmds = [
    "sudo systemctl stop geth",
    "sudo rm -rf /usr/local/bin/geth",
    "sudo rm -rf /var/lib/geth",
    "sudo rm -rf /etc/systemd/system/geth.service",
    "sudo userdel -r geth || true",
]

besu_cmds = [
    "sudo systemctl stop besu",
    "sudo rm -rf /usr/local/bin/besu",
    "sudo rm -rf /var/lib/besu",
    "sudo rm -rf /etc/systemd/system/besu.service",
    "sudo userdel -r besu || true",
]

nethermind_cmds = [
    "sudo systemctl stop nethermind",
    "sudo rm -rf /usr/local/bin/nethermind",
    "sudo rm -rf /var/lib/nethermind",
    "sudo rm -rf /etc/systemd/system/nethermind.service",
    "sudo userdel -r nethermind || true",
]

# Execute removal commands for execution_client_delete
print(f"Removing execution client: {execution_client_delete}")

if execution_client_delete == 'geth':
    for cmd in geth_cmds:
        print(cmd)
        subprocess.run(cmd, shell=True, check=False)

elif execution_client_delete == 'besu':
    for cmd in besu_cmds:
        print(cmd)
        subprocess.run(cmd, shell=True, check=False)

elif execution_client_delete == 'nethermind':
    for cmd in nethermind_cmds:
        print(cmd)
        subprocess.run(cmd, shell=True, check=False)

elif execution_client_delete == 'none':
    print("No client selected for deletion")
    
# Update and upgrade packages
subprocess.run(['sudo', 'apt', '-y', 'update'])
subprocess.run(['sudo', 'apt', '-y', 'upgrade'])

# Install New Client
print(f"\nInstalling execution client: {execution_client_install}\n")
print(f"Creating usernames, directories, and serfice files...\n")
print(execution_client_install.lower()) 

############ GETH INSTALL##################
if execution_client_install == 'geth':
    # Create User and directories
    subprocess.run(['sudo', 'useradd', '--no-create-home', '--shell', '/bin/false', 'geth'])
    subprocess.run(['sudo', 'mkdir', '-p', '/var/lib/geth'])
    subprocess.run(['sudo', 'chown', '-R', 'geth:geth', '/var/lib/geth'])

    # Define the URL of the Geth download page
    url = 'https://geth.ethereum.org/downloads/'

    # Send a GET request to the download page and retrieve the HTML response
    response = requests.get(url)
    html = response.text

    # Use regex to extract the URL of the latest Geth binary for Linux (amd64)
    match = re.search(r'href="(https://gethstore\.blob\.core\.windows\.net/builds/geth-linux-amd64-[0-9]+\.[0-9]+\.[0-9]+-[0-9a-f]+\.tar\.gz)"', html)
    if match:
        download_url = match.group(1)
        filename = os.path.expanduser('~/geth.tar.gz')
        print(f'Downloading {download_url}...')
        response = requests.get(download_url)
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f'Done! Binary saved to {filename}.')

        # Extract the contents of the tarball to the user's home folder
        with tarfile.open(filename, 'r:gz') as tar:
            dirname = tar.getnames()[0].split('/')[0]
            tar.extractall(os.path.expanduser('~'))

        # Remove the existing geth executable from /usr/local/bin if it exists
        if os.path.exists('/usr/local/bin/geth'):
            subprocess.run(['sudo', 'rm', '/usr/local/bin/geth'])
            print('Existing geth executable removed from /usr/local/bin.')

        # Copy the geth executable to /usr/local/bin
        src = os.path.expanduser(f'~/{dirname}/geth')
        subprocess.run(['sudo', 'cp', src, '/usr/local/bin/'])
        print('Geth executable copied to /usr/local/bin.')

        # Remove the downloaded file and extracted directory
        os.remove(filename)
        shutil.rmtree(os.path.expanduser(f'~/{dirname}'))
        print(f'Removed {filename} and directory {dirname}.')
    else:
        print('Error: could not find download URL.')

############ BESU INSTALL##################
if execution_client_install == 'besu':
	# Create User and directories
	subprocess.run(['sudo', 'useradd', '--no-create-home', '--shell', '/bin/false', 'besu'])
	subprocess.run(['sudo', 'mkdir', '-p', '/var/lib/besu'])
	subprocess.run(['sudo', 'chown', '-R', 'besu:besu', '/var/lib/besu'])

	# Get the latest version number
	url = "https://api.github.com/repos/hyperledger/besu/releases/latest"
	response = urllib.request.urlopen(url)
	data = json.loads(response.read().decode("utf-8"))
	latest_version = data['tag_name']

	besu_version = latest_version

	# Download the latest version
	download_url = f"https://hyperledger.jfrog.io/hyperledger/besu-binaries/besu/{latest_version}/besu-{latest_version}.tar.gz"
	urllib.request.urlretrieve(download_url, f"besu-{latest_version}.tar.gz")

	# Extract the tar.gz file
	with tarfile.open(f"besu-{latest_version}.tar.gz", "r:gz") as tar:
	    tar.extractall()

if execution_client_install == 'besu':
	# Copy the extracted besu folder to /usr/local/bin/besu
	subprocess.run(["sudo", "cp", "-a", f"besu-{latest_version}", "/usr/local/bin/besu"], check=True)

	# Remove the downloaded .tar.gz file
	os.remove(f"besu-{latest_version}.tar.gz")

	# Install OpenJDK-17-JRE
	subprocess.run(["sudo", "apt", "-y", "install", "openjdk-17-jre"])

	# Install libjemalloc-dev
	subprocess.run(["sudo", "apt", "install", "-y", "libjemalloc-dev"])

############ NETHERMIND INSTALL##################
if execution_client_install == 'nethermind':
    # Create User and directories
    subprocess.run(["sudo", "useradd", "--no-create-home", "--shell", "/bin/false", "nethermind"])
    subprocess.run(["sudo", "mkdir", "-p", "/var/lib/nethermind"])
    subprocess.run(["sudo", "chown", "-R", "nethermind:nethermind", "/var/lib/nethermind"])
    subprocess.run(["sudo", "apt-get", "install", "libsnappy-dev", "libc6-dev", "libc6", "unzip", "-y"], check=True)

    # Define the Github API endpoint to get the latest release
    url = 'https://api.github.com/repos/NethermindEth/nethermind/releases/latest'

    # Send a GET request to the API endpoint
    response = requests.get(url)

    # Search for the asset with the name that ends in linux-x64.zip
    assets = response.json()['assets']
    download_url = None
    zip_filename = None
    for asset in assets:
        if asset['name'].endswith('linux-x64.zip'):
            download_url = asset['browser_download_url']
            zip_filename = asset['name']
            break

    if download_url is None or zip_filename is None:
        print("Error: Could not find the download URL for the latest release.")
        exit(1)

    # Download the latest release binary
    response = requests.get(download_url)

    # Save the binary to a temporary file
    with tempfile.NamedTemporaryFile('wb', suffix='.zip', delete=False) as temp_file:
        temp_file.write(response.content)
        temp_path = temp_file.name

    # Create a temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract the binary to the temporary directory
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Copy the contents of the temporary directory to /usr/local/bin/nethermind using sudo
        subprocess.run(["sudo", "cp", "-a", f"{temp_dir}/.", "/usr/local/bin/nethermind"])

    # chown nethermind:nethermind /usr/local/bin/nethermind
    subprocess.run(["sudo", "chown", "nethermind:nethermind", "/usr/local/bin/nethermind"])

    # chown nethermind:nethermind /usr/local/bin/nethermind/nethermind
    subprocess.run(["sudo", "chown", "nethermind:nethermind", "/usr/local/bin/nethermind/nethermind"])

    # chmod a+x /usr/local/bin/nethermind/nethermind
    subprocess.run(["sudo", "chmod", "a+x", "/usr/local/bin/nethermind/nethermind"])

    # Remove the temporary zip file
    os.remove(temp_path)

    nethermind_version = os.path.splitext(zip_filename)[0]  

###### ERIGON INSTALL ################
if execution_client_install == 'erigon':
    # Create User and directories (assuming not already created)
    try:
        subprocess.run(["sudo", "useradd", "--no-create-home", "--shell", "/bin/false", "erigon"], check=True)
        subprocess.run(["sudo", "mkdir", "-p", "/var/lib/erigon"], check=True)
        subprocess.run(["sudo", "chown", "-R", "erigon:erigon", "/var/lib/erigon"], check=True)
    except:
        print("User already added")
        

    # Define the Github API endpoint to get the latest release
    url = 'https://api.github.com/repos/ledgerwatch/erigon/releases/latest'

    # Send a GET request to the API endpoint
    response = requests.get(url)

    # Search for the asset with the name that ends in linux-x64.tar.gz
    assets = response.json()['assets']
    download_url = None
    archive_filename = None
    for asset in assets:
        if asset['name'].endswith('linux_amd64.tar.gz'):
            download_url = asset['browser_download_url']
            archive_filename = asset['name']
            break

    if download_url is None or archive_filename is None:
        print("Error: Could not find the download URL for the latest release.")
        exit(1)

    # Download the latest release archive
    response = requests.get(download_url)

    # Save the archive to a temporary file
    with tempfile.NamedTemporaryFile('wb', suffix='.tar.gz', delete=False) as temp_file:
        temp_file.write(response.content)
        temp_path = temp_file.name

    # Create a temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract the archive to the temporary directory
        with tarfile.open(temp_path, 'r:gz') as tar_ref:
            tar_ref.extractall(temp_dir)

        # Move the extracted Erigon binary to /usr/local/bin/erigon with sudo (assuming it's named erigon)
        subprocess.run(["sudo", "mv", f"{temp_dir}/erigon", "/usr/local/bin/erigon"], check=True)

    # chown erigon:erigon /usr/local/bin/erigon
    subprocess.run(["sudo", "chown", "erigon:erigon", "/usr/local/bin/erigon"], check=True)

    # chmod a+x /usr/local/bin/erigon
    subprocess.run(["sudo", "chmod", "a+x", "/usr/local/bin/erigon"], check=True)

    # Remove the temporary archive file
    os.remove(temp_path)  
 
###### GETH SERVICE FILE #############
if execution_client_install == 'geth':
    geth_service_file_lines = [
        '[Unit]',
        'Description=Geth Execution Client (Mainnet)',
        'Wants=network.target',
        'After=network.target',
        '',
        '[Service]',
        'User=geth',
        'Group=geth',
        'Type=simple',
        'Restart=always',
        'RestartSec=5',
        'TimeoutStopSec=600',
        'ExecStart=/usr/local/bin/geth \\',
        f'    --{eth_network} \\',
        '    --datadir /var/lib/geth \\',
        '    --authrpc.jwtsecret /var/lib/jwtsecret/jwt.hex',
        '',
        '[Install]',
        'WantedBy=default.target',
    ]

    geth_service_file = '\n'.join(geth_service_file_lines)

    geth_temp_file = 'geth_temp.service'
    geth_service_file_path = '/etc/systemd/system/geth.service'

    with open(geth_temp_file, 'w') as f:
        f.write(geth_service_file)

    os.system(f'sudo cp {geth_temp_file} {geth_service_file_path}')
    os.remove(geth_temp_file)

############ BESU SERVICE FILE ###############
if execution_client_install == 'besu':
    besu_service_file_lines = [
        '[Unit]',
        'Description=Besu Execution Client (Mainnet)',
        'Wants=network-online.target',
        'After=network-online.target',
        '',
        '[Service]',
        'User=besu',
        'Group=besu',
        'Type=simple',
        'Restart=always',
        'RestartSec=5',
        'Environment="JAVA_OPTS=-Xmx5g"',
        'ExecStart=/usr/local/bin/besu/bin/besu \\',
        f'    --network={eth_network} \\',
        '    --sync-mode=X_SNAP \\',
        '    --data-path=/var/lib/besu \\',
        '    --data-storage-format=BONSAI \\',
        '    --engine-jwt-secret=/var/lib/jwtsecret/jwt.hex',
        '',
        '[Install]',
        'WantedBy=multi-user.target',
    ]

    besu_service_file = '\n'.join(besu_service_file_lines)

    besu_temp_file = 'besu_temp.service'
    besu_service_file_path = '/etc/systemd/system/besu.service'

    with open(besu_temp_file, 'w') as f:
        f.write(besu_service_file)

    os.system(f'sudo cp {besu_temp_file} {besu_service_file_path}')
    os.remove(besu_temp_file)

####### NETHERMIND SERVICE FILE ###########
if execution_client_install == 'nethermind':
    nethermind_service_file_lines = [
        '[Unit]',
        'Description=Nethermind Execution Client (Mainnet)',
        'Wants=network.target',
        'After=network.target',
        '',
        '[Service]',
        'User=nethermind',
        'Group=nethermind',
        'Type=simple',
        'Restart=always',
        'RestartSec=5',
        'WorkingDirectory=/var/lib/nethermind',
        'Environment="DOTNET_BUNDLE_EXTRACT_BASE_DIR=/var/lib/nethermind"',
        'ExecStart=/usr/local/bin/nethermind/nethermind \\',
        f'    --config {eth_network.lower()} \\',
        '    --datadir /var/lib/nethermind \\',
        '    --Sync.SnapSync true \\',
        '    --Sync.AncientBodiesBarrier 11052984 \\',
        '    --Sync.AncientReceiptsBarrier 11052984 \\',
        '    --JsonRpc.JwtSecretFile /var/lib/jwtsecret/jwt.hex',
        '',
        '[Install]',
        'WantedBy=default.target',
    ]

    nethermind_service_file = '\n'.join(nethermind_service_file_lines)

    nethermind_temp_file = 'nethermind_temp.service'
    nethermind_service_file_path = '/etc/systemd/system/nethermind.service'

    with open(nethermind_temp_file, 'w') as f:
        f.write(nethermind_service_file)

    os.system(f'sudo cp {nethermind_temp_file} {nethermind_service_file_path}')

    os.remove(nethermind_temp_file)

##### ERIGON SERVICE FILE ######
if execution_client_install == 'erigon':
    erigon_service_file_lines = [
        '[Unit]',
        'Description=Erigon Execution Client (Mainnet)',
        'Wants=network.target',
        'After=network.target',
        '',
        '[Service]',
        'User=erigon',
        'Group=erigon',
        'Type=simple',
        'Restart=always',
        'RestartSec=5',
        'WorkingDirectory=/var/lib/erigon',
        'Environment="DOTNET_BUNDLE_EXTRACT_BASE_DIR=/var/lib/erigon"',
        'ExecStart=/usr/local/bin/erigon/erigon \\',
        f'    --config {eth_network.lower()} \\',
        '    --datadir /var/lib/erigon \\',
        '    --Sync.SnapSync true \\',
        '    --JsonRpc.JwtSecretFile /var/lib/jwtsecret/jwt.hex',
        '',
        '[Install]',
        'WantedBy=default.target',
    ]

    erigon_service_file = '\n'.join(erigon_service_file_lines)

    erigon_temp_file = 'erigon_temp.service'
    erigon_service_file_path = '/etc/systemd/system/erigon.service'

    with open(erigon_temp_file, 'w') as f:
        f.write(erigon_service_file)

    os.system(f'sudo cp {erigon_temp_file} {erigon_service_file_path}')

    os.remove(erigon_temp_file)

#### END SERVICE FILES #####

# Reload system daemon
subprocess.run(f"sudo systemctl daemon-reload", shell=True, check=False)

############ PRINT FINAL OUTPUT ###############
print("\n########### CLIENT SWTICH DETAILS #############\n")

print(f'Removed: {execution_client_delete.upper()}\n')
print(f'Installed: {execution_client_install.upper()}\n')

# Check & Print Installed Versions
if execution_client_install == 'geth':
    geth_version = subprocess.run(["geth", "--version"], stdout=subprocess.PIPE).stdout
    if geth_version is not None:
        geth_version = geth_version.decode()
        geth_version = geth_version.split(" ")[-1].strip()
    else:
        geth_version = ""
    print(f'Geth Version: v{geth_version}\n')

if execution_client_install == 'besu':
    print(f'Besu Version: v{besu_version}\n')
    
if execution_client_install == 'nethermind':
    print(f'Nethermind Version: \n{nethermind_version}\n')

print(f"Client switch complete, you can start {execution_client_install.upper()} to begin syncing!\n")
