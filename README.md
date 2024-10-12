# SysInfoViewer

**SysInfoViewer** is an effective command-line tool that provides detailed insights into your system's hardware and performance. It equips you with all the information you need to manage your computer optimally and monitor the status of your hardware components.

## Features

- **Hardware Information**: Displays detailed information about CPU, RAM, disk, and GPU.
- **Network Status**: Provides information about your network interfaces, including IP addresses, MAC addresses, and connection status.
- **Usage Metrics**: Allows you to monitor RAM, disk, and CPU usage percentages to assess system health.
- **User-Friendly Interface**: Offers easy-to-understand access to information.

## Getting Started

### Requirements

- Python 3.x must be installed.
- The `subprocess` and `os` libraries are required (included with Python).

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/glitchidea/SysInfoViewer.git
   cd SysInfoViewer
   ```

2. Run the application:
   ```bash
   python sys_info_viewer.py
   ```

## Usage

1. **Launch the Application**: Run the command above to open the CLI interface.
2. **View Information**: The program will instantly display your system information.
3. **Check Details**: Each section provides detailed information, allowing you to quickly assess your system's status.

## Sample Output

When the program runs, you will see information displayed as follows:

```
           System Information           
========================================
System           : Linux
Host Name        : yourhostname
Kernel Version   : 5.4.0-42-generic
Machine          : x86_64
Processor        : x86_64

           CPU Information               
========================================
Processor        : Intel(R) Core(TM) i7-8565U CPU @ 1.80GHz
Core Count       : 4
Logical Processor Count : 8
CPU Frequency (lscpu) : 1800.00 MHz
CPU Usage        : 12.5%
```

## Additional Features

- **No Data Entry Required**: Automatically collects all information without requiring additional user input.
- **Fast Performance**: Provides information quickly without slowing down the system.
- **Compatibility**: Compatible with Linux-based operating systems.

## Developer Notes

- You can contribute to the development of this application and suggest new features.
- For bug reports and suggestions, please use the GitHub Issues section.
