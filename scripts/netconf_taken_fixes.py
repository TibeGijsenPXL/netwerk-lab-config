"""
LAB 8.2 – Gefixte taken voor CSR1000V (IOS-XE 16.9.5)
Router: 192.168.56.103

Fixes t.o.v. origineel script:
- IP-adressen via Cisco native YANG model (niet ietf-ip)
- Enkel GigabitEthernet1 beschikbaar
- VLAN niet mogelijk op CSR1000V
- Statische route aangepast aan jouw subnet
"""

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
#  Verbindingsinstellingen
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
#  Task 2 – Enable GigabitEthernet1
#  (uitschakelen = verbinding weg, dus enable=True)
# ─────────────────────────────────────────────
def task2_enable_interface():
    config = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <GigabitEthernet>
            <name>1</name>
            <shutdown operation="delete"/>
          </GigabitEthernet>
        </interface>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print("[OK] Task 2: GigabitEthernet1 ingeschakeld (no shutdown)")


# ─────────────────────────────────────────────
#  Task 3 – IPv4 op Loopback1
#  (Gi1 aanpassen = gevaarlijk, gebruik Loopback1)
# ─────────────────────────────────────────────
def task3_configure_ipv4():
    config = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <Loopback>
            <name>1</name>
            <ip>
              <address>
                <primary>
                  <address>10.0.0.1</address>
                  <mask>255.255.255.0</mask>
                </primary>
              </address>
            </ip>
          </Loopback>
        </interface>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print("[OK] Task 3: IP 10.0.0.1/24 geconfigureerd op Loopback1")


# ─────────────────────────────────────────────
#  Task 4 – IPv4 verwijderen van Loopback1
# ─────────────────────────────────────────────
def task4_remove_ipv4():
    config = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <Loopback>
            <name>1</name>
            <ip>
              <address>
                <primary operation="delete">
                  <address>10.0.0.1</address>
                  <mask>255.255.255.0</mask>
                </primary>
              </address>
            </ip>
          </Loopback>
        </interface>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print("[OK] Task 4: IP 10.0.0.1 verwijderd van Loopback1")


# ─────────────────────────────────────────────
#  Task 6 – IP toewijzen aan Loopback0
# ─────────────────────────────────────────────
def task6_loopback_ip():
    config = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <Loopback>
            <name>0</name>
            <ip>
              <address>
                <primary>
                  <address>1.1.1.1</address>
                  <mask>255.255.255.255</mask>
                </primary>
              </address>
            </ip>
          </Loopback>
        </interface>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print("[OK] Task 6: IP 1.1.1.1/32 toegewezen aan Loopback0")


# ─────────────────────────────────────────────
#  Task 10 – Statische route aanmaken
#  Bestemming: 172.16.0.0/16 via 192.168.0.1
# ─────────────────────────────────────────────
def task10_static_route():
    config = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <ip>
          <route>
            <ip-route-interface-forwarding-list>
              <prefix>172.16.0.0</prefix>
              <mask>255.255.0.0</mask>
              <fwd-list>
                <fwd>192.168.0.1</fwd>
              </fwd-list>
            </ip-route-interface-forwarding-list>
          </route>
        </ip>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print("[OK] Task 10: statische route 172.16.0.0/16 via 192.168.0.1 aangemaakt")


# ─────────────────────────────────────────────
#  Task 11 – Statische route verwijderen
# ─────────────────────────────────────────────
def task11_remove_static_route():
    config = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <ip>
          <route>
            <ip-route-interface-forwarding-list operation="delete">
              <prefix>172.16.0.0</prefix>
              <mask>255.255.0.0</mask>
            </ip-route-interface-forwarding-list>
          </route>
        </ip>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print("[OK] Task 11: statische route 172.16.0.0/16 verwijderd")


# ─────────────────────────────────────────────
#  Task 15 – VLAN (niet mogelijk op CSR1000V)
# ─────────────────────────────────────────────
def task15_create_vlan():
    print("[INFO] Task 15: VLAN configuratie is NIET mogelijk op een CSR1000V.")
    print("       De CSR1000V is een pure router zonder switch-module.")
    print("       VLAN's zijn enkel configureerbaar op Catalyst switches.")


# ─────────────────────────────────────────────
#  Task 16 – VLAN assign (niet mogelijk op CSR1000V)
# ─────────────────────────────────────────────
def task16_assign_vlan():
    print("[INFO] Task 16: Switchport/VLAN toewijzing NIET mogelijk op CSR1000V.")
    print("       Switchport commando's bestaan niet op deze router.")


# ─────────────────────────────────────────────
#  Task 20 – Validate via candidate datastore
# ─────────────────────────────────────────────
def task20_validate_config():
    config = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <GigabitEthernet>
            <name>1</name>
            <description>Gevalideerd via NETCONF candidate datastore</description>
          </GigabitEthernet>
        </interface>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        caps = list(m.server_capabilities)
        heeft_candidate = any("candidate" in c for c in caps)

        if heeft_candidate:
            try:
                m.edit_config(target="candidate", config=config)
                m.validate(source="candidate")
                m.commit()
                print("[OK] Task 20: gevalideerd en gecommit via candidate datastore")
            except Exception as e:
                print(f"[WARN] Task 20: candidate mislukt ({e}), fallback naar running")
                m.edit_config(target="running", config=config)
                print("[OK] Task 20: toegepast op running (fallback)")
        else:
            m.edit_config(target="running", config=config)
            print("[OK] Task 20: candidate niet beschikbaar, toegepast op running")


# ─────────────────────────────────────────────
#  Hoofdprogramma
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  LAB 8.2 – Gefixte taken voor CSR1000V")
    print("  Router: 192.168.56.103")
    print("=" * 55)

    taken = [
        ("Task 2  – Interface enable",       task2_enable_interface),
        ("Task 3  – IPv4 op Loopback1",      task3_configure_ipv4),
        ("Task 4  – IPv4 verwijderen",        task4_remove_ipv4),
        ("Task 6  – Loopback0 IP",            task6_loopback_ip),
        ("Task 10 – Statische route",         task10_static_route),
        ("Task 11 – Route verwijderen",       task11_remove_static_route),
        ("Task 15 – VLAN (info)",             task15_create_vlan),
        ("Task 16 – VLAN assign (info)",      task16_assign_vlan),
        ("Task 20 – Validate config",         task20_validate_config),
    ]

    for naam, functie in taken:
        print(f"\n--- {naam} ---")
        try:
            functie()
        except Exception as e:
            print(f"[FOUT] mislukt: {e}")

    print("\n" + "=" * 55)
    print("  Klaar! Controleer op de router met:")
    print("  show ip interface brief")
    print("  show ip route")
    print("  show running-config")
    print("=" * 55)
