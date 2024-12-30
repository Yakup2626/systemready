import psutil
import time
import subprocess

# Funktion zum Überwachen der Systemleistung
def monitor_system_performance():
    # CPU-Auslastung (im Prozent)
    cpu_usage = psutil.cpu_percent(interval=1)
    
    # RAM-Auslastung
    memory = psutil.virtual_memory()
    memory_usage = memory.percent  # Prozentuale Auslastung des RAMs

    # Weitere Parameter (z.B. Disk) könnten hier hinzugefügt werden

    print(f"CPU-Auslastung: {cpu_usage}%")
    print(f"RAM-Auslastung: {memory_usage}%")
    
    # Anpassung der Pausen je nach Systemleistung
    if cpu_usage > 85 or memory_usage > 85:
        # Bei hoher Auslastung größere Pausen einbauen
        return 3  # 3 Sekunden Pause
    elif cpu_usage > 50 or memory_usage > 50:
        # Bei mittlerer Auslastung eine normale Pause einbauen
        return 1  # 1 Sekunde Pause
    else:
        # Bei niedriger Auslastung keine Pausen
        return 0.2  # 0.2 Sekunden Pause (kleine Verzögerung)

# Funktion zum Installieren von APT-Paketen
def install_apt(package):
    try:
        print(f"Installiere {package} mit APT...")
        result = subprocess.run(f"sudo apt install {package} -y -f", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"Fehler bei der Installation von {package}: {result.stderr.decode()}")
    except Exception as e:
        print(f"Fehler bei der Installation von {package}: {str(e)}")

# Funktion zum Installieren von DEB-Paketen über dpkg
def install_dpkg(file_url):
    try:
        print(f"Herunterladen und installieren von {file_url} mit dpkg...")
        file_name = file_url.split('/')[-1]
        subprocess.call(f"sudo wget {file_url} -O {file_name}", shell=True)
        subprocess.call(f"sudo dpkg -i {file_name}", shell=True)
        subprocess.call(f"sudo apt install -f -y", shell=True)  # Korrigiert fehlende Abhängigkeiten
    except Exception as e:
        print(f"Fehler bei der Installation von {file_url}: {str(e)}")

# Funktion zur Überprüfung, ob Software bereits installiert ist
def is_installed(package):
    result = subprocess.run(f"dpkg -l | grep {package}", shell=True, stdout=subprocess.PIPE)
    return result.returncode == 0

# Log-Datei erstellen
def log_action(message):
    with open("install_log.txt", "a") as log_file:
        log_file.write(f"{message}\n")

# Hauptfunktion zum Durchgehen der Tools
def main():
    print("System vorbereiten...")
    subprocess.call("sudo dpkg --configure -a", shell=True)

    # Log-Datei erstellen
    log_action("Systemvorbereitung gestartet.")
    
    software_list = []
    dpkg_list = []

    print("Willkommen beim Tool-Installer!\n")

    # Tools fragen
    tools = {
        "Chrome": "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb",  # Chrome über wget installieren
        "Rustdesk": "https://github.com/rustdesk/rustdesk/releases/download/1.3.6/rustdesk-1.3.6-x86_64.deb",  # Rustdesk über wget installieren
        "Openssh": "openssh-server",
    }

    for tool, package in tools.items():
        answer = input(f"Möchtest du {tool} installieren? (Y/N): ").strip().lower()
        if answer == "y":
            if package.startswith("http"):  # Wenn es sich um eine URL handelt, wird es später mit dpkg installiert
                dpkg_list.append(package)
            else:  # Ansonsten wird es als APT-Paket behandelt
                if not is_installed(tool):
                    software_list.append(package)
                else:
                    print(f"{tool} ist bereits installiert.")
                    log_action(f"{tool} wurde übersprungen, da es bereits installiert ist.")

    # Benutzerdefinierten Bereich
    custom_answer = input("Möchtest du benutzerdefinierte Software hinzufügen? (Y/N): ").strip().lower()
    while custom_answer == "y":
        software_name = input("Bitte gib den Namen der Software ein, die du installieren möchtest:\nSoftwarename: ")
        if not is_installed(software_name):
            software_list.append(software_name)
        custom_answer = input("Möchtest du noch eine benutzerdefinierte Software hinzufügen? (Y/N): ").strip().lower()

    # Installation der Software mit Pausen basierend auf der Systemleistung
    print("\nInstallation der ausgewählten Software...")
    for software in software_list:
        install_apt(software)
        # Überwache die Systemleistung und passe die Pause entsprechend an
        pause_time = monitor_system_performance()
        print(f"Pause von {pause_time} Sekunden...")
        time.sleep(pause_time)

    for file_url in dpkg_list:
        install_dpkg(file_url)
        # Überwache die Systemleistung und passe die Pause entsprechend an
        pause_time = monitor_system_performance()
        print(f"Pause von {pause_time} Sekunden...")
        time.sleep(pause_time)

    # Am Ende vollständiges Upgrade und Neustart
    print("\nFühre vollständiges Upgrade durch...")
    subprocess.call("sudo apt-get full-upgrade -y", shell=True)
    log_action("Vollständiges Upgrade abgeschlossen.")

    print("\nStarte das System neu...")
    subprocess.call("sudo reboot", shell=True)
    log_action("Systemneustart durchgeführt.")

if __name__ == "__main__":
    main()
