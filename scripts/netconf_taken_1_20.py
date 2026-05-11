"""
LAB 8.2 – IOS-XE Automatisering met YANG, NETCONF en RESTCONF
Taken 1 t/m 20 – Python + ncclient
Router: 192.168.56.103 | YANG Suite: 192.168.0.117

Vereiste installatie:
    pip install ncclient

Gebruik:
    python netconf_taken_1_20.py
    Of roep individuele functies aan onderaan het script.
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
#  Task 1 – Configure Interface Description
# ─────────────────────────────────────────────
def task1_interface_description():
    config = """
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>GigabitEthernet1</name>
          <description>Geconfigureerd via NETCONF/YANG</description>
        </interface>
      </interfaces>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print("[OK] Task 1: description geconfigureerd op GigabitEthernet1")


# ─────────────────────────────────────────────
#  Task 2 – Enable / Disable Interface
# ─────────────────────────────────────────────
def task2_disable_interface(interface="GigabitEthernet2", enable=False):
    status = "true" if enable else "false"
    config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{interface}</name>
          <enabled>{status}</enabled>
        </interface>
      </interfaces>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        actie = "ingeschakeld" if enable else "uitgeschakeld"
        print(f"[OK] Task 2: {interface} {actie}")


# ─────────────────────────────────────────────
#  Task 3 – Configure IPv4 Address
# ─────────────────────────────────────────────
def task3_configure_ipv4(interface="GigabitEthernet2", ip="10.0.0.1", prefix=24):
    config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{interface}</name>
          <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
            <address>
              <ip>{ip}</ip>
              <prefix-length>{prefix}</prefix-length>
            </address>
          </ipv4>
        </interface>
      </interfaces>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print(f"[OK] Task 3: IPv4-adres {ip}/{prefix} geconfigureerd op {interface}")


# ─────────────────────────────────────────────
#  Task 4 – Remove IPv4 Address
# ─────────────────────────────────────────────
def task4_remove_ipv4(interface="GigabitEthernet2", ip="10.0.0.1"):
    config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{interface}</name>
          <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
            <address operation="delete">
              <ip>{ip}</ip>
            </address>
          </ipv4>
        </interface>
      </interfaces>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print(f"[OK] Task 4: IPv4-adres {ip} verwijderd van {interface}")


# ─────────────────────────────────────────────
#  Task 5 – Create Loopback Interface
# ─────────────────────────────────────────────
def task5_create_loopback(loopback_id=0):
    config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{loopback_id}</name>
          <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">
            ianaift:softwareLoopback
          </type>
          <enabled>true</enabled>
        </interface>
      </interfaces>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print(f"[OK] Task 5: Loopback{loopback_id} aangemaakt")


# ─────────────────────────────────────────────
#  Task 6 – Configure Loopback IP
# ─────────────────────────────────────────────
def task6_loopback_ip(loopback_id=0, ip="1.1.1.1", prefix=32):
    config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{loopback_id}</name>
          <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
            <address>
              <ip>{ip}</ip>
              <prefix-length>{prefix}</prefix-length>
            </address>
          </ipv4>
        </interface>
      </interfaces>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print(f"[OK] Task 6: IP {ip}/{prefix} toegewezen aan Loopback{loopback_id}")


# ─────────────────────────────────────────────
#  Task 7 – Change Hostname
# ─────────────────────────────────────────────
def task7_change_hostname(hostname="MijnRouter"):
    config = f"""
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <hostname>{hostname}</hostname>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print(f"[OK] Task 7: hostname gewijzigd naar '{hostname}'")


# ─────────────────────────────────────────────
#  Task 8 – Configure DNS Server
# ─────────────────────────────────────────────
def task8_configure_dns(dns_server="8.8.8.8"):
    config = f"""
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <ip>
          <name-server>
            <no-vrf>{dns_server}</no-vrf>
          </name-server>
        </ip>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print(f"[OK] Task 8: DNS-server {dns_server} geconfigureerd")


# ─────────────────────────────────────────────
#  Task 9 – Configure NTP Server
# ─────────────────────────────────────────────
def task9_configure_ntp(ntp_server="216.239.35.0"):
    config = f"""
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <ntp>
          <server xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ntp">
            <server-list>
              <ip-address>{ntp_server}</ip-address>
            </server-list>
          </server>
        </ntp>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print(f"[OK] Task 9: NTP-server {ntp_server} geconfigureerd")


# ─────────────────────────────────────────────
#  Task 10 – Configure Static Route
# ─────────────────────────────────────────────
def task10_static_route(prefix="192.168.10.0", mask="255.255.255.0", next_hop="10.0.0.254"):
    config = f"""
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <ip>
          <route>
            <ip-route-interface-forwarding-list>
              <prefix>{prefix}</prefix>
              <mask>{mask}</mask>
              <fwd-list>
                <fwd>{next_hop}</fwd>
              </fwd-list>
            </ip-route-interface-forwarding-list>
          </route>
        </ip>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print(f"[OK] Task 10: statische route {prefix}/{mask} via {next_hop} aangemaakt")


# ─────────────────────────────────────────────
#  Task 11 – Remove Static Route
# ─────────────────────────────────────────────
def task11_remove_static_route(prefix="192.168.10.0", mask="255.255.255.0"):
    config = f"""
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <ip>
          <route>
            <ip-route-interface-forwarding-list operation="delete">
              <prefix>{prefix}</prefix>
              <mask>{mask}</mask>
            </ip-route-interface-forwarding-list>
          </route>
        </ip>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print(f"[OK] Task 11: statische route {prefix} verwijderd")


# ─────────────────────────────────────────────
#  Task 12 – Configure Banner MOTD
# ─────────────────────────────────────────────
def task12_banner_motd(bericht="Welkom! Onbevoegde toegang is verboden."):
    config = f"""
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <banner>
          <motd>
            <banner>{bericht}</banner>
          </motd>
        </banner>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print(f"[OK] Task 12: banner MOTD geconfigureerd")


# ─────────────────────────────────────────────
#  Task 13 – Create Local User
# ─────────────────────────────────────────────
def task13_create_user(username="labuser", password="Labpass123", privilege=15):
    config = f"""
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <username>
          <name>{username}</name>
          <privilege>{privilege}</privilege>
          <password>
            <encryption>0</encryption>
            <password>{password}</password>
          </password>
        </username>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print(f"[OK] Task 13: gebruiker '{username}' aangemaakt met privilege {privilege}")


# ─────────────────────────────────────────────
#  Task 14 – Change User Password
# ─────────────────────────────────────────────
def task14_change_password(username="labuser", new_password="NieuwWachtwoord456"):
    config = f"""
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <username>
          <name>{username}</name>
          <password>
            <encryption>0</encryption>
            <password>{new_password}</password>
          </password>
        </username>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print(f"[OK] Task 14: wachtwoord van '{username}' gewijzigd")


# ─────────────────────────────────────────────
#  Task 15 – Create VLAN
# ─────────────────────────────────────────────
def task15_create_vlan(vlan_id=10, vlan_name="LAB_VLAN"):
    config = f"""
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <vlan>
          <vlan-list xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-vlan">
            <id>{vlan_id}</id>
            <name>{vlan_name}</name>
          </vlan-list>
        </vlan>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print(f"[OK] Task 15: VLAN {vlan_id} '{vlan_name}' aangemaakt")


# ─────────────────────────────────────────────
#  Task 16 – Assign Interface to VLAN
# ─────────────────────────────────────────────
def task16_assign_vlan(interface_nr="3", vlan_id=10):
    config = f"""
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <GigabitEthernet>
            <name>{interface_nr}</name>
            <switchport>
              <access xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-switch">
                <vlan>
                  <vlan>{vlan_id}</vlan>
                </vlan>
              </access>
              <mode xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-switch">
                <access/>
              </mode>
            </switchport>
          </GigabitEthernet>
        </interface>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print(f"[OK] Task 16: GigabitEthernet{interface_nr} toegewezen aan VLAN {vlan_id}")


# ─────────────────────────────────────────────
#  Task 17 – Enable SNMP Community
# ─────────────────────────────────────────────
def task17_snmp_community(community="public"):
    config = f"""
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <snmp-server>
          <community xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-snmp">
            <name>{community}</name>
            <RO/>
          </community>
        </snmp-server>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print(f"[OK] Task 17: SNMP read-only community '{community}' geconfigureerd")


# ─────────────────────────────────────────────
#  Task 18 – Retrieve Interface Statistics
# ─────────────────────────────────────────────
def task18_interface_statistics(interface="GigabitEthernet1"):
    filtr = f"""
    <filter>
      <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{interface}</name>
          <statistics/>
        </interface>
      </interfaces-state>
    </filter>
    """
    with manager.connect(**CONN) as m:
        result = m.get(filtr)
        print(f"[OK] Task 18: statistieken van {interface}:")
        print(result)


# ─────────────────────────────────────────────
#  Task 19 – Retrieve Running Configuration
# ─────────────────────────────────────────────
def task19_running_config():
    filtr = """
    <filter>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
      </interfaces>
    </filter>
    """
    with manager.connect(**CONN) as m:
        result = m.get_config(source="running", filter=filtr)
        print("[OK] Task 19: running-config (interfaces) opgehaald:")
        print(result)


# ─────────────────────────────────────────────
#  Task 20 – Validate Configuration Change
# ─────────────────────────────────────────────
def task20_validate_config():
    config = """
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>GigabitEthernet1</name>
          <description>Gevalideerd via candidate datastore</description>
        </interface>
      </interfaces>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="candidate", config=config)
        m.validate(source="candidate")
        m.commit()
        print("[OK] Task 20: configuratie gevalideerd en gecommit via candidate datastore")


# ─────────────────────────────────────────────
#  Hoofdprogramma – voer alle taken uit
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  LAB 8.2 – NETCONF Taken 1 t/m 20")
    print("  Router: 192.168.56.103")
    print("=" * 55)

    taken = [
        ("Task 1",  task1_interface_description),
        ("Task 2",  lambda: task2_disable_interface("GigabitEthernet2", enable=False)),
        ("Task 3",  lambda: task3_configure_ipv4("GigabitEthernet2", "10.0.0.1", 24)),
        ("Task 4",  lambda: task4_remove_ipv4("GigabitEthernet2", "10.0.0.1")),
        ("Task 5",  lambda: task5_create_loopback(0)),
        ("Task 6",  lambda: task6_loopback_ip(0, "1.1.1.1", 32)),
        ("Task 7",  lambda: task7_change_hostname("MijnRouter")),
        ("Task 8",  lambda: task8_configure_dns("8.8.8.8")),
        ("Task 9",  lambda: task9_configure_ntp("216.239.35.0")),
        ("Task 10", lambda: task10_static_route("192.168.10.0", "255.255.255.0", "10.0.0.254")),
        ("Task 11", lambda: task11_remove_static_route("192.168.10.0", "255.255.255.0")),
        ("Task 12", lambda: task12_banner_motd("Welkom! Onbevoegde toegang is verboden.")),
        ("Task 13", lambda: task13_create_user("labuser", "Labpass123", 15)),
        ("Task 14", lambda: task14_change_password("labuser", "NieuwWachtwoord456")),
        ("Task 15", lambda: task15_create_vlan(10, "LAB_VLAN")),
        ("Task 16", lambda: task16_assign_vlan("3", 10)),
        ("Task 17", lambda: task17_snmp_community("public")),
        ("Task 18", lambda: task18_interface_statistics("GigabitEthernet1")),
        ("Task 19", task19_running_config),
        ("Task 20", task20_validate_config),
    ]

    for naam, functie in taken:
        print(f"\n--- {naam} ---")
        try:
            functie()
        except Exception as e:
            print(f"[FOUT] {naam} mislukt: {e}")

    print("\n" + "=" * 55)
    print("  Alle taken uitgevoerd!")
    print("=" * 55)
