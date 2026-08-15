# Zensical Setup on AlmaLinux 10

This guide will help you setup Zensical on a system running AlmaLinux 10 and how publish them using nginx.


## Requirements

The Zensical setup is a very straight-forward process and does not differ a lot from other Linux distributions but there are a few things that you should have ready.

- [x] A system running AlmaLinux 10 with
    - [X] SSH access
    - [X] Root permissions
    - [X] Internet access
- [X] A basic understanding how to interact with a shell

## Setup

### Login & Update

To begin with the Zensical setup, connect to your system using SSH. Once logged in we will make the system is up-to-date. Since we need root permissions to update the system and will be needing these permissions to install all required components as well we switch into the root session using the ``su`` command.

```console
[user@zensical ~]$ sudo su
[root@zensical user]# dnf update -y
```

### Installation Dependency & Zensical

Once the updates are installed we can continue with the installation of all Zensical dependencies and Zensical itself.

First we will need to ensure that Python3 is installed on the system.

```console
[root@zensical user]# dnf install python3
[root@zensical user]# python3 --version
Python 3.12.13
```

Once python is installed we can install all required python components using a virtual environment. Since it is recommended create this environment without the root permissions within the user context on the local machine that will be used together with Zensical.

```console
[root@zensical user]# exit
[user@zensical ~]$ python3 -m venv .venv
[user@zensical ~]$ source .venv/bin/activate
[user@zensical ~]$ pip install zensical
[user@zensical ~]$ zensical --version
0.0.46
```

!!! info
    For the initial setup this is sufficient. We will discuss the installation of extensions and plugins later.

### Initialize a basic Zensical project

Zensical offers a quick way to setup a new project with a single command. We can verify this by checking the structure and files created. 

```console
[user@zensical ~]$ zensical new myproject
[user@zensical ~]$ cd myproject
```

The following structure with the first pages under `docs`, a workflow for github within the `.github/workflows` directory and the `zensical.toml` file at the root should now exist.

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
- Within the `markdown.md` basic markdown syntax is provided as a cheat sheet
- Within the `index.md` file you are able to discover the various editing options that Zensical offers which extend basic markdown features
- The workflow configured within `docs.yml` aims to provide a quick deployment option using Github Pages.
- `zensical.toml` is the main configuration file which defines
    - Basic information about the website
    - Which features are enabled and how they will work
    - If you don't use the default navigation it also contains the website navigation setup.

You can already launch this website using the `zensical serve` command which will spin up a local webserver. This is especially useful for debugging and testing. If you want to host your website securely without GitHub pages you'll need to build your project and serve it with a dedicated webserver engine like nginx.


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

### Setting up nginx

As one of the most common and simple webservers nginx is ideal to quickly and securely host a Zensical website.
First we need to install nginx, set it up correctly and configure it to run as a background service.

```console
[user@zensical ~]$ sudo su
[root@zensical ~]$ dnf install nginx -y
```

Once nginx is installed navigate to `/etc/nginx`. You need to create a config file inside nginx. The file needs to point to the directory where the output from `zensical build` are located.


```console 
[root@zensical nginx]$ nano yourwebsite.example.com.conf
```

Copy the following content and edit the domain and the `root` directive inside the second server block. This needs to point towards the Zensical Website directory.

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

Please note that there is currently no SSL certificate provided for https, which is required. It is recommended to use the `certbot` to get a valid LetsEncrypt certificate. It will also take care of adapting your nginx configuration once it created a valid SSL certificate.

Now we just need to register nginx as a system service and start it.

```console
[root@zensical nginx]$ systemctl enable nginx
[root@zensical nginx]$ systemctl start nginx
```

Now you can verify if your website is reachable using the domain. You might need to edit firewall rules to allow communication via http/https to reach your webserver.

If you want to update the website you only need to update the files within the Zensical project, run `zensical build` and make sure the new files replace the old ones.





