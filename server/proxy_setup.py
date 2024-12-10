"""
Aspen VPN 2024
Handles setting up and tearing down the server proxy.
"""

import subprocess

def process_commands(commands: list, check: bool = True):
    """Process a list of commands."""
    for command in commands:
        try:
            subprocess.run(command, check=check)
        except subprocess.CalledProcessError:
            print(f"Error executing command: {command}")
            break

def enable_ip_forwarding():
    """Enable IP forwarding on the server."""
    # Modify /etc/sysctl.conf to enable IP forwarding
    with open("/etc/sysctl.conf", "r") as file:
        sysctl_conf = file.readlines()

    with open("/etc/sysctl.conf", "w") as file:
        for line in sysctl_conf:
            if line.strip() == "#net.ipv4.ip_forward=1":
                file.write("net.ipv4.ip_forward=1\n")
            elif line.strip() == "net.ipv4.ip_forward=1":
                file.write("net.ipv4.ip_forward=1\n")
            else:
                file.write(line)

    # Apply the changes
    subprocess.run(["sudo", "sysctl", "-p"], check=True)
    print("IP forwarding enabled.")

def disable_ip_forwarding():
    """Disable IP forwarding on the server."""
    # Modify /etc/sysctl.conf to disable IP forwarding
    with open("/etc/sysctl.conf", "r") as file:
        sysctl_conf = file.readlines()

    with open("/etc/sysctl.conf", "w") as file:
        for line in sysctl_conf:
            if line.strip() == "net.ipv4.ip_forward=1":
                file.write("#net.ipv4.ip_forward=1\n")
            else:
                file.write(line)

    # Apply the changes
    subprocess.run(["sudo", "sysctl", "-p"], check=True)
    print("IP forwarding disabled.")

def configure_iptables(interface_name: str):
    """Configure IPTables for NAT and forwarding."""
    commands = [
        ["sudo", "iptables", "-t", "nat", "-A", "POSTROUTING", "-o", "eth0", "-j", "MASQUERADE"],
        ["sudo", "iptables", "-A", "FORWARD", "-i", interface_name, "-o", "eth0", "-m", "state", "--state", "RELATED,ESTABLISHED", "-j", "ACCEPT"],
        ["sudo", "iptables", "-A", "FORWARD", "-i", "eth0", "-o", interface_name, "-j", "ACCEPT"],
        ["sudo", "sh", "-c", "iptables-save > /etc/iptables/rules.v4"]
    ]
    # 0 - Set up IP masquerading
    # 1 - Allow forwarding from the VPN interface to eth0
    # 2 - Allow forwarding from eth0 to the VPN interface
    # 3 - Save the IPTables rules
    process_commands(commands)
    print("IPTables configured for NAT and forwarding.")

def clear_iptables(interface_name: str):
    """Clear IPTables rules for NAT and forwarding."""
    commands = [
        ["sudo", "iptables", "-t", "nat", "-D", "POSTROUTING", "-o", "eth0", "-j", "MASQUERADE"],
        ["sudo", "iptables", "-D", "FORWARD", "-i", interface_name, "-o", "eth0", "-m", "state", "--state", "RELATED,ESTABLISHED", "-j", "ACCEPT"],
        ["sudo", "iptables", "-D", "FORWARD", "-i", "eth0", "-o", interface_name, "-j", "ACCEPT"],
        ["sudo", "sh", "-c", "iptables-save > /etc/iptables/rules.v4"]
    ]
    # 0 - Remove IP masquerading
    # 1, 2 - Remove forwarding rules
    # 3 - Save the IPTables rules
    process_commands(commands)
    
    print("IPTables rules cleared.")

def setup_server_proxy(interface_name: str):
    """Automate server proxy setup."""
    enable_ip_forwarding()
    configure_iptables(interface_name)
    print("Server proxy setup completed.")

def disable_server_proxy(interface_name: str):
    """Automate server proxy remove."""
    disable_ip_forwarding()
    clear_iptables(interface_name)
    print("Server proxy remove completed.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Setup or remove server proxy.")
    parser.add_argument("action", choices=["setup", "remove"], help="Action to perform: setup or remove the server proxy.")
    parser.add_argument("--interface", default="wg1", help="Name of the VPN interface (default: wg1).")
    args = parser.parse_args()

    if args.action == "setup":
        setup_server_proxy(args.interface)
    elif args.action == "remove":
        disable_server_proxy(args.interface)