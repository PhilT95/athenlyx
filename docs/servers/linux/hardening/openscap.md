# OpenSCAP

[OpenSCAP](https://www.open-scap.org/) provides a wide variety of hardening guides configuration baselines. It also offers tools to evaluate systems against these baselines.

## Installing OpenSCAP on AlmaLinux

The installation of **OpenSCAP** on AlmaLinux systems is rather easy. You need to install the tool to scan and evaluate your system and the guidelines and profiles that are used for this evaluation.

```bash-session
[root@system user]# dnf install openscap-scanner
[root@system user]# dnf install scap-security-guide
```

The first command installs the scanner and the second one the profiles that are relevant to the current system. The installation of both can be verified by confirming that the right profiles are installed. The XML that defines these can be found within the ``/usr/share/xml/scap/ssg/content/`` directory.

```bash-session
[root@system user]# oscap info /usr/share/xml/scap/ssg/content/ssg-almalinux10-ds.xml
Document type: Source Data Stream
Imported: 2025-07-15T00:00:00

Stream: scap_org.open-scap_datastream_from_xccdf_ssg-almalinux10-xccdf.xml
Generated: 2025-07-15T00:00:00
Version: 1.3
Checklists:
        Ref-Id: scap_org.open-scap_cref_ssg-almalinux10-xccdf.xml
                Status: draft
                Generated: 2025-07-15
                Resolved: true
                Profiles:
                        Title: ANSSI-BP-028 (enhanced)
                                Id: xccdf_org.ssgproject.content_profile_anssi_bp28_enhanced
                        Title: ANSSI-BP-028 (high)
                                Id: xccdf_org.ssgproject.content_profile_anssi_bp28_high
                        Title: ANSSI-BP-028 (intermediary)
                                Id: xccdf_org.ssgproject.content_profile_anssi_bp28_intermediary
                        Title: ANSSI-BP-028 (minimal)
                                Id: xccdf_org.ssgproject.content_profile_anssi_bp28_minimal
                        Title: DRAFT - CIS AlmaLinux OS 10 Benchmark for Level 2 - Server
                                Id: xccdf_org.ssgproject.content_profile_cis
                        Title: DRAFT - CIS AlmaLinux OS 10 Benchmark for Level 1 - Server
                                Id: xccdf_org.ssgproject.content_profile_cis_server_l1
                        Title: DRAFT - CIS AlmaLinux OS 10 Benchmark for Level 1 - Workstation
                                Id: xccdf_org.ssgproject.content_profile_cis_workstation_l1
                        Title: DRAFT - CIS AlmaLinux OS 10 Benchmark for Level 2 - Workstation
                                Id: xccdf_org.ssgproject.content_profile_cis_workstation_l2
                        Title: Australian Cyber Security Centre (ACSC) Essential Eight
                                Id: xccdf_org.ssgproject.content_profile_e8
                        Title: Health Insurance Portability and Accountability Act (HIPAA)
                                Id: xccdf_org.ssgproject.content_profile_hipaa
                        Title: Australian Cyber Security Centre (ACSC) ISM Official - Base
                                Id: xccdf_org.ssgproject.content_profile_ism_o
                        Title: Australian Cyber Security Centre (ACSC) ISM Official - Secret
                                Id: xccdf_org.ssgproject.content_profile_ism_o_secret
                        Title: Australian Cyber Security Centre (ACSC) ISM Official - Top Secret
                                Id: xccdf_org.ssgproject.content_profile_ism_o_top_secret
                        Title: PCI-DSS v4.0.1 Control Baseline for Red Hat Enterprise Linux 10
                                Id: xccdf_org.ssgproject.content_profile_pci-dss
                        Title: Red Hat STIG for Red Hat Enterprise Linux 10
                                Id: xccdf_org.ssgproject.content_profile_stig
                        Title: Red Hat STIG for Red Hat Enterprise Linux 10
                                Id: xccdf_org.ssgproject.content_profile_stig_gui
                Referenced check files:
                        ssg-almalinux10-oval.xml
                                system: http://oval.mitre.org/XMLSchema/oval-definitions-5
                        ssg-almalinux10-ocil.xml
                                system: http://scap.nist.gov/schema/ocil/2
```

!!! note
    You can see that the XML file is already named after the distribution and version the system is running on.

## Evaluating the system

OpenSCAP provides a easy to read and handy **HTML** bases report. You can create a report based on the selected profile.

```bash-session
[root@system user]# oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_cis --results-arf arf.xml --report system-cis2.html /usr/share/xml/scap/ssg/content/ssg-almalinux10-ds.xml
```

This will generate a report based on the **CIS Level 2 Benchmark** profile. Any other profile can be selected depending on the compliance requirements for the system.

