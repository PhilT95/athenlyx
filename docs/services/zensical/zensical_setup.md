# Zensical Setup on AlmaLinux 10

This guide will help you setup a Zensical project on a AlmaLinux 10 system. This includes the installation and secure configuration ob Zensical and nginx using the `certbot` to easily integrate SSL and create the necessary **LetsEncrypt** certificate.


## Requirements

The Zensical setup is a pretty straight-forward process and does not differ a lot between Linux distributions but there are a few things required..

- [x] A system running AlmaLinux 10 with
    - [X] SSH access
    - [X] Root permissions
    - [X] Internet access
- [X] A basic understanding how to interact with a shell
- [X] Ideally a domain that can point to the system which is supposed to host the Zensical project 

## Setup

### Login & Update

To begin with the Zensical setup, connect to your system using SSH. Once logged in we will make sure the it is fully updated. Since we need root permissions to update the system and will be needing these permissions to install all required components as well we switch into the root session using the ``su`` command.

```bash
sudo su
dnf update -y
```

### Installing Dependencies & Zensical

Once all updates are installed we can continue installing of all Zensical dependencies and Zensical itself.
The only dependency required to install Zensical is `Python3`. It is required to install Zensical and various Python libraries required by the different Zensical extensions.

We will use the built-in package manger to install python and verify its installation.

```bash
dnf install python3
python3 --version
```

Once python is installed we can install all required python components ideally within a separate virtual  Python environment. Since we want to run Zensical without root permission and it is recommended to use the virtual environment without them as well we will continue inside the normal user context.

```bash
exit
python3 -m venv .venv
source .venv/bin/activate
pip install zensical
zensical --version
```

!!! info
    The initial setup does not need more components to be installed. If you want to know more on how to install plugins and extensions, please refer to [this](#extensions-plugins) part of this guide.

### Initialize a basic Zensical project

Zensical offers a quick way to setup a new project with a single command. This will create the necessary files and folders for a basic Zensical website to work.

```bash
zensical new myproject
cd myproject
```

After executing the `zensical new` command and navigating into the newly created directory we can verify it by checking if the project structure resembles the structure below.

```console
.
├── docs
│   ├── index.md
│   └── markdown.md
├── .github
│   └── workflows
│       └── docs.yml
└── zensical.toml
```

To understand what the various files and folders are supposed to be used for here a quick overview

- The `docs` directory is the place where all markdown files, that should be transformed into web pages, will be placed 
    - Within the `markdown.md` basic markdown syntax is provided as a cheat sheet
    - Within the `index.md` file you are able to discover the various editing options that Zensical offers which extend basic markdown features
- The `.github` directory is used by GitHub for its CI/CD pipeline configuration
    - The workflow configured within `docs.yml` aims to provide a quick deployment option using GitHub Pages.
- `zensical.toml` is the main configuration file which defines
    - Basic information about the website
    - Which features are enabled and how they will work
    - If you don't use the default navigation it also contains the website navigation setup.

You can already launch this website using the `zensical serve` command which will spin up a local web server. This is especially useful for debugging and testing. If you want to host your website securely without GitHub pages you'll need to build your project and serve it with a dedicated web server engine like nginx.


!!! info "Zensical Build"
    You can use `zensical build` to generate all files necessary to host the website using nginx. Per default website will the saved to the `site` directory inside the folder where you execute `zensical build`. The directory for this website looks like this:

    ```console
    .
    ├── 404.html
    ├── about
    ├── ai
    ├── assets
    ├── blue-sec
    ├── images
    ├── index.html
    ├── linux-admin
    ├── mkdocs_github_authors.yaml
    ├── objects.inv
    ├── robots.txt
    ├── search.json
    ├── services
    ├── sitemap.xml
    └── stylesheets
    ```

    The structure and files from your project can and should differ to the one shown above.

### Setting up nginx

The web server engine nginx is one of the most reliable and lightweight ones. It is an ideal way to easily and securely host Zensical projects.
Before we can host Zensical using nginx we need to install it, set it up correctly and configure it to run as a background service.

```bash
sudo su
dnf install nginx -y
```

Once nginx is installed navigate to the nginx directory `/etc/nginx`. There we need to create a dedicated nginx configuration file for the project. 

```bash
nano yourwebsite.example.com.conf
```

Copy the following content and edit the domain and the `root` directive inside the second server block. This needs to point towards the Zensical Website directory. The following configuration will redirect all requests via **HTTP**  to the **HTTP** protocol. The second `server` block contains the **HTTP** configuration with certain security and logging features as well as caching configured.

```nginx

server {
    listen 80;
    server_name yourwebsite.example.com;

    if ($host = yourwebsite.example.com) {
        return 301 https://$host$request_uri;
    }

}

server {
        listen 443 ssl;
        server_name yourwebsite.example.com;

        access_log /var/log/nginx/yourwebsite.example.com:443.access.log;
        error_log /var/log/nginx/yourwebsite.example.com:443:error.log;

        ssl_protocols TLSv1.3 TLSv1.2;
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains";
        ssl_stapling on;
        ssl_stapling_verify on;

        root /www
        error_page 404 /404.html;

        add_header X-Content-Type-Options nosniff;

        gzip on;
        gzip_types text/html application/javascript text/css text/xml application/json;

        location ~* .min.(css|js)$ {
                add_header Cache-Control "max-age=604800";
                add_header Surrogate-Control "max-age=604800";
        }

        location /search/search_index.json {
                add_header Cache-Control "max-age=3600";
                add_header Surrogate-Control "max-age=3600";
        }

        location /.minio.sys/ {
                deny all;
        }

}
```

!!! note
    If you don't have a domain name you can also use an IP-Address within the `server_name` directive.

Please note that there is currently no SSL certificate provided for HTTPS, which is required for it to work. It is recommended to use the `certbot` to get a valid LetsEncrypt certificate. `certbot` also takes care of adapting your nginx configuration once it created a valid SSL certificate.

Now we just need to register nginx as a system service and start it.

```bash
systemctl enable nginx
systemctl start nginx
```

Once the nginx service it setup and running we can verify if the Zensical project is reachable using the domain or IP-Address inserted at the `server_name` directive. You might need to edit firewall rules to allow communication via HTTP/HTTPS to reach your web server.

If you want to update the website you only need to update the files within the Zensical project, run `zensical build` and make sure the new files replace the old ones.


## Extensions & Plugins

Most extensions that Zensical is using are provided by the [Python Markdown Extension](https://zensical.org/docs/setup/extensions/python-markdown/) that is usually installed by default with Python itself.

If you want to enable the various features that are provided using this extension please refer to the Zensical documentation itself. To enable and configure these extensions the `zensical.toml` file needs to be edited. You can refer to the toml-file for [this project](https://github.com/PhilT95/athenlyx/blob/main/zensical.toml).




