#!/usr/bin/env python3
import os
import subprocess

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f} {unit}{suffix}"
        bytes /= factor

def get_system_info():
    uname = os.uname()
    return {
        "System": uname.sysname,
        "Host Name": uname.nodename,
        "Kernel Version": uname.release,
        "Machine": uname.machine,
        "Processor": uname.version.split()[0],
    }

import subprocess

def get_cpu_info():
    # Get CPU information using the lscpu command
    result = subprocess.run(['lscpu'], capture_output=True, text=True)
    cpu_info = {}
    for line in result.stdout.splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            cpu_info[key.strip()] = value.strip()
    
    # Properly retrieve CPU frequency
    cpu_frequency_lscpu = cpu_info.get("CPU MHz", "N/A") + " MHz"
    
    # Alternatively, try to get frequency from /proc/cpuinfo
    try:
        cpuinfo_result = subprocess.run(['cat', '/proc/cpuinfo'], capture_output=True, text=True)
        cpu_frequency_proc = "N/A"
        for line in cpuinfo_result.stdout.splitlines():
            if line.startswith("cpu MHz"):
                cpu_frequency_proc = line.split(':', 1)[1].strip() + " MHz"
                break
    except Exception:
        cpu_frequency_proc = "N/A"
    
    # Optionally, check real-time frequency using cpufreq-info (if needed)
    try:
        cpufreq_result = subprocess.run(['cpufreq-info'], capture_output=True, text=True)
        cpu_frequency_cpufreq = "N/A"
        for line in cpufreq_result.stdout.splitlines():
            if line.startswith("current CPU frequency is"):
                cpu_frequency_cpufreq = line.split(':', 1)[1].strip()
                break
    except Exception:
        cpu_frequency_cpufreq = "N/A"
    
    # Get CPU usage percentage
    try:
        top_output = subprocess.run(['top', '-bn1'], capture_output=True, text=True)
        cpu_usage = "N/A"
        for line in top_output.stdout.splitlines():
            if line.startswith('%Cpu(s):'):
                cpu_usage = line.split(',')[0].split()[1]
                break
    except Exception:
        cpu_usage = "N/A"

    return {
        "Processor": cpu_info.get("Model name", "N/A"),
        "Core Count": cpu_info.get("Core(s) per socket", "N/A"),
        "Logical Processor Count": cpu_info.get("CPU(s)", "N/A"),
        "CPU Frequency (lscpu)": cpu_frequency_lscpu,
        "CPU Frequency (/proc/cpuinfo)": cpu_frequency_proc,
        "CPU Frequency (cpufreq-info)": cpu_frequency_cpufreq,
        "CPU Usage": cpu_usage + "%"  # CPU usage percentage
    }

# Test code (you can add this to the main function to ensure it works)


def get_memory_info():
    result = subprocess.run(['free', '-b'], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    memory_info = {}
    if len(lines) > 1:
        values = lines[1].split()
        memory_info["Total Memory"] = get_size(int(values[1]))
        memory_info["Used Memory"] = get_size(int(values[2]))
        memory_info["Free Memory"] = get_size(int(values[3]))

    if len(lines) > 2:
        swap_values = lines[2].split()
        memory_info["Swap Total"] = get_size(int(swap_values[1]))
        memory_info["Swap Used"] = get_size(int(swap_values[2]))
        memory_info["Swap Free"] = get_size(int(swap_values[3]))

    return memory_info

def get_disk_info():
    result = subprocess.run(['df', '-h'], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    disk_info = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 6:
            disk_info.append({
                "Device": parts[0],
                "Mount Point": parts[5],
                "Filesystem Type": parts[1],
                "Total Size": parts[2],
                "Used": parts[3],
                "Free": parts[4],
                "Usage Percentage": parts[4]  # Should be 'Usage Percentage' instead of 'Free'
            })
    return disk_info

def get_network_info():
    result = subprocess.run(['ip', '-s', 'a'], capture_output=True, text=True)
    network_info = []
    lines = result.stdout.splitlines()

    interface_info = {}
    for i, line in enumerate(lines):
        parts = line.split()
        if len(parts) > 1 and parts[1].endswith(':'):
            if interface_info:
                network_info.append(interface_info)
                interface_info = {}
            interface_info['Interface'] = parts[1][:-1]  # Remove ':'
        elif 'link/ether' in parts:
            interface_info['MAC Address'] = parts[1]
        elif 'mtu' in parts:
            interface_info['MTU'] = parts[1]
        elif 'inet' in parts:
            if 'scope global' in line:
                interface_info['IP Address'] = parts[1]
        elif 'inet6' in parts:
            if 'scope link' in line:
                interface_info['IPv6 Address'] = parts[1]
        elif 'RX:' in parts:
            if i + 1 < len(lines):
                rx_data = lines[i + 1].split()
                if len(rx_data) > 1:
                    interface_info['Received'] = get_size(int(rx_data[0].replace(':', '')))
                    interface_info['Transmitted'] = get_size(int(rx_data[1]))
        elif 'TX:' in parts:
            if i + 1 < len(lines):
                tx_data = lines[i + 1].split()
                if len(tx_data) > 1:
                    interface_info['Packets Sent'] = tx_data[0]
                    interface_info['Packets Received'] = tx_data[1]

    if interface_info:
        network_info.append(interface_info)
    
    return network_info

def get_gpu_info():
    result = subprocess.run(['lspci'], capture_output=True, text=True)
    gpu_info = []
    for line in result.stdout.splitlines():
        if 'VGA' in line or '3D' in line:
            gpu_info.append({
                "GPU": line
            })
    return gpu_info

def get_ip_info():
    try:
        result = subprocess.run(['ip', '-o', '-4', 'addr', 'list'], capture_output=True, text=True, check=True)
        ip_info = {}
        for line in result.stdout.splitlines():
            parts = line.split()
            interface = parts[1]
            ip_address = parts[3].split('/')[0]
            ip_info[interface] = ip_address
        return ip_info
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the command: {e}")
        return {}
    except FileNotFoundError as e:
        print(f"Command not found: {e}")
        return {}


def main():
    print(f"{'System Information':^40}")
    print("="*40)
    for k, v in get_system_info().items():
        print(f"{k:20}: {v}")

    print(f"\n{'CPU Information':^40}")
    print("="*40)
    for k, v in get_cpu_info().items():
        print(f"{k:20}: {v}")

    print(f"\n{'Memory Information':^40}")
    print("="*40)
    for k, v in get_memory_info().items():
        print(f"{k:20}: {v}")

    print(f"\n{'Disk Information':^40}")
    print("="*40)
    for disk in get_disk_info():
        for k, v in disk.items():
            print(f"{k:20}: {v}")
        print("-"*40)

    print(f"\n{'Network Information':^40}")
    print("="*40)
    for interface in get_network_info():
        print(f"Interface: {interface.get('Interface', 'N/A')}")
        print(f"MAC Address: {interface.get('MAC Address', 'N/A')}")
        print(f"MTU: {interface.get('MTU', 'N/A')}")
        print(f"IP Address: {interface.get('IP Address', 'N/A')}")
        print(f"IPv6 Address: {interface.get('IPv6 Address', 'N/A')}")
        print(f"Received: {interface.get('Received', 'N/A')}")
        print(f"Transmitted: {interface.get('Transmitted', 'N/A')}")
        print(f"Packets Sent: {interface.get('Packets Sent', 'N/A')}")
        print(f"Packets Received: {interface.get('Packets Received', 'N/A')}")
        print("-"*40)

    print(f"\n{'GPU Information':^40}")
    print("="*40)
    for gpu in get_gpu_info():
        print(f"{gpu['GPU']}")

    print(f"\n{'IP Information':^40}")
    print("="*40)
    for k, v in get_ip_info().items():
        print(f"{k:20}: {v}")

if __name__ == "__main__":
    main()
