# SIEM & MITRE ATT&CK Mapping

## Project

`profiles-rest-api` — Django REST API SIEM detection project.

## Scope

This document maps the application's validated SIEM detections to MITRE ATT&CK techniques where the observed behavior supports a direct mapping. IOC-based detections that do not represent a specific ATT&CK technique are explicitly documented as having no direct mapping.

## Detection Mapping

| Kibana Rule | Django Event | Detection Logic | MITRE ATT&CK | Tactic | Assessment |
|---|---|---|---|---|---|
| **Django - Brute Force Detected** | `BRUTE_FORCE_DETECTED` | Five failed login attempts from the same IP within five minutes | **T1110 – Brute Force** | Credential Access | Direct mapping. |
| **Django - Successful Login After Brute Force** | `BRUTE_FORCE_DETECTED` → `LOGIN_SUCCESS` | EQL sequence from the same source IP within five minutes | **T1110 – Brute Force** + **T1078 – Valid Accounts** | Credential Access / Initial Access | The sequence detects brute-force behavior followed by successful authentication. |
| **Django - Privilege Escalation** | `PRIVILEGE_ESCALATION` | Account privilege changes such as `is_staff` or `is_superuser` being granted | **T1098 – Account Manipulation** | Persistence / Privilege Escalation | Direct mapping because the application records modification of account privileges. |
| **Django - Unauthorized Access** | `UNAUTHORIZED_ACCESS` | Application records an access attempt that was denied | **No direct mapping** | — | The event identifies the security outcome but not the underlying attack technique. |
| **Django - Suspicious IP Detected** | `SUSPICIOUS_IP_DETECTED` | Source IP matches the configured suspicious-IP list | **No direct mapping** | — | IOC-based detection; an IP match alone does not establish an ATT&CK technique. |

## 1. Brute Force — T1110

### Detection

**Kibana rule:** `Django - Brute Force Detected`

**Django event:** `BRUTE_FORCE_DETECTED`

The application detects five failed login attempts from the same source IP within a five-minute window.

### MITRE ATT&CK

**T1110 – Brute Force**

This is a direct mapping because the observed behavior consists of repeated authentication attempts consistent with brute-force activity.

---

## 2. Successful Login After Brute Force — T1110 + T1078

### Detection

**Kibana rule:** `Django - Successful Login After Brute Force`

**EQL:**

```eql
sequence by source.ip with maxspan=5m
  [ any where event.action == "BRUTE_FORCE_DETECTED" ]
  [ any where event.action == "LOGIN_SUCCESS" ]
