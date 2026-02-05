# Google Drive Structure

Document: Collapse-Ready Sprint — Drive Folder Structure

Version: v01

---

## Root Structure

```text
/Collapse-Ready-Sprints/
├── _Templates/
│   ├── 01-Threat-Model-Template.gdoc
│   ├── 02-Data-Flow-Map-Template.gdoc
│   ├── 03-Findings-Register-Template.gdoc
│   ├── 04-Pass-Fail-Gates-Template.gdoc
│   ├── 05-Executive-Summary-Template.gdoc
│   └── 06-Scope-Lock-Template.gdoc
│
├── _Archive/
│   └── (closed engagements moved here after 90 days)
│
└── Client-{{intake_token}}/
    ├── 01-Threat-Model/
    │   └── Threat-Model-{{client_name}}.gdoc
    │
    ├── 02-Data-Flows/
    │   └── Data-Flow-Map-{{client_name}}.gdoc
    │
    ├── 03-Findings/
    │   └── Findings-Register-{{client_name}}.gdoc
    │
    ├── 04-Hardening/
    │   └── Pass-Fail-Gates-{{client_name}}.gdoc
    │
    ├── 05-Executive-Summary/
    │   └── Executive-Summary-{{client_name}}.gdoc
    │
    ├── 06-Scope-Lock/
    │   └── Scope-Lock-{{client_name}}.gdoc
    │
    ├── 07-Client-Provided/
    │   └── (documentation uploaded by client)
    │
    └── 08-Delivery/
        ├── Threat-Model-{{client_name}}.pdf
        ├── Data-Flow-Map-{{client_name}}.pdf
        ├── Findings-Register-{{client_name}}.pdf
        ├── Pass-Fail-Gates-{{client_name}}.pdf
        ├── Executive-Summary-{{client_name}}.pdf
        ├── README.md
        └── Collapse-Ready-Sprint-{{client_name}}.zip
```

---

## Folder Descriptions

| Folder | Purpose | Permissions |
| --- | --- | --- |
| `_Templates/` | Master templates (never modified) | Internal only |
| `_Archive/` | Closed engagements (90+ days) | Internal only |
| `Client-{{token}}/` | Active engagement workspace | Internal + client (limited) |
| `01-Threat-Model/` | Threat analysis document | Internal |
| `02-Data-Flows/` | Data flow mapping | Internal |
| `03-Findings/` | Findings register | Internal |
| `04-Hardening/` | Pass/fail gates | Internal |
| `05-Executive-Summary/` | Executive summary | Internal |
| `06-Scope-Lock/` | Scope definition | Internal |
| `07-Client-Provided/` | Client uploads | Client: Editor, Internal: Viewer |
| `08-Delivery/` | Final deliverables | Client: Viewer |

---

## Permissions Model

### During Sprint (Active)

| Folder | Client | Internal |
| --- | --- | --- |
| Client root | No access | Owner |
| 01-06 folders | No access | Editor |
| 07-Client-Provided | Editor | Viewer |
| 08-Delivery | No access | Owner |

### At Delivery

| Folder | Client | Internal |
| --- | --- | --- |
| 08-Delivery | Viewer (link) | Owner |
| All other folders | No access | Owner |

### Post-Closure (90 days)

| Folder | Client | Internal |
| --- | --- | --- |
| 08-Delivery | Viewer (link, read-only) | Owner |
| All other folders | No access | Owner |

### Archive (90+ days)

| Action | Result |
| --- | --- |
| Move to _Archive | Folder moved |
| Client access | Revoked |
| Internal access | Owner only |

---

## Naming Conventions

### Folders

```
Client-{{intake_token}}
```

Example: `Client-550e8400-e29b-41d4-a716-446655440000`

### Documents

```
{{Document-Type}}-{{client_name}}.gdoc
```

Example: `Threat-Model-Acme-Corp.gdoc`

### PDFs

```
{{Document-Type}}-{{client_name}}.pdf
```

Example: `Threat-Model-Acme-Corp.pdf`

### ZIP Package

```
Collapse-Ready-Sprint-{{client_name}}.zip
```

Example: `Collapse-Ready-Sprint-Acme-Corp.zip`

---

## Automation Actions (Make)

### Scenario 3: Workspace Creation

1. **Create client folder:**
   - Path: `/Collapse-Ready-Sprints/Client-{{intake_token}}/`

2. **Create subfolders:**
   - `01-Threat-Model/`
   - `02-Data-Flows/`
   - `03-Findings/`
   - `04-Hardening/`
   - `05-Executive-Summary/`
   - `06-Scope-Lock/`
   - `07-Client-Provided/`
   - `08-Delivery/`

3. **Copy templates:**
   - Copy from `_Templates/` to respective folders
   - Rename with client name

4. **Auto-populate:**
   - Replace `{{client_name}}`
   - Replace `{{intake_token}}`
   - Replace `{{sprint_start_date}}`
   - Replace `{{delivery_date}}`

5. **Set permissions:**
   - Client gets Editor on `07-Client-Provided/`
   - All other folders internal only

### Scenario 5: Delivery Package Generation

1. **Export PDFs:**
   - Export each Google Doc to PDF
   - Save to `08-Delivery/`

2. **Generate README.md:**
   - Artifact list
   - Scope summary
   - Residual risks
   - (Optional) SHA256 hashes

3. **Create ZIP:**
   - Include all PDFs + README.md
   - Save as `Collapse-Ready-Sprint-{{client_name}}.zip`

4. **Generate share link:**
   - `08-Delivery/` folder
   - Viewer access
   - Link sharing enabled

### Scenario 6: Post-Delivery

1. **Lock permissions:**
   - Client: Viewer only on `08-Delivery/`
   - Remove any Editor access

2. **Archive (after 90 days):**
   - Move folder to `_Archive/`
   - Revoke all client access

---

## README.md Template (Delivery)

```markdown
# Collapse-Ready Sprint Delivery Package

Client: {{client_name}}
Engagement Token: {{intake_token}}
Delivery Date: {{delivery_date}}

## Contents

| File | Description |
| --- | --- |
| Executive-Summary.pdf | High-level findings and recommendations |
| Threat-Model.pdf | System threat analysis |
| Data-Flow-Map.pdf | Data flow and trust boundaries |
| Findings-Register.pdf | Detailed findings with evidence |
| Pass-Fail-Gates.pdf | Binary assessment criteria |

## Scope Summary

System: {{system_name}}

In Scope:
{{in_scope_summary}}

Out of Scope:
{{out_of_scope_summary}}

## Residual Risks

{{residual_risks_summary}}

## Integrity Verification (Optional)

SHA256 Hashes:
- Executive-Summary.pdf: {{hash_exec}}
- Threat-Model.pdf: {{hash_threat}}
- Data-Flow-Map.pdf: {{hash_data}}
- Findings-Register.pdf: {{hash_findings}}
- Pass-Fail-Gates.pdf: {{hash_gates}}

## Contact

For questions about this delivery, contact via the engagement email.

---
Collapse-Ready Sprint
```

---

## Drive API Endpoints (Reference)

| Action | Endpoint |
| --- | --- |
| Create folder | `files.create` with mimeType `application/vnd.google-apps.folder` |
| Copy file | `files.copy` |
| Update permissions | `permissions.create` |
| Export PDF | `files.export` with mimeType `application/pdf` |
| Generate link | `permissions.create` with type `anyone`, role `reader` |

---

## Security Considerations

- All folders have restricted sharing by default
- Client cannot see internal work folders
- Delivery folder is view-only (no download option if preferred)
- Archive revokes all external access
- Audit log maintained for all access
