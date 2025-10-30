# Digital Forensics and Incident Response

**DFIR** covers the collection of forensic artifacts from digital devices like computers, media devices and phones to investigate an incident by

- Finding evidence of malicious activity in the network and filtering false alarms from real incidents
- Robustly removing the attacker so their access to the network is gone
- Identifying the extent and timeframe of a breach, which assists in communicating with relevant stakeholders
- Finding loopholes that led to the breach, which can give insight into what needs to be changed to avoid further breaches
- Understanding attacker behavior to preemptively block further attempts
- Sharing information about attackers with the cyber security community

Since DFIR requires both expertise in **Digital Forensics** and **Incident Response**, the field is divided into its 2 parts:

- **Digital Forensics**: Requires expertise in identifying forensics artifacts or evidence of human activity in digital devices
- **Incident Response**: Requires expertise in cybersecurity to leverage forensic information for identifying activities of interest from a security perspective

Working in DFIR requires both of these skill sets and these sets are often combined because they are highly co-dependent.

## Basic Concepts

### Artifacts

Artifacts are pieces of evidence that point to an activity performed on a system. When DFIR is performed these artifacts are collected to support a hypothesis or claim about malicious activity. 

!!! example

    A registry key can be an artifact that points toward maintaining persistence on a given system.

### Evidence Preservation

While DFIR is being performed, the integrity of the evidence that is being collected must be maintained. There are established practices that make the preservation easier.

1. Any forensic analysis contaminates the evidence, therefore evidence is first collected and write-protected (read-only)
2. A copy of the write-protected evidence is used for the analysis. No analysis will be done on the original evidence and also assures investigators that there is always a backup.

### Chain of Custody

The Chain of custody defines the secure process of collecting the evidence. Only people relevant to the investigation must be able to access the evidence or the chain of custody will be broken. A broken or contaminated chain of custody can lead to doubts about the integrity of the data and weakens a case being built by adding unknown variables that can't be solved or traced.

### Order of Volatility

Digital evidence is often volatile, which means that it can be lost forever if not captured in time. This can happen when the evidence is stored in a computers system memory (RAM) and will be lost when the computer looses power or is shut down. Therefore it is important to understand the volatility of different evidence sources to capture and preserve data accordingly. 

!!! example

    Evidence that is stored in RAM should be prioritized instead of focusing on data stored on a hard drive.


### Timeline creation

Once all artifacts are collected and their integrity is maintained, they need to be presented transparent to fully use the information contained in them. A timeline of events needs to be created for efficient and accurate analysis. The timeline puts all activities in a chronological order and helps to put a perspective to the investigation which makes it easier to collate information from various sources to create a story of how things happened.