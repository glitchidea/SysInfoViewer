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
        "Sistem": uname.sysname,
        "Host Adı": uname.nodename,
        "Çekirdek Sürümü": uname.release,
        "Makine": uname.machine,
        "İşlemci": uname.version.split()[0],
    }


def get_cpu_info():
    # lscpu komutunu kullanarak CPU bilgilerini al
    result = subprocess.run(['lscpu'], capture_output=True, text=True)
    cpu_info = {}
    for line in result.stdout.splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            cpu_info[key.strip()] = value.strip()
    
    # CPU frekansını doğru biçimde almak için
    cpu_frequency_lscpu = cpu_info.get("CPU MHz", "N/A") + " MHz"
    
    # Alternatif olarak /proc/cpuinfo'dan da frekans almayı dene
    try:
        cpuinfo_result = subprocess.run(['cat', '/proc/cpuinfo'], capture_output=True, text=True)
        cpu_frequency_proc = "N/A"
        for line in cpuinfo_result.stdout.splitlines():
            if line.startswith("cpu MHz"):
                cpu_frequency_proc = line.split(':', 1)[1].strip() + " MHz"
                break
    except Exception:
        cpu_frequency_proc = "N/A"
    
    # Gerçek zamanlı frekansı kontrol etmek için cpufreq-info kullanımı (gerekirse)
    try:
        cpufreq_result = subprocess.run(['cpufreq-info'], capture_output=True, text=True)
        cpu_frequency_cpufreq = "N/A"
        for line in cpufreq_result.stdout.splitlines():
            if line.startswith("current CPU frequency is"):
                cpu_frequency_cpufreq = line.split(':', 1)[1].strip()
                break
    except Exception:
        cpu_frequency_cpufreq = "N/A"
    
    # CPU kullanım oranını al
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
        "İşlemci": cpu_info.get("Model name", "N/A"),
        "Çekirdek Sayısı": cpu_info.get("Core(s) per socket", "N/A"),
        "Mantıksal İşlemci Sayısı": cpu_info.get("CPU(s)", "N/A"),
        "CPU Frekansı (lscpu)": cpu_frequency_lscpu,
        "CPU Frekansı (/proc/cpuinfo)": cpu_frequency_proc,
        "CPU Frekansı (cpufreq-info)": cpu_frequency_cpufreq,
        "CPU Kullanımı": cpu_usage + "%"  # CPU kullanım oranı
    }

# Test kodu (bu kodun çalıştığından emin olmak için main fonksiyonuna ekleyebilirsiniz)


def get_memory_info():
    result = subprocess.run(['free', '-b'], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    memory_info = {}
    if len(lines) > 1:
        values = lines[1].split()
        memory_info["Toplam Bellek"] = get_size(int(values[1]))
        memory_info["Kullanılan Bellek"] = get_size(int(values[2]))
        memory_info["Boş Bellek"] = get_size(int(values[3]))

    if len(lines) > 2:
        swap_values = lines[2].split()
        memory_info["Swap Toplam"] = get_size(int(swap_values[1]))
        memory_info["Swap Kullanılan"] = get_size(int(swap_values[2]))
        memory_info["Swap Boş"] = get_size(int(swap_values[3]))

    return memory_info

def get_disk_info():
    result = subprocess.run(['df', '-h'], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    disk_info = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 6:
            disk_info.append({
                "Cihaz": parts[0],
                "Bağlantı Noktası": parts[5],
                "Dosya Sistemi Türü": parts[1],
                "Toplam Boyut": parts[2],
                "Kullanılan": parts[3],
                "Boş": parts[4],
                "Kullanım Yüzdesi": parts[4]  # 'Boş' yerine 'Kullanım Yüzdesi' olmalı
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
            interface_info['Arayüz'] = parts[1][:-1]  # ':' işaretini kaldır
        elif 'link/ether' in parts:
            interface_info['MAC Adresi'] = parts[1]
        elif 'mtu' in parts:
            interface_info['MTU'] = parts[1]
        elif 'inet' in parts:
            if 'scope global' in line:
                interface_info['IP Adresi'] = parts[1]
        elif 'inet6' in parts:
            if 'scope link' in line:
                interface_info['IPv6 Adresi'] = parts[1]
        elif 'RX:' in parts:
            if i + 1 < len(lines):
                rx_data = lines[i + 1].split()
                if len(rx_data) > 1:
                    interface_info['Gönderilen'] = get_size(int(rx_data[0].replace(':', '')))
                    interface_info['Alınan'] = get_size(int(rx_data[1]))
        elif 'TX:' in parts:
            if i + 1 < len(lines):
                tx_data = lines[i + 1].split()
                if len(tx_data) > 1:
                    interface_info['Paket Gönderilen'] = tx_data[0]
                    interface_info['Paket Alınan'] = tx_data[1]

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
        print(f"Komut çalıştırılırken bir hata oluştu: {e}")
        return {}
    except FileNotFoundError as e:
        print(f"Komut bulunamadı: {e}")
        return {}

def get_temperature_info():
    try:
        result = subprocess.run(['sensors'], capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else "Sıcaklık bilgisi alınamadı."
    except FileNotFoundError:
        return "sensors komutu bulunamadı. Kurmak için 'sudo apt-get install lm-sensors' komutunu kullanın."

def get_detailed_cpu_usage():
    try:
        result = subprocess.run(['mpstat', '-P', 'ALL', '1', '1'], capture_output=True, text=True)
        cpu_usage = {}
        for line in result.stdout.splitlines():
            if line.startswith("Average:"):
                parts = line.split()
                cpu_core = parts[2]
                usage = 100 - float(parts[-1])  # Son sütun "idle" (boşta) yüzdesidir, bu yüzden 100'den çıkarıyoruz
                cpu_usage[cpu_core] = f"{usage:.2f}%"
        return cpu_usage
    except FileNotFoundError:
        return {"Hata": "mpstat komutu bulunamadı. Kurmak için 'sudo apt-get install sysstat' komutunu kullanın."}

def main():
    print(f"{'Sistem Bilgileri':^40}")
    print("="*40)
    for k, v in get_system_info().items():
        print(f"{k:20}: {v}")
        
    print(f"\n{'GPU Bilgileri':^40}")
    print("="*40)
    for gpu in get_gpu_info():
        print(f"{gpu['GPU']}")

    print(f"\n{'CPU Bilgileri':^40}")
    print("="*40)
    for k, v in get_cpu_info().items():
        print(f"{k:20}: {v}")

    print(f"\n{'Detaylı CPU Kullanımı':^40}")
    print("="*40)
    for k, v in get_detailed_cpu_usage().items():
        print(f"Çekirdek {k:15}: {v}")

    print(f"\n{'Donanım Sıcaklıkları':^40}")
    print("="*40)
    print(get_temperature_info())

    print(f"\n{'Bellek Bilgileri':^40}")
    print("="*40)
    for k, v in get_memory_info().items():
        print(f"{k:20}: {v}")

    print(f"\n{'Ağ Bilgileri':^40}")
    print("="*40)
    for interface in get_network_info():
        print(f"Arayüz: {interface.get('Arayüz', 'N/A')}")
        print(f"MAC Adresi: {interface.get('MAC Adresi', 'N/A')}")
        print(f"MTU: {interface.get('MTU', 'N/A')}")
        print(f"IP Adresi: {interface.get('IP Adresi', 'N/A')}")
        print(f"IPv6 Adresi: {interface.get('IPv6 Adresi', 'N/A')}")
        print(f"Gönderilen: {interface.get('Gönderilen', 'N/A')}")
        print(f"Alınan: {interface.get('Alınan', 'N/A')}")
        print(f"Paket Gönderilen: {interface.get('Paket Gönderilen', 'N/A')}")
        print(f"Paket Alınan: {interface.get('Paket Alınan', 'N/A')}")
        print("-"*40)


    print(f"\n{'IP Bilgileri':^40}")
    print("="*40)
    for k, v in get_ip_info().items():
        print(f"Ağ Arayüzü: {k:15} IP Adresi: {v}")

    print(f"\n{'Disk Bilgileri':^40}")
    print("="*40)
    for disk in get_disk_info():
        for k, v in disk.items():
            print(f"{k:20}: {v}")
        print("-"*40)

if __name__ == "__main__":
    main()
