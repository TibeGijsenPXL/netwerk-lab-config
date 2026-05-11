"""
Task 36 – NETCONF (Python)
Haalt YANG-XML configuratie op uit GitHub en deployt via NETCONF op IOS-XE.

Vereisten:
    pip install ncclient paramiko==2.12.0 requests

GitHub repo: https://github.com/TibeGijsenPXL/netwerk-lab-config
Config file: netconf_config.xml
"""

import requests
from ncclient import manager
from paramiko.transport import Transport

# ─────────────────────────────────────────────────────────
#  SSH-fix voor oude Cisco IOS-XE algoritmen (paramiko 2.x)
# ─────────────────────────────────────────────────────────
Transport._preferred_kex = (
    "diffie-hellman-group14-sha1",
    "diffie-hellman-group-exchange-sha256",
    "diffie-hellman-group-exchange-sha1",
    "diffie-hellman-group1-sha1",
)
Transport._preferred_keys = (
    "ssh-rsa",
    "ssh-dss",
    "ecdsa-sha2-nistp256",
    "ecdsa-sha2-nistp384",
    "ecdsa-sha2-nistp521",
)

# ─────────────────────────────────────────────
#  Instellingen
# ─────────────────────────────────────────────
GITHUB_RAW_URL = "https://raw.githubusercontent.com/TibeGijsenPXL/netwerk-lab-config/main/netconf_config.xml"

CONN = {
    "host": "192.168.56.103",
    "port": 830,
    "username": "admin",
    "password": "admin",
    "hostkey_verify": False,
    "look_for_keys": False,
    "allow_agent": False,
    "device_params": {"name": "iosxe"},
    "manager_params": {"timeout": 60},
}


def haal_config_op_uit_github(url):
    """Haal XML configuratie op uit GitHub."""
    print(f"[INFO] Configuratie ophalen uit GitHub...")
    print(f"       URL: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"[OK] Configuratie opgehaald ({len(response.text)} bytes)")
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception(f"GitHub ophalen mislukt: {e}")


def deploy_via_netconf(xml_config):
    """Deploy de XML configuratie via NETCONF naar de router."""
    print(f"\n[INFO] Verbinding maken met router {CONN['host']}:{CONN['port']}...")

    with manager.connect(**CONN) as m:
        print("[OK] NETCONF verbinding geslaagd")

        # Controleer of candidate beschikbaar is
        caps = list(m.server_capabilities)
        heeft_candidate = any("candidate" in c for c in caps)

        try:
            if heeft_candidate:
                print("[INFO] Candidate datastore beschikbaar, configuratie stagen...")
                m.edit_config(target="candidate", config=xml_config)
                m.validate(source="candidate")
                m.commit()
                print("[OK] Configuratie gecommit via candidate datastore")
            else:
                print("[INFO] Candidate niet beschikbaar, deployen naar running...")
                with m.locked("running"):
                    m.edit_config(target="running", config=xml_config)
                print("[OK] Configuratie toegepast op running datastore")

        except Exception as e:
            print(f"[FOUT] Deployment mislukt: {e}")
            if heeft_candidate:
                try:
                    m.discard_changes()
                    print("[OK] discard-changes uitgevoerd (rollback)")
                except Exception:
                    pass
            raise


def verifieer_configuratie():
    """Haal de running config op ter verificatie."""
    print("\n[INFO] Configuratie verificeren...")

    filtr = """
    <filter>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <hostname/>
        <interface/>
        <router/>
      </native>
    </filter>
    """

    with manager.connect(**CONN) as m:
        result = m.get_config(source="running", filter=filtr)
        print("[OK] Verificatie geslaagd - running config opgehaald:")
        print(result)


def main():
    print("=" * 55)
    print("  Task 36 – NETCONF Python Deployment")
    print("  GitHub → NETCONF → IOS-XE")
    print("=" * 55)

    try:
        # Stap 1: Config ophalen uit GitHub
        xml_config = haal_config_op_uit_github(GITHUB_RAW_URL)

        # Stap 2: Deploy via NETCONF
        deploy_via_netconf(xml_config)

        # Stap 3: Verificeer
        verifieer_configuratie()

        print("\n" + "=" * 55)
        print("  [OK] Task 36 volledig geslaagd!")
        print("  Configuratie actief op de router.")
        print("=" * 55)

    except Exception as e:
        print(f"\n[FOUT] Task 36 mislukt: {e}")
        print("=" * 55)


if __name__ == "__main__":
    main()
