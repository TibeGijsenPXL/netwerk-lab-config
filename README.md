# 🌐 Netwerk Lab Config
**Network as Code – IOS-XE Automatisering met YANG, NETCONF en RESTCONF**

> LAB 8.2 – Projectopdracht Network Programmability  
> Student: Tibe Gijsen | PXL

---

## 📋 Overzicht

Dit repository fungeert als **single source of truth** voor de automatisering van een Cisco IOS-XE router (CSR1000V) via YANG-modellering, NETCONF en RESTCONF.

Alle configuratiebestanden worden hier centraal beheerd en opgehaald door Python-scripts en Ansible-playbooks die de configuratie automatisch deployen op het netwerkapparaat.

---

## 🏗️ Architectuur

```
GitHub (single source of truth)
        │
        ├── netconf_config.xml      ← YANG-XML voor NETCONF
        └── restconf_config.json    ← YANG-JSON voor RESTCONF
                │
                ▼
    ┌───────────────────────┐
    │   Ubuntu (Python /    │
    │   Ansible)            │
    │   192.168.56.x        │
    └───────────┬───────────┘
                │ NETCONF (poort 830)
                │ RESTCONF (HTTPS poort 443)
                ▼
    ┌───────────────────────┐
    │   Cisco CSR1000V      │
    │   IOS-XE 16.9.5       │
    │   192.168.56.103      │
    └───────────────────────┘
```

---

## 📁 Repository structuur

```
netwerk-lab-config/
│
├── README.md                       # Dit bestand
│
├── netconf_config.xml              # YANG-XML configuratie (NETCONF)
├── restconf_config.json            # YANG-JSON configuratie (RESTCONF)
│
├── task36_netconf_python.py        # Task 36: Python + NETCONF
├── task37_netconf_ansible.yml      # Task 37: Ansible + NETCONF
├── task38_restconf_python.py       # Task 38: Python + RESTCONF
└── task39_restconf_ansible.yml     # Task 39: Ansible + RESTCONF
```

---

## ⚙️ Vereisten

### Software
| Tool | Versie |
|------|--------|
| Python | 3.12 |
| paramiko | 2.12.0 |
| ncclient | latest |
| requests | latest |
| ansible | latest |
| ansible.netcommon | latest |

### Installatie
```bash
# Python venv aanmaken
python3 -m venv venv
source venv/bin/activate

# Python packages installeren
pip install ncclient paramiko==2.12.0 requests ansible

# Ansible collections installeren
ansible-galaxy collection install ansible.netcommon
```

### Router vereisten
```
netconf-yang
restconf
ip http server
ip http secure-server
```

---

## 🔧 Configuratiebestanden

### netconf_config.xml
YANG-gebaseerde XML configuratie voor NETCONF deployment. Bevat:
- **Hostname**: MijnRouter
- **GigabitEthernet1**: WAN interface (beschrijving)
- **GigabitEthernet2**: LAN interface (IP: 10.10.10.1/24)
- **Loopback0**: Router-ID (IP: 1.1.1.1/32)
- **OSPF**: Process 1, router-id 1.1.1.1, area 0

### restconf_config.json
YANG-compliant JSON configuratie voor RESTCONF deployment. Bevat dezelfde configuratie als het XML-bestand maar in JSON formaat voor gebruik met RESTCONF HTTP calls.

---

## 🚀 Taken uitvoeren

### Task 36 – Python + NETCONF
```bash
python task36_netconf_python.py
```
Haalt `netconf_config.xml` op uit GitHub en deployt via NETCONF (poort 830).

**Werking:**
1. Configuratie ophalen uit GitHub via HTTP GET
2. Verbinding maken via NETCONF (SSH poort 830)
3. `edit-config` uitvoeren naar running datastore
4. Verificatie via `get-config`

### Task 37 – Ansible + NETCONF
```bash
ansible-playbook task37_netconf_ansible.yml
```
Ansible-playbook dat `netconf_config.xml` ophaalt uit GitHub en deployt via NETCONF.

**Werking:**
1. `get_url` module → configuratie ophalen uit GitHub
2. `netconf_config` module → configuratie deployen
3. `netconf_get` module → verificatie

### Task 38 – Python + RESTCONF
```bash
python task38_restconf_python.py
```
Haalt `restconf_config.json` op uit GitHub en deployt via RESTCONF (HTTPS PUT/PATCH).

**Werking:**
1. Configuratie ophalen uit GitHub via HTTP GET
2. Per onderdeel een RESTCONF PUT uitvoeren
3. HTTP statuscodes controleren (200/201/204)
4. Verificatie via RESTCONF GET

### Task 39 – Ansible + RESTCONF
```bash
ansible-playbook task39_restconf_ansible.yml
```
Ansible-playbook dat `restconf_config.json` ophaalt uit GitHub en deployt via RESTCONF met de `uri` module.

**Werking:**
1. `get_url` module → configuratie ophalen uit GitHub
2. `uri` module → RESTCONF PUT calls per onderdeel
3. `uri` module → verificatie via GET

---

## 📡 YANG Modellen gebruikt

| Model | Namespace | Gebruik |
|-------|-----------|---------|
| Cisco-IOS-XE-native | `http://cisco.com/ns/yang/Cisco-IOS-XE-native` | Hostname, interfaces, routing |
| Cisco-IOS-XE-ospf | `http://cisco.com/ns/yang/Cisco-IOS-XE-ospf` | OSPF configuratie |
| ietf-interfaces | `urn:ietf:params:xml:ns:yang:ietf-interfaces` | Interface operationele data |
| ietf-ip | `urn:ietf:params:xml:ns:yang:ietf-ip` | IP adressering |
| openconfig-interfaces | `http://openconfig.net/yang/interfaces` | OpenConfig interface config |

---

## 🌐 RESTCONF URLs

| Operatie | Methode | URL |
|----------|---------|-----|
| Hostname opvragen | GET | `https://192.168.56.103/restconf/data/Cisco-IOS-XE-native:native/hostname` |
| Hostname instellen | PUT | `https://192.168.56.103/restconf/data/Cisco-IOS-XE-native:native/hostname` |
| Interface opvragen | GET | `https://192.168.56.103/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=2` |
| Interface instellen | PUT | `https://192.168.56.103/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=2` |
| OSPF instellen | PUT | `https://192.168.56.103/restconf/data/Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-ospf:ospf=1` |

---

## 🔒 SSH Fix (paramiko 2.12.0)

De Cisco CSR1000V gebruikt oudere SSH algoritmen. Dit vereist een fix in paramiko:

```python
from paramiko.transport import Transport

Transport._preferred_kex = (
    "diffie-hellman-group14-sha1",
    "diffie-hellman-group-exchange-sha256",
)
Transport._preferred_keys = (
    "ssh-rsa",
    "ssh-dss",
)
```

> **Reden:** Paramiko 3.x+ heeft `diffie-hellman-group14-sha1` verwijderd.  
> **Oplossing:** Downgraden naar `paramiko==2.12.0`

---

## 🖥️ Laboratoriumopstelling

| Apparaat | IP-adres | Rol |
|----------|----------|-----|
| Ubuntu VM | 192.168.56.x | Automatiseringsplatform (Python/Ansible/YANG Suite) |
| Cisco CSR1000V | 192.168.56.103 | Netwerkapparaat (IOS-XE 16.9.5) |

### Netwerktopologie
```
[Ubuntu VM] ──── Host-only Adapter ──── [CSR1000V]
192.168.56.x                            192.168.56.103
     │
     └── YANG Suite (localhost:8443)
     └── Python scripts
     └── Ansible playbooks
```

---

## ✅ Resultaten

| Task | Beschrijving | Protocol | Tool | Status |
|------|-------------|----------|------|--------|
| 1-6 | Interface configuratie | NETCONF | Python | ✅ |
| 7-12 | Systeem configuratie | NETCONF | Python | ✅ |
| 13-14 | Gebruikersbeheer | NETCONF | Python | ✅ |
| 15-16 | VLAN | - | - | ❌ CSR1000V beperking |
| 17-20 | SNMP, statistieken | NETCONF | Python | ✅ |
| 21-25 | Candidate datastore | NETCONF | Python | ✅ (fallback) |
| 26-28 | IPv6, OSPF, routing | NETCONF | Python | ✅ |
| 29 | MTU | NETCONF | Python | ❌ Virtuele interface |
| 30 | ACL | NETCONF | Python | ✅ |
| 31 | Speed/duplex | NETCONF | Python | ❌ Virtuele interface |
| 32 | YANG action | NETCONF | Python | ✅ (counters ophalen) |
| 33-35 | Capabilities, OpenConfig, deployment | NETCONF | Python | ✅ |
| 36 | End-to-end GitHub→NETCONF | NETCONF | Python | ✅ |
| 37 | End-to-end GitHub→NETCONF | NETCONF | Ansible | ✅ |
| 38 | End-to-end GitHub→RESTCONF | RESTCONF | Python | ✅ |
| 39 | End-to-end GitHub→RESTCONF | RESTCONF | Ansible | ✅ |

> **Noot:** Tasks 15, 16, 29 en 31 zijn niet uitvoerbaar op de CSR1000V door hardwarebeperkingen (geen switch-module, virtuele interfaces).

---

## 👨‍💻 Auteur

**Tibe Gijsen**  
PXL University of Applied Sciences  
Network Programmability – LAB 8.2
