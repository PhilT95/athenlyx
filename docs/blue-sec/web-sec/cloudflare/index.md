![Cloudflare Logo](images/cloudflare_Logo.png)
# Cloudflare

Cloudflare is one the largest CDN and WAF providers worldwide with more than 330 PoPs in 125+ countries. Together these PoPs build a network with a network capacity of more than 500 Tbps. Other providers like [Akamai](https://www.akamai.com/de) offer similar features as Cloudflare, but can't compete with its network capacity. This gap is even bigger if you look at the way Cloudflare's PoPs are designed. Each one of them is build the same way, making it possible for every PoP to offer all common Cloudflare CDN and security features while other providers need to forward traffic for certain actions to dedicated *scrubbing centers*. 

This makes Cloudflare an ideal solution for websites suffering DDoS Attacks. But Cloudflare can do more than offering the size of its network, bundling a variety of different security solutions into it's network:

- **WAF**: this component can filter malicious traffic based upon rulesets like OWASP and for example block SQL injections
- **Bot Management**: the Bot Management filters automated traffic. It can differentiate between verified Bots, scraper, crawler, and even AI agents for search and learning.
- **Rate Limiting**: Cloudflare can additionally be used to further limit requests based on IP addresses and other characteristics


!!! warning
    Please be aware that, depending on your Cloudflare license, certain features are only available in a limited capacity or not included at all. Especially the WAF component lacks configurable managed ruleset and the OWASP rules are not available inside the Free plan. Therefore the Free plan only offers a basic security against attacks and malicious requests.


## Basic traffic concept

Cloudflare and most other cloud-based CDN provider uses DNS records for directing the traffic to themselves instead of directly routing it to the so called **origin[^1]** server. Once a requests hits their networks they open the TLS connection, working like a *man-in-the-middle"*. Terminating the TLS connection is required to

- analyze the traffic for malicious behavior, automated traffic or attacks, and block it if needed
- directly replying with cached responses from the CDN network itself
- further limit the traffic based on access rates

Once Cloudflare checked the traffic and, based on the rules and enabled features either blocks the requests or, after verifying its cache, sends a requests towards the origin server. Depending on the Cloudflare configuration the user can also be asked to answer a Cloudflare challenge. These challenges can be non- and interactive.

<!-- vale Google.FirstPerson = NO -->

??? info "Traffic flow with Cloudflare"
    ```mermaid
    graph TB
    A([User requests website]) --> B[User machine resolves DNS request];
    B -->|User gets Cloudflare IP address| C[Request is send to Cloudflare PoP];
    C --> D[Cloudflare analyzes the request];
    D -->|Request is flagged as bad| G([Cloudflare blocks the request]);
    D -->|Request is flagged for challenge| F[User needs to pass a Cloudflare Challenge] --> E;
    D -->|Request flagged as good| E{Is request cached by Cloudflare};
    E -->|Yes| H([Cloudflare sends the cached response to the user]);
    E -->|No| I[Cloudflare sends the requests to the origin server];
    I --> J{Response OK};
    J -->|Yes| K([Cloudflare gets response and sends it to the user]);
    J -->|No| L([Cloudflare sends an error message to the user]);

    B -->|User gets the origin IP address| M([The origin server handles the request itself])

    ```

<!-- vale Google.FirstPerson = Yes -->

## Licensing

Cloudflare's licensing model has multiple tiers. I'd generally separate the tiers into 3 different categories

1. **Free tier**: offers basic capabilities and rudimentary bot management. Suitable for small non-critical projects and domains which only redirect to other domains, for example from example.de.com to example.com.
2. **Self-buyer tier**: comes with enhanced security, feature set, and curated rulesets. Ideal for business sites, applications, and projects.
3. **Enterprise tier**: enables access to the most advanced Cloudflare features and enhanced security capabilities. Also increases ruleset complexity and detection behavior. Ideal for critical business applications.

!!! note
    If certain compliance requirements like data localization (for example GDPR) are a concern the Enterprise tier is the only one where these features can be included.

See the following license comparison with key details. If you need more information please refer to the [Cloudflare website](https://www.cloudflare.com/plans/)

|Feature|Free|Pro|Business|Enterprise|
|:------|:---|:--|:-------|:---------|
|**Full feature DNS**|Yes|Yes|Yes|Yes|
|**Layer 7 DDoS protection**|Yes|Yes|Yes|Yes|
|**CDN**|Yes|Yes|Yes|Yes|
|**Bot mitigation**|Simple bots|Easy-to-detect bots|Sophisticated bots with *Super Bot Fight Mode*|All bots, anomaly detection, custom CAPTCHAs|
|**Bot analytics**|No|No|Basic bot analytics|Advanced bot analytics|



[^1]: The origin the server that hosts the application itself. These are web servers within the Cloudflare context since most of its features are based around web applications.