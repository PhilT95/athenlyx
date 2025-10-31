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

## DFIR Tools

There are various tools that assist with the DFIR process which enhance different capabilities and can save time.

|Tool|Description|
|:---|:----------|
|**Eric Zimmerman's tools**|Eric Zimmerman is a security researcher who has written a few tools that help perform forensic analysis on Windows systems. These tools help analyzing the registry, file system, timeline and more.|
|**KAPE**|KAPE is another tool by Eric Zimmerman. It automates the collection and parsing of forensic artifacts and can help to create a timeline of events.|
|**Autopsy**|Autopsy is an open-source forensics platform that helps analyzing data from digital media like mobile devices, hard drives and removable drives. Various plugins for autopsy speed up the forensic process and extract valuable information from raw data sources.|
|**Volatility**|This tools assists at performing analysis for memory captures from both Windows and Linux systems. It is a powerful tool that can help extract valuable information from the memory of a machine under investigation.|
|**Redline**|Redline is an incident response tool developed and freely distributed by **FireEye**. This tool can gather forensic data from a system and help with collected forensic information.|
|**Velociraptor**|Velociraptor is an advanced endpoint-monitoring, forensics and response platform. It is open-source and very powerful.|

## Incident Response Process

In Security Operations, the prominent use of Digital Forensics is to perform Incident response. Different organizations and agencies have published standardized methods to perform this response. NIST has a defined process in their [SP-800-61 Incident Handling Guide](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r2.pdf), which defines the following steps:

1. Preparation
2. Detection and Analysis
3. Containment, Eradication and Recovery
4. Post-incident Activity

Similarly, SANS has published an [Incident Handler's handbook](https://www.sans.org/white-papers/33901) which defines these steps:

1. Preparation
2. Identification
3. Containment
4. Eradication
5. Recovery
6. Lessons Learned

The steps from SANS and NIST are basically identical, although SANS spreads out the activities into multiple separate steps. Based on SANS, the steps have the following meaning:

1. **Preparation**: Before incidents happen, preparation needs to be done so everything is ready in case of an incident. This includes having required people, processes and technology to prevent and respond to incidents.
2. **Identification**: An incident is identified through indicators in the identification phase. These indicators are then analyzed for False Positives, documented and communicated to the relevant stakeholders.
3. **Containment**: In this phase the incident is contained and efforts are made to limit its effects. There can be short and long-term fixes for containing the threat based on forensic analysis of the incident.
4. **Eradication**: With this step the threat will be eradicated from the network. It has to be ensured that a proper forensic analysis is performed and the threat is effectively contained before eradication. This means, for example, all possible entry points need to be secured so an attacker can't get access again.
5. **Recovery**: Once the threat is removed from the network, the services which have been disrupted are brought back as they were before the incident happened.
6. **Lessons Learned**: Finally, a review of the incident is performed, the incident is documented and steps are taken based on the findings from the incident to make sure that everything is better prepared for the next incident.

