---
hide:
    - toc
    - navigation
---

![Image](images/general/athenlyx-high-resolution-logo-transparent.png#only-dark)
![Image](images/general/athenlyx-high-resolution-logo_banner.png#only-light)

# Welcome to Athenlyx.com

This is a collection of documentations, guides and how-to's about general **System Administration**, **App & Service Hosting**, **Cyber Security** and other technical topics built on an **Open-Source Stack**.

<div class="grid cards" markdown>

-   :fontawesome-brands-linux: __Linux Administration__

    ---

    Step-by-step guides for setting up and securing AlmaLinux systems — from initial OS configuration and basic CLI commands to Firewalld, SELinux, and infrastructure automation with Ansible.

    [:octicons-arrow-right-24: Explore](linux-admin/rhel-alma/almalinux_setup.md)

-   :material-shield-check: __Cyber Security — Blue Teaming__

    ---

    Defensive security operations including network traffic analysis with Wireshark, Zeek & Snort, endpoint monitoring with Sysmon & OSquery, SIEM operations with Elastic & Splunk, Wazuh EDR deployment, DFIR methodology, and security assessment with OpenSCAP.

    [:octicons-arrow-right-24: Explore](blue-sec/index.md)

-   :material-server: __Self-Hosted Apps & Services__

    ---

    Deployment guides for server software you can run yourself — including documentation tooling with MkDocs and more to come.

    [:octicons-arrow-right-24: Explore](services/index.md)

-   :material-robot: __AI Security__

    ---

    Resources and tools for securing AI and LLM applications against emerging threats.

    [:octicons-arrow-right-24: Explore](ai/tools-ai.md)

-   :material-account-circle: __About Me__

    ---

    Learn more about the author and the motivation behind this project.

    [:octicons-arrow-right-24: About](about/index.md)

</div>

## Infrastructure Stack

Athenlyx.com is hosted on an **Open-Source Stack** and serves as a real-world example of how open-source products can be combined to host and publish websites securely without proprietary software or licensing costs. The infrastructure is hosted by Hetzner and consists of:

- **OPNSense** — primary Firewall and Gateway
- **SafeLine** — Web Application Firewall (WAF)
- **Nginx** — reverse proxy and web server

## Project Structure

This project is built using Git, [MkDocs](services/mkdocs/mkdocs_setup.md) and the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme. You can find the repository on [GitHub](https://github.com/PhilT95/athenlyx).

---

!!! danger "Legal Notice"
    The content on this website is the author's intellectual property. **Unauthorized use for AI training or any form of automated extraction is strictly prohibited.** Violations will result in a contractual fine of up to **$100,000** per infringement.
