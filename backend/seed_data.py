"""Seed the database with sample knowledge base content for demonstration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import Base, SessionLocal, engine
from app.models import Domain, Project, Source, WebPage
from app.services.indexer import index_web_page

SAMPLE_CONTENT = {
    "Data Retention Policy": """# Data Retention Policy for Clinical Trial Documents

## Overview
All clinical trial documents must be retained for a minimum of 15 years after study completion or regulatory approval, whichever is later. This policy applies to all phases of clinical research.

## Scope
This policy covers:
- Protocol documents and amendments
- Informed consent forms
- Case report forms (CRFs)
- Adverse event reports
- Regulatory submissions and correspondence
- Audit trails and source data verification records

## Retention Periods
| Document Type | Minimum Retention |
|---------------|-------------------|
| Core trial documents | 15 years post-completion |
| Safety reports | 25 years |
| Financial records | 7 years |
| Training records | Duration of employment + 3 years |

## Storage Requirements
Documents must be stored in approved electronic systems with:
- Version control and audit trails
- Role-based access controls
- Regular backup verification
- Disaster recovery capabilities

## Destruction Process
Documents may only be destroyed after written approval from the Data Governance Committee. A certificate of destruction must be filed.""",

    "Project Alpha Charter": """# Project Alpha — Clinical Trial Charter

## Project Overview
Project Alpha is a Phase III randomized, double-blind, placebo-controlled study evaluating the efficacy and safety of Compound X in patients with moderate-to-severe rheumatoid arthritis.

## Compliance Status
**Data Retention Compliance: COMPLIANT**
Project Alpha follows the organization's 15-year data retention policy. All trial documents are stored in the validated eTMF system with full audit trails.

## Key Milestones
- Study initiation: January 2024
- First patient enrolled: March 2024
- Database lock: December 2025 (projected)
- Final CSR: Q2 2026 (projected)

## Document Management
- Primary repository: Veeva Vault eTMF
- Backup repository: SharePoint Clinical Archive
- All documents indexed and searchable within 24 hours of upload

## Team Contacts
- Study Director: Dr. Sarah Chen
- Data Manager: James Rodriguez
- Regulatory Lead: Maria Santos""",

    "Project Beta Charter": """# Project Beta — Observational Study Charter

## Project Overview
Project Beta is a prospective observational study tracking long-term outcomes in patients receiving standard-of-care treatment for type 2 diabetes across 12 clinical sites.

## Compliance Status
**Data Retention Compliance: PARTIALLY COMPLIANT**
Project Beta has implemented the 15-year retention policy for core documents. However, patient-reported outcome (PRO) data from mobile app submissions is currently stored in a non-validated system and requires migration to the approved eTMF by Q3 2025.

## Key Milestones
- Study initiation: June 2023
- Enrollment complete: February 2025
- Interim analysis: Q4 2025
- Study completion: June 2028 (projected)

## Document Management
- Primary repository: SharePoint (legacy)
- Migration to Veeva Vault: In progress (60% complete)
- PRO data: Mobile app backend (migration pending)

## Action Items
1. Complete eTMF migration by September 2025
2. Migrate PRO data to validated system
3. Update retention schedule documentation""",

    "GDPR Compliance Guidelines": """# GDPR Compliance Guidelines for Clinical Data

## Purpose
These guidelines ensure all clinical trial data processing activities comply with the General Data Protection Regulation (GDPR) and applicable national data protection laws.

## Lawful Basis for Processing
Clinical trial data processing is conducted under:
- Explicit consent (Article 6(1)(a) and Article 9(2)(a))
- Scientific research exemption (Article 89)
- Legal obligation for pharmacovigilance reporting

## Data Subject Rights
Participants have the right to:
- Access their personal data
- Request rectification of inaccurate data
- Request erasure (subject to retention requirements)
- Data portability for data provided directly by the subject
- Object to processing in specific circumstances

## Cross-Border Transfers
Data transfers outside the EU/EEA require:
- Standard Contractual Clauses (SCCs), or
- Adequacy decision for the recipient country, or
- Binding Corporate Rules (BCRs)

## Breach Notification
Personal data breaches must be reported to the DPO within 24 hours and to the relevant supervisory authority within 72 hours if they pose a risk to data subjects.""",

    "eTMF System Guide": """# Electronic Trial Master File (eTMF) System Guide

## System Overview
The organization uses Veeva Vault as the primary eTMF system for all clinical trials. The system provides:
- 21 CFR Part 11 compliant electronic signatures
- Automated workflow routing and approvals
- Real-time inspection readiness dashboards
- Integrated quality management

## Access Levels
| Role | Permissions |
|------|-------------|
| Study Team Member | Read + Upload to assigned studies |
| Study Director | Full access to assigned studies |
| QA Reviewer | Read + QC review across studies |
| System Administrator | Full system access |

## Document Upload Process
1. Navigate to the appropriate study workspace
2. Select the correct artifact type from the TMF Reference Model
3. Upload the document with required metadata
4. Route for review and approval
5. System automatically indexes for search within 24 hours

## Integration with Atlas
All eTMF documents are synchronized to Atlas nightly. The sync includes document content, metadata, access controls, and version history. Users can search across all connected eTMF studies through the Atlas search interface.""",
}


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Source).count() > 0:
            print("Database already seeded. Skipping.")
            return

        source = Source(
            name="Clinical Operations Wiki",
            description="Primary knowledge source for clinical operations, compliance, and trial management.",
        )
        db.add(source)
        db.flush()

        domain = Domain(
            source_id=source.id,
            name="Clinical Trials",
            description="Clinical trial operations, compliance, and project documentation.",
        )
        db.add(domain)
        db.flush()

        project_alpha = Project(
            domain_id=domain.id,
            name="Project Alpha",
            description="Phase III rheumatoid arthritis study.",
        )
        project_beta = Project(
            domain_id=domain.id,
            name="Project Beta",
            description="Observational diabetes outcomes study.",
        )
        db.add_all([project_alpha, project_beta])
        db.flush()

        compliance_domain = Domain(
            source_id=source.id,
            name="Regulatory & Compliance",
            description="Regulatory guidelines, GDPR, and compliance policies.",
        )
        db.add(compliance_domain)
        db.flush()

        compliance_project = Project(
            domain_id=compliance_domain.id,
            name="Data Governance",
            description="Data retention, privacy, and governance policies.",
        )
        db.add(compliance_project)
        db.flush()

        pages = [
            WebPage(
                project_id=compliance_project.id,
                title="Data Retention Policy",
                content=SAMPLE_CONTENT["Data Retention Policy"],
                url="https://wiki.example.com/policies/data-retention",
            ),
            WebPage(
                project_id=project_alpha.id,
                title="Project Alpha Charter",
                content=SAMPLE_CONTENT["Project Alpha Charter"],
                url="https://wiki.example.com/projects/alpha/charter",
            ),
            WebPage(
                project_id=project_beta.id,
                title="Project Beta Charter",
                content=SAMPLE_CONTENT["Project Beta Charter"],
                url="https://wiki.example.com/projects/beta/charter",
            ),
            WebPage(
                project_id=compliance_project.id,
                title="GDPR Compliance Guidelines",
                content=SAMPLE_CONTENT["GDPR Compliance Guidelines"],
                url="https://wiki.example.com/compliance/gdpr",
            ),
            WebPage(
                project_id=compliance_project.id,
                title="eTMF System Guide",
                content=SAMPLE_CONTENT["eTMF System Guide"],
                url="https://wiki.example.com/systems/etmf-guide",
            ),
        ]
        db.add_all(pages)
        db.commit()

        print("Seeding content pages...")
        for page in pages:
            db.refresh(page)
            try:
                count = index_web_page(db, page)
                print(f"  Indexed '{page.title}': {count} chunks")
            except ValueError as exc:
                print(f"  Skipped indexing '{page.title}': {exc}")

        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
