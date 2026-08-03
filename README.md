# Adaptive CLI System Health & Diagnostics Tool

A cross-platform, menu-driven command-line application in Python designed to perform real-time system diagnostics, monitor system health metrics, evaluate adaptive recommendations, export health reports, and execute safe maintenance tasks across **Windows**, **Linux**, and **macOS**.

Built using **100% Pure Standard Python 3** with zero third-party pip dependencies.

---

## 📋 Features Overview

- **💻 System Information**: View operating system specifications, kernel version, architecture, CPU model, total RAM, disk space, system uptime, and primary IP address.
- **⚡ Live Resource Monitor**: Real-time terminal resource dashboard monitoring CPU load, RAM utilization, max partition disk usage, network status, and ping latency.
- **⚙️ Process Manager**: Enumerate active processes, sort by CPU/RAM/PID, and perform process termination (`kill`).
- **💾 Disk & Storage Analysis**: Partition statistics, temporary files scan, Downloads folder analysis, and deep large directory detection (>500 MB).
- **🌐 Network Diagnostics & Bitwise Subnet Calculation**: Public host connectivity ping checks, DNS resolution validation, active interface checks, open port scanner, and IPv4 subnet calculations using bitwise operators.
- **🛠️ Service Manager**: Inspect system services across platform managers (**Windows Services**, **systemd**, **launchd**).
- **📜 Log Inspector**: Inspect recent system event logs (Windows Event Logs, systemd journal, macOS logs).
- **🩺 System Diagnostics & Health Scoring**: Comprehensive diagnostic engine calculating a system health score (0–100) and cataloging severity issues.
- **🧠 Adaptive Recommendation Engine**: Rule-based expert system (`configs/rules.json`) evaluating metric thresholds to suggest actionable system optimizations.
- **📄 Multi-Format Report Generator**: Export health reports to **TXT**, **JSON**, or interactive responsive **HTML** dashboards with CSS styling.
- **🔧 Configuration Assistant**: Safe maintenance tasks with confirmation prompts (Flush DNS, Clear Temporary Files, Restart Network Adapters, Change Hostname, Cleanup Package Manager Caches).

---

## 📚 Technical Concepts Demonstrated

This project explicitly demonstrates core Python concepts:

| Concept | Implementation Details |
| :--- | :--- |
| **Command Line Execution** | Executed directly via `python main.py` or subcommands. |
| **Control Flow Structures** | `if/elif/else` conditional logic, `while True` main loop, `for` iteration in [cli.py](file:///c:/Users/shubh/Desktop/cli%20system%20diagnosis/cli.py). |
| **Relational Operators** | `>=`, `<`, `==`, `!=`, `<=`, `>` used across health scoring and threshold evaluation in [modules/diagnostics.py](file:///c:/Users/shubh/Desktop/cli%20system%20diagnosis/modules/diagnostics.py). |
| **Logical Operators** | `and`, `or`, `not` used for multi-condition network and storage checks. |
| **Bitwise Operators** | `<<`, `>>`, `&`, `|`, `~` used for IPv4 integer conversions, subnet mask calculation, and bitwise status flag validation in [modules/network.py](file:///c:/Users/shubh/Desktop/cli%20system%20diagnosis/modules/network.py). |
| **Simple Input & Output** | Interactive menu driven by built-in `input()` and custom ASCII table formatting via `print()`. |
| **Numeric & String Conversions** | `int()`, `float()`, `str()`, `.strip()`, `.split()`, `.upper()`, and f-strings. |
| **Python for Windows** | Win32 kernel32 API calls via `ctypes` (`GlobalMemoryStatusEx`, `IsUserAnAdmin`), PowerShell commands, and Windows system utilities in [platforms/windows.py](file:///c:/Users/shubh/Desktop/cli%20system%20diagnosis/platforms/windows.py). |
| **Built-in Unittest Framework** | Unit testing using Python standard library `unittest` runner. |

---

## 📂 Project Architecture

```
cli system diagnosis/
├── main.py                     # Program entrypoint launching interactive menu
├── cli.py                      # Interactive menu-driven CLI (Pure stdlib)
├── requirements.txt            # Project indicator file (Zero dependencies)
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore configuration
├── configs/
│   └── rules.json              # Configurable recommendation rules
├── core/
│   ├── models.py               # Pure Python dataclasses
│   ├── detector.py             # OS platform detection factory
│   └── manager.py              # System diagnostics manager
├── platforms/
│   ├── base.py                 # Abstract Base Class PlatformAdapter
│   ├── common.py               # Subprocess helpers & temp locators
│   ├── windows.py              # Windows Win32 API ctypes & PowerShell adapter
│   ├── linux.py                # Linux /proc & systemctl adapter
│   └── macos.py                # macOS sysctl & launchctl adapter
├── modules/
│   ├── system_info.py          # Hardware & OS information
│   ├── cpu.py                  # CPU metrics
│   ├── memory.py               # Memory metrics
│   ├── disk.py                 # Disk metrics & folder analysis
│   ├── network.py              # Network checks, bitwise calculations & port scanner
│   ├── process.py              # Process manager & process control
│   ├── services.py             # Service manager wrapper
│   ├── logs.py                 # Log analyzer wrapper
│   ├── diagnostics.py          # Health score calculator & issue engine
│   ├── recommendations.py      # Adaptive rules engine
│   ├── report.py               # Report generator (TXT, JSON, HTML)
│   └── config_assistant.py     # Safe configuration maintenance tasks
├── reports/                    # Output directory for exported health reports
└── tests/                      # Built-in unittest testing suite
    ├── test_system_info.py
    ├── test_detector_and_platforms.py
    ├── test_modules.py
    ├── test_recommendations.py
    ├── test_report.py
    └── test_cli.py
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+** (No external `pip` packages required).

### Installation & Running
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/cli-system-diagnosis.git
   cd cli-system-diagnosis
   ```
2. Run the application:
   ```bash
   python main.py
   ```

---

## 🎮 Interactive Menu Interface

```
===========================================================================
               ADAPTIVE CLI SYSTEM HEALTH & DIAGNOSTICS TOOL               
===========================================================================
  1. System Information Overview
  2. Live Resource Monitor
  3. Process Manager (List & Control Processes)
  4. Disk & Storage Analysis
  5. Network Diagnostics & Open Port Scanner
  6. System Service Manager
  7. System Log Inspector
  8. Run Full System Health Diagnostics
  9. View Adaptive Recommendations
 10. Export System Health Report (TXT / JSON / HTML)
 11. Safe Configuration & Maintenance Assistant
  0. Exit Application
===========================================================================

Select an option [0-11]:
```

---

## 🧪 Running Unit Tests

Run the test suite using Python's built-in `unittest` runner:

```bash
python -m unittest discover tests
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.


