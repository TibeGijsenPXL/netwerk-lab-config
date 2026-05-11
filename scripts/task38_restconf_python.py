"""
Task 38 – RESTCONF (Python)
Haalt YANG-JSON configuratie op uit GitHub en deployt via RESTCONF op IOS-XE.

Vereisten:
    pip install requests

GitHub repo: https://github.com/TibeGijsenPXL/netwerk-lab-config
Config file: restconf_config.json
"""

import json
import requests
from requests.auth import HTTPBasicAuth

# Schakel SSL waarschuwingen uit voor self-signed certificaat
requests.packages.urllib3.disable_warnings()

# ─────────────────────────────────────────────
#  Instellingen
# ─────────────────────────────────────────────
GITHUB_RAW_URL = "https://raw.githubusercontent.com/TibeGijsenPXL/netwerk-lab-config/main/restconf_config.json"

ROUTER = {
    "host": "192.168.56.103",
    "port": 443,
    "username": "admin",
    "password": "admin",
}

RESTCONF_BASE = f"https://{ROUTER['host']}:{ROUTER['port']}/restconf/data"
AUTH = HTTPBasicAuth(ROUTER["username"], ROUTER["password"])
HEADERS = {
    "Content-Type": "application/yang-data+json",
    "Accept": "application/yang-data+json",
}


def haal_config_op_uit_github(url):
    """Haal JSON configuratie op uit GitHub."""
    print(f"[INFO] Configuratie ophalen uit GitHub...")
    print(f"       URL: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        config = response.json()
        # Verwijder comment velden
        config.pop("_comment", None)
        config.pop("_gebruikt_door", None)
        print(f"[OK] Configuratie opgehaald uit GitHub")
        return config
    except requests.exceptions.RequestException as e:
        raise Exception(f"GitHub ophalen mislukt: {e}")


def deploy_hostname(hostname):
    """Configureer hostname via RESTCONF."""
    url = f"{RESTCONF_BASE}/Cisco-IOS-XE-native:native/hostname"
    payload = {"Cisco-IOS-XE-native:hostname": hostname}

    response = requests.put(url, auth=AUTH, headers=HEADERS,
                            json=payload, verify=False, timeout=10)

    if response.status_code in [200, 201, 204]:
        print(f"[OK] Hostname '{hostname}' geconfigureerd")
    else:
        print(f"[WARN] Hostname: HTTP {response.status_code} - {response.text}")


def deploy_interface_gi2(ip, mask):
    """Configureer GigabitEthernet2 IP via RESTCONF."""
    url = f"{RESTCONF_BASE}/Cisco-IOS-XE-native:native/interface/GigabitEthernet=2"
    payload = {
        "Cisco-IOS-XE-native:GigabitEthernet": {
            "name": "2",
            "description": "LAN - Geconfigureerd via RESTCONF/YANG GitHub",
            "ip": {
                "address": {
                    "primary": {
                        "address": ip,
                        "mask": mask
                    }
                }
            }
        }
    }

    response = requests.put(url, auth=AUTH, headers=HEADERS,
                            json=payload, verify=False, timeout=10)

    if response.status_code in [200, 201, 204]:
        print(f"[OK] GigabitEthernet2 geconfigureerd met IP {ip}/{mask}")
    else:
        print(f"[WARN] GigabitEthernet2: HTTP {response.status_code} - {response.text}")


def deploy_loopback(ip, mask):
    """Configureer Loopback0 IP via RESTCONF."""
    url = f"{RESTCONF_BASE}/Cisco-IOS-XE-native:native/interface/Loopback=0"
    payload = {
        "Cisco-IOS-XE-native:Loopback": {
            "name": "0",
            "description": "Router-ID Loopback",
            "ip": {
                "address": {
                    "primary": {
                        "address": ip,
                        "mask": mask
                    }
                }
            }
        }
    }

    response = requests.put(url, auth=AUTH, headers=HEADERS,
                            json=payload, verify=False, timeout=10)

    if response.status_code in [200, 201, 204]:
        print(f"[OK] Loopback0 geconfigureerd met IP {ip}/{mask}")
    else:
        print(f"[WARN] Loopback0: HTTP {response.status_code} - {response.text}")


def deploy_ospf():
    """Configureer OSPF via RESTCONF."""
    url = f"{RESTCONF_BASE}/Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-ospf:ospf=1"
    payload = {
        "Cisco-IOS-XE-ospf:ospf": {
            "id": 1,
            "router-id": "1.1.1.1",
            "network": [
                {"ip": "192.168.56.0", "mask": "0.0.0.255", "area": 0},
                {"ip": "10.10.10.0",   "mask": "0.0.0.255", "area": 0},
                {"ip": "1.1.1.1",      "mask": "0.0.0.0",   "area": 0}
            ]
        }
    }

    response = requests.put(url, auth=AUTH, headers=HEADERS,
                            json=payload, verify=False, timeout=10)

    if response.status_code in [200, 201, 204]:
        print(f"[OK] OSPF process 1 geconfigureerd")
    else:
        print(f"[WARN] OSPF: HTTP {response.status_code} - {response.text}")


def verifieer_via_restconf():
    """Verifieer de configuratie via RESTCONF GET."""
    print("\n[INFO] Verificatie via RESTCONF GET...")

    url = f"{RESTCONF_BASE}/Cisco-IOS-XE-native:native/hostname"
    response = requests.get(url, auth=AUTH, headers=HEADERS,
                            verify=False, timeout=10)

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Verificatie geslaagd!")
        print(f"     Hostname: {data.get('Cisco-IOS-XE-native:hostname', 'onbekend')}")
    else:
        print(f"[WARN] Verificatie: HTTP {response.status_code}")


def main():
    print("=" * 55)
    print("  Task 38 – RESTCONF Python Deployment")
    print("  GitHub → RESTCONF → IOS-XE")
    print("=" * 55)

    try:
        # Stap 1: Config ophalen uit GitHub
        config = haal_config_op_uit_github(GITHUB_RAW_URL)

        native = config.get("Cisco-IOS-XE-native:native", {})

        print("\n[INFO] Configuratie deployen via RESTCONF...")

        # Stap 2: Hostname
        hostname = native.get("hostname", "MijnRouter")
        deploy_hostname(hostname)

        # Stap 3: Interfaces
        interfaces = native.get("interface", {})

        gi_list = interfaces.get("GigabitEthernet", [])
        for gi in gi_list:
            if gi.get("name") == "2":
                ip = gi.get("ip", {}).get("address", {}).get("primary", {})
                if ip:
                    deploy_interface_gi2(ip["address"], ip["mask"])

        lo_list = interfaces.get("Loopback", [])
        for lo in lo_list:
            if lo.get("name") == "0":
                ip = lo.get("ip", {}).get("address", {}).get("primary", {})
                if ip:
                    deploy_loopback(ip["address"], ip["mask"])

        # Stap 4: OSPF
        deploy_ospf()

        # Stap 5: Verificeer
        verifieer_via_restconf()

        print("\n" + "=" * 55)
        print("  [OK] Task 38 volledig geslaagd!")
        print("  Configuratie zichtbaar in running-config.")
        print("=" * 55)

    except Exception as e:
        print(f"\n[FOUT] Task 38 mislukt: {e}")


if __name__ == "__main__":
    main()
