![Cloudflare Logo](images/cloudflare_Logo.png)
# Cloudflare

Cloudflare is the largest CDN and WAF providers with more than 330 PoPs in 125+ countries. Together they build a network with a capacity of more than 500 Tbps which is constantly growing. Other providers like [Akamai](https://www.akamai.com/de) offer the same features as Cloudflare, but can't compete with the network size. This makes Cloudflare an ideal solution for websites suffering DDoS Attacks. But Cloudflare can do more than offering the size of its network, bundling a variety of different security solutions into it's network:

- **WAF**: this component can filter malicious traffic based upon rulesets like OWASP and for example block SQL injections
- **Bot Management**: the Bot Management filters automated traffic. It can differentiate between verified Bots, scraper, crawler, and even AI agents for search and learning.
- **Rate Limiting**: Cloudflare can additionally be used to further limit requests based on IP addresses and other characteristics

An important distinction to similar solution is the way each Cloudflare PoP is build. Most CDN and WAF providers use all their locations for caching but only a few dedicated data centers are capable of checking the traffic for malicious behavior. Cloudflare instead uses the same full-feature configuration for each of the 330+ PoPs. This also improves the service availability since every location can do everything. 


## Basic concept

Cloudflare and basically every other CDN provider uses 2 basic features