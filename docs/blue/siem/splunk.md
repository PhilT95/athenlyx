# Splunk

Splunk consist of three main components:

- **Forwarder**
- **Indexer**
- **Search Head**


## Splunk Forwarder

The **Splunk Forwarder** is a lightweight agent installed on endpoints intended to be monitored and its main task is to collect the data and send it to the Splunk instance. It does not affect the endpoint's performance since its lightweight implementation. Some key data sources are:

- Web server generating web traffic
- Windows machines generating [Windows Event Logs](../endpoint-security/windows/windows_event_logs.md), PowerShell and [Sysmon](../endpoint-security/windows/sysmon.md)
- Linux hosts generating host-centric logs
- Databases generating database connection requests, responses and errors


## Splunk Indexer

The **Splunk Indexer** plays the main role in processing the data it receives from forwarders. It takes data, normalizes it into field-value pairs, determines the datatype of the data and stores them as events. Processed data is easier to search and analyze.


## Search Head

The **Splunk Search Head** is within the **Search & Reporting App** of Splunk where users can search the indexed logs. When users are searching for a term or use a Search language known as the **Splunk Search Processing Language**, the request is sent to the indexer and the relevant events are returned in the form of field-value pairs.

