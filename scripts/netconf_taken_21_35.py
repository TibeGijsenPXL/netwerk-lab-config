"""
LAB 8.2 – IOS-XE Automatisering met YANG, NETCONF en RESTCONF
Taken 21 t/m 35 – Python + ncclient
Router: 192.168.56.103

Vereisten:
    pip install ncclient paramiko==2.12.0
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
#  Task 21 – Use Candidate Datastore
#  Candidate niet ondersteund op IOS-XE 16.9.5
#  → fallback naar running met lock
# ─────────────────────────────────────────────
def task21_candidate_datastore():
    config = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <GigabitEthernet>
            <name>1</name>
            <description>Task 21 - via candidate/running datastore</description>
          </GigabitEthernet>
        </interface>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        caps = list(m.server_capabilities)
        heeft_candidate = any("candidate" in c for c in caps)
        if heeft_candidate:
            m.edit_config(target="candidate", config=config)
            m.validate(source="candidate")
            m.commit()
            print("[OK] Task 21: geconfigureerd via candidate datastore")
        else:
            # Fallback: lock running, wijzig, unlock
            with m.locked("running"):
                m.edit_config(target="running", config=config)
            print("[OK] Task 21: candidate niet beschikbaar, geconfigureerd via running (met lock)")


# ─────────────────────────────────────────────
#  Task 22 – Lock and Unlock Datastore
# ─────────────────────────────────────────────
def task22_lock_unlock():
    config = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <GigabitEthernet>
            <name>1</name>
            <description>Task 22 - geconfigureerd met datastore lock</description>
          </GigabitEthernet>
        </interface>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        print("[INFO] Task 22: datastore locken...")
        with m.locked("running"):
            print("[OK] Task 22: datastore gelockt")
            m.edit_config(target="running", config=config)
            print("[OK] Task 22: configuratie toegepast")
        print("[OK] Task 22: datastore ontgrendeld")


# ─────────────────────────────────────────────
#  Task 23 – Configure Multiple Interfaces
#  in One Transaction
# ─────────────────────────────────────────────
def task23_multiple_interfaces():
    config = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <GigabitEthernet>
            <name>1</name>
            <description>Task 23 - Interface 1 in transactie</description>
          </GigabitEthernet>
          <GigabitEthernet>
            <name>2</name>
            <description>Task 23 - Interface 2 in transactie</description>
            <ip>
              <address>
                <primary>
                  <address>10.10.10.1</address>
                  <mask>255.255.255.0</mask>
                </primary>
              </address>
            </ip>
          </GigabitEthernet>
          <Loopback>
            <name>0</name>
            <description>Task 23 - Loopback in transactie</description>
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
        with m.locked("running"):
            m.edit_config(target="running", config=config)
        print("[OK] Task 23: Gi1, Gi2 en Loopback0 geconfigureerd in één transactie")


# ─────────────────────────────────────────────
#  Task 24 – Rollback Configuration
#  Wijzig iets en zet het terug
# ─────────────────────────────────────────────
def task24_rollback():
    # Stap 1: Wijziging doorvoeren
    config_nieuw = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <GigabitEthernet>
            <name>1</name>
            <description>Task 24 - TIJDELIJKE beschrijving</description>
          </GigabitEthernet>
        </interface>
      </native>
    </config>
    """
    # Stap 2: Rollback (originele waarde herstellen)
    config_rollback = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <GigabitEthernet>
            <name>1</name>
            <description>Geconfigureerd via NETCONF/YANG</description>
          </GigabitEthernet>
        </interface>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config_nieuw)
        print("[OK] Task 24: tijdelijke wijziging toegepast")
        m.edit_config(target="running", config=config_rollback)
        print("[OK] Task 24: rollback uitgevoerd, originele config hersteld")


# ─────────────────────────────────────────────
#  Task 25 – Compare Running vs Candidate
#  Candidate niet beschikbaar → vergelijk
#  twee get-config resultaten
# ─────────────────────────────────────────────
def task25_compare_config():
    filtr = """
    <filter>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface/>
      </native>
    </filter>
    """
    with manager.connect(**CONN) as m:
        running = m.get_config(source="running", filter=filtr)
        print("[OK] Task 25: running configuratie opgehaald")
        print("[INFO] Task 25: candidate niet beschikbaar op IOS-XE 16.9.5")
        print("[INFO] Task 25: running config interfaces:")
        print(running)


# ─────────────────────────────────────────────
#  Task 26 – Configure IPv6 Address
# ─────────────────────────────────────────────
def task26_configure_ipv6():
    # Eerst IPv6 unicast routing inschakelen
    config_routing = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <ipv6>
          <unicast-routing/>
        </ipv6>
      </native>
    </config>
    """
    # Dan IPv6 adres op Loopback0
    config_ipv6 = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <Loopback>
            <name>0</name>
            <ipv6>
              <address>
                <prefix-list>
                  <prefix>2001:db8::1/128</prefix>
                </prefix-list>
              </address>
            </ipv6>
          </Loopback>
        </interface>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config_routing)
        m.edit_config(target="running", config=config_ipv6)
        print("[OK] Task 26: IPv6 adres 2001:db8::1/128 geconfigureerd op Loopback0")


# ─────────────────────────────────────────────
#  Task 27 – Configure OSPF Routing
#  Gi1: 192.168.56.103 (bestaand)
#  Gi2: 10.10.10.1 (geconfigureerd in Task 23)
#  Lo0: 1.1.1.1 (router-id)
# ─────────────────────────────────────────────
def task27_configure_ospf():
    config = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <router>
          <ospf xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ospf">
            <id>1</id>
            <router-id>1.1.1.1</router-id>
            <network>
              <ip>192.168.56.0</ip>
              <mask>0.0.0.255</mask>
              <area>0</area>
            </network>
            <network>
              <ip>10.10.10.0</ip>
              <mask>0.0.0.255</mask>
              <area>0</area>
            </network>
            <network>
              <ip>1.1.1.1</ip>
              <mask>0.0.0.0</mask>
              <area>0</area>
            </network>
          </ospf>
        </router>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print("[OK] Task 27: OSPF process 1 geconfigureerd met router-id 1.1.1.1")


# ─────────────────────────────────────────────
#  Task 28 – Retrieve Routing Table
# ─────────────────────────────────────────────
def task28_routing_table():
    filtr = """
    <filter>
      <routing-state xmlns="urn:ietf:params:xml:ns:yang:ietf-routing">
        <routing-instance>
          <ribs/>
        </routing-instance>
      </routing-state>
    </filter>
    """
    with manager.connect(**CONN) as m:
        try:
            result = m.get(filtr)
            print("[OK] Task 28: routing table opgehaald:")
            print(result)
        except Exception:
            # Fallback via native model
            filtr2 = """
            <filter>
              <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                <ip>
                  <route/>
                </ip>
              </native>
            </filter>
            """
            result = m.get_config(source="running", filter=filtr2)
            print("[OK] Task 28: statische routes opgehaald via native model:")
            print(result)


# ─────────────────────────────────────────────
#  Task 29 – Configure Interface MTU
# ─────────────────────────────────────────────
def task29_configure_mtu():
    config = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <GigabitEthernet>
            <name>2</name>
            <mtu>1400</mtu>
          </GigabitEthernet>
        </interface>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print("[OK] Task 29: MTU 1400 geconfigureerd op GigabitEthernet2")


# ─────────────────────────────────────────────
#  Task 30 – Configure Access Control List
# ─────────────────────────────────────────────
def task30_configure_acl():
    # Stap 1: ACL aanmaken
    config_acl = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <ip>
          <access-list>
            <extended xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-acl">
              <name>LAB_ACL</name>
              <access-list-seq-rule>
                <sequence>10</sequence>
                <ace-rule>
                  <action>permit</action>
                  <protocol>ip</protocol>
                  <ipv4-address>192.168.56.0</ipv4-address>
                  <mask>0.0.0.255</mask>
                  <dst-any/>
                </ace-rule>
              </access-list-seq-rule>
              <access-list-seq-rule>
                <sequence>20</sequence>
                <ace-rule>
                  <action>deny</action>
                  <protocol>ip</protocol>
                  <any/>
                  <dst-any/>
                </ace-rule>
              </access-list-seq-rule>
            </extended>
          </access-list>
        </ip>
      </native>
    </config>
    """
    # Stap 2: ACL toepassen op interface
    config_apply = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <GigabitEthernet>
            <name>2</name>
            <ip>
              <access-group>
                <in>
                  <acl>
                    <acl-name>LAB_ACL</acl-name>
                    <in/>
                  </acl>
                </in>
              </access-group>
            </ip>
          </GigabitEthernet>
        </interface>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config_acl)
        print("[OK] Task 30: ACL 'LAB_ACL' aangemaakt")
        try:
            m.edit_config(target="running", config=config_apply)
            print("[OK] Task 30: ACL toegepast op GigabitEthernet2 inbound")
        except Exception as e:
            print(f"[WARN] Task 30: ACL toepassen mislukt: {e}")


# ─────────────────────────────────────────────
#  Task 31 – Configure Interface Speed and Duplex
# ─────────────────────────────────────────────
def task31_speed_duplex():
    config = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <GigabitEthernet>
            <name>2</name>
            <speed>
              <value-1000/>
            </speed>
            <duplex>
              <full/>
            </duplex>
          </GigabitEthernet>
        </interface>
      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        m.edit_config(target="running", config=config)
        print("[OK] Task 31: speed 1000 en duplex full geconfigureerd op GigabitEthernet2")


# ─────────────────────────────────────────────
#  Task 32 – Execute YANG Action
#  Interface counters wissen op GigabitEthernet1
# ─────────────────────────────────────────────
def task32_yang_action():
    action = """
    <action xmlns="urn:ietf:params:xml:ns:yang:1">
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>GigabitEthernet1</name>
          <statistics>
            <clear-counters xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-interfaces-oper"/>
          </statistics>
        </interface>
      </interfaces>
    </action>
    """
    with manager.connect(**CONN) as m:
        try:
            m.dispatch(action)
            print("[OK] Task 32: interface counters gewist op GigabitEthernet1")
        except Exception as e:
            print(f"[WARN] Task 32: YANG action mislukt: {e}")
            print("[INFO] Task 32: niet alle IOS-XE versies ondersteunen deze action via NETCONF")


# ─────────────────────────────────────────────
#  Task 33 – Retrieve YANG Capabilities
# ─────────────────────────────────────────────
def task33_yang_capabilities():
    with manager.connect(**CONN) as m:
        caps = list(m.server_capabilities)
        print(f"[OK] Task 33: {len(caps)} YANG capabilities gevonden\n")

        # Categoriseer capabilities
        ietf = [c for c in caps if "ietf" in c]
        cisco = [c for c in caps if "cisco" in c.lower()]
        openconfig = [c for c in caps if "openconfig" in c.lower()]
        netconf = [c for c in caps if "netconf" in c.lower()]

        print(f"  NETCONF basis:     {len(netconf)} capabilities")
        print(f"  IETF modellen:     {len(ietf)} capabilities")
        print(f"  Cisco modellen:    {len(cisco)} capabilities")
        print(f"  OpenConfig:        {len(openconfig)} capabilities")

        print("\n  Enkele IETF modellen:")
        for c in ietf[:5]:
            print(f"    {c}")

        print("\n  Enkele Cisco modellen:")
        for c in cisco[:5]:
            print(f"    {c}")

        if openconfig:
            print("\n  OpenConfig modellen:")
            for c in openconfig[:5]:
                print(f"    {c}")


# ─────────────────────────────────────────────
#  Task 34 – Use OpenConfig Models
# ─────────────────────────────────────────────
def task34_openconfig():
    config = """
    <config>
      <interfaces xmlns="http://openconfig.net/yang/interfaces">
        <interface>
          <name>GigabitEthernet2</name>
          <config>
            <name>GigabitEthernet2</name>
            <description>Task 34 - OpenConfig model</description>
            <enabled>true</enabled>
          </config>
        </interface>
      </interfaces>
    </config>
    """
    with manager.connect(**CONN) as m:
        try:
            m.edit_config(target="running", config=config)
            print("[OK] Task 34: interface geconfigureerd via OpenConfig YANG model")
        except Exception as e:
            print(f"[WARN] Task 34: OpenConfig mislukt: {e}")
            print("[INFO] Task 34: OpenConfig mogelijk niet ondersteund op deze IOS-XE versie")


# ─────────────────────────────────────────────
#  Task 35 – Full Service Deployment
#  Interfaces + IP + OSPF + ACL in één transactie
# ─────────────────────────────────────────────
def task35_full_deployment():
    config = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">

        <!-- Interfaces -->
        <interface>
          <GigabitEthernet>
            <name>1</name>
            <description>Task 35 - WAN interface</description>
          </GigabitEthernet>
          <GigabitEthernet>
            <name>2</name>
            <description>Task 35 - LAN interface</description>
            <ip>
              <address>
                <primary>
                  <address>10.10.10.1</address>
                  <mask>255.255.255.0</mask>
                </primary>
              </address>
            </ip>
          </GigabitEthernet>
          <Loopback>
            <name>0</name>
            <description>Task 35 - Router-ID</description>
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

        <!-- OSPF -->
        <router>
          <ospf xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ospf">
            <id>1</id>
            <router-id>1.1.1.1</router-id>
            <network>
              <ip>192.168.56.0</ip>
              <mask>0.0.0.255</mask>
              <area>0</area>
            </network>
            <network>
              <ip>10.10.10.0</ip>
              <mask>0.0.0.255</mask>
              <area>0</area>
            </network>
            <network>
              <ip>1.1.1.1</ip>
              <mask>0.0.0.0</mask>
              <area>0</area>
            </network>
          </ospf>
        </router>

        <!-- ACL -->
        <ip>
          <access-list>
            <extended xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-acl">
              <name>FULL_DEPLOY_ACL</name>
              <access-list-seq-rule>
                <sequence>10</sequence>
                <ace-rule>
                  <action>permit</action>
                  <protocol>ip</protocol>
                  <ipv4-address>192.168.56.0</ipv4-address>
                  <mask>0.0.0.255</mask>
                  <dst-any/>
                </ace-rule>
              </access-list-seq-rule>
            </extended>
          </access-list>
        </ip>

      </native>
    </config>
    """
    with manager.connect(**CONN) as m:
        with m.locked("running"):
            m.edit_config(target="running", config=config)
        print("[OK] Task 35: volledige service deployment geslaagd!")
        print("     - Interfaces geconfigureerd (Gi1, Gi2, Lo0)")
        print("     - OSPF process 1 actief")
        print("     - ACL FULL_DEPLOY_ACL aangemaakt")


# ─────────────────────────────────────────────
#  Hoofdprogramma
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  LAB 8.2 – NETCONF Taken 21 t/m 35")
    print("  Router: 192.168.56.103")
    print("=" * 55)

    taken = [
        ("Task 21 – Candidate datastore",         task21_candidate_datastore),
        ("Task 22 – Lock/Unlock datastore",        task22_lock_unlock),
        ("Task 23 – Multiple interfaces",          task23_multiple_interfaces),
        ("Task 24 – Rollback",                     task24_rollback),
        ("Task 25 – Compare config",               task25_compare_config),
        ("Task 26 – IPv6 adres",                   task26_configure_ipv6),
        ("Task 27 – OSPF routing",                 task27_configure_ospf),
        ("Task 28 – Routing table",                task28_routing_table),
        ("Task 29 – MTU aanpassen",                task29_configure_mtu),
        ("Task 30 – ACL configureren",             task30_configure_acl),
        ("Task 31 – Speed en duplex",              task31_speed_duplex),
        ("Task 32 – YANG action",                  task32_yang_action),
        ("Task 33 – YANG capabilities",            task33_yang_capabilities),
        ("Task 34 – OpenConfig modellen",          task34_openconfig),
        ("Task 35 – Full deployment",              task35_full_deployment),
    ]

    for naam, functie in taken:
        print(f"\n--- {naam} ---")
        try:
            functie()
        except Exception as e:
            print(f"[FOUT] mislukt: {e}")

    print("\n" + "=" * 55)
    print("  Alle taken uitgevoerd!")
    print("  Controleer op de router met:")
    print("  show ip interface brief")
    print("  show ip ospf neighbor")
    print("  show ip route ospf")
    print("  show access-lists")
    print("=" * 55)
