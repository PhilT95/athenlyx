# Security Assessments

A **Security Assessment** is a comprehensive evaluation of IT systems & networks as well as security controls to identify vulnerabilities, risks and potential weaknesses that could be exploited by attackers. The goal of these assessments is to measure the effectiveness of existing security measures and ensure that appropriate safeguards are in place. 

There are already plenty of guidelines, policies,  recommendations and standards published by agencies and organizations around the world like the [**DISA**](https://www.disa.mil/) or [**CIS**](https://www.cisecurity.org/). 

## Tools

To automatically check systems against these standards, tools like [**OpenSCAP**](openscap.md) for Linux or the the **SCAP Compliance Checker** for Windows and Linux can be used. These tools use **SCAP**, which is a method to enable automated vulnerability management, measurement and policy compliance evaluation of systems by comparing various settings against the standards defined by agencies and organizations. For example, the DISA, which is operated by the US Department of Defense manages a [Public Exchange Website](https://www.cyber.mil/stigs) where so-called [STIG-files](#stigs) can be found.



### STIGs - Security Technical Implementation Guide

Based on these policies and standards, so called **STIGs** are created and published. A STIG is a configuration standard which contains cyber security related requirements for a specific product like *Windows Server 2019* or *Google Chrome*. These STIG-files can be used with various tools to either manually or automatically check the specific systems settings against the requirements the STIG comes with. 



