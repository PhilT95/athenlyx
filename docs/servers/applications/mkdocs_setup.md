# MkDocs - Make documentation beautiful (again)
This guide will show you the steps to transform your markdown documentation into a self-hosted web server with navigation and search functions. It will be centered around the Linux distribution **AlmaLinux 9** and **MkDocs**.

## Prerequisites
Before you can install **MkDocs** and its extensions you need to have fulfill these following:

- You have a system where **AlmaLinux 9** is installed
- You have root access on the system
- Your system has access to the Internet
- You have a recent version of `python` installed. The version should at least be > **3.8.2**
- You have `pip` installed. The version should at least be > **20.0.2**

Using `dnf` you can install Python and pip using these commands:

```bash
[user@machine ~]$ sudo dnf install python3 python3-pip
```

Regarding your documentation, I'd recommend to keep nesting of directories up to maximal 4 levels.

## Setup
### mkdocs Installation
The first thing to do is installing **MkDocs** itself using pip. 

```bash
[user@machine ~]$ pip install mkdocs
```

Verify the installation and version of mkdocs.

```bash
[user@machine ~]$ mkdocs --version
mkdocs, version 1.6.1 from /home/user/.local/lib/python3.12/site-packages/mkdocs (Python 3.12)
```
**Material for MkDocs** is a framework based on top of **MkDocs** which offers an extended range of functionality and customization. We will be using it in this guide since its setup is very easy as well.

```bash
[user@machine ~]$ pip install mkdocs-material
```

If this installation is completed, we can begin to prepare the project.

### Setting up your project
Now that you have installed MkDocs we can start to get your project ready to compile the webpage.

First navigate to the root of your documentation and create a new MkDocs project.

```bash
[user@machine ~]$ cd /path/to/your/project
[user@machine project]$ mkdocs new project-name
```

This command will create a new folder `docs` with an **index.md** file and a **mkdocs.yml** file within the root directory of your project.
You directory structure should look like this now:

```bash
/path/to/your/project
├── docs
│   ├── index.md
├── mkdocs.yml
│
...
```

Now you need to move your entire documentation within the `docs` directory. This is needed to compile the webpages accordingly.

### Configuring your project
Once you have all your files in this directory, we can start preparing the **mkdocs.yml** file. Here the entire configuration of your documentation website will be set.

Open the file, for example with the text editor `nano`.

```bash
[user@machine project]$ nano mkdocs.yml
```

The file should look like this:

```yaml
site_name: My Docs
```

First we will adjust the name and url of the website. Change `My Docs` to the name you want to be displayed and add a new line for the URL of the website.

```yaml
site_name: YourProject
site_url: https://example.com
```

Now we can add the navigation, which defines the structure of the pages and how they are ordered. You can make it resemble your actual file structure, but this is not a must. The `nav` parameter works by creating a set of directories and files (webpages), which will be compiled accordingly to the configuration. Here is an example of a simple navigation structure.

```yaml
nav:
    - Home: index.md
    - Cooking & Baking:
        - Cooking Recipes:
            - Meatloaf: path/to/meatloaf.md
            - Enchilada: path/to/enchilada.md
        - Cooking Tools: path/to/cooking_tools.md
```

Adapt this to your needs and add it to your **mkdocs.yml** file.

To use the **Material** theme and get access to its extended functionality, we need to tell MkDocs to use it. We can do that by adding

```yaml
theme:
  name: material
  features:
    - search.suggest
    - navigation.instant
    - navigation.instant.prefetch
    - navigation.tabs
```

to the configuration file. This tell MkDocs to use the **Material** theme and activates the listed features. For more information regarding the **Material Configuration**, please refer to [the Material Documentation](https://squidfunk.github.io/mkdocs-material/setup/).

As a final touch, to enable a powerful search function, add 

```yaml
plugins:
  - search
```

to your configuration file and save it. Your file should look like this now:

```yaml
site_name: YourProject
site_url: https://example.com

nav:
    - Home: index.md
    - Cooking & Baking:
        - Cooking Recipes:
            - Meatloaf: path/to/meatloaf.md
            - Enchilada: path/to/enchilada.md
        - Cooking Tools: path/to/cooking_tools.md

theme:
  name: material
  features:
    - search.suggest
    - navigation.instant
    - navigation.instant.prefetch
    - navigation.tabs

plugins:
  - search
```
### Compiling your project
Now that you have structured your project and configured the configuration file for MkDocs you can build the webpage. 

```bash
[user@machine project]$ mkdocs build
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /path/to/your/project/site
INFO    -  Documentation built in 0.54 seconds
```

The generated files are created and saved to the `site` directory within your project. You can use these files to host your documentation. For hosting you still need a web server, which provides access to these files.
## Hosting your documentation using nginx
To make your files available via http or https, you need to setup a web server. I'll show you how to that using nginx.

The installation of nginx is very simple. For AlmaLinux, just use this command.

```bash
[user@machine project]$ sudo dnf install nginx
```

It should not be very different for other Linux distributions. 


Now we have to configure nginx. Go the the nginx directory as root.

```bash
[user@machine project]$ sudo su
[root@machine project]$ cd /etc/nginx
```

Verify that the following folders `sites-available` and `sites-enabled` are within this directory and if not, create them.  
Edit the the file `nginx.conf` and search the line 
```nginx
include /etc/nginx/conf.d/*.conf;
``` 

and add the following line:

```nginx
include /etc/nginx/sites-enabled/*.conf;
```

Now we have to create the configuration file for our website. Create a new configuration file within `sites-available`. It is standard to name the config file after the domain of your website, for example `myproject.example.org.conf`.

Within the configuration we need to tell nginx when and how it should react on **http** and **https** request. Since we are just hosting a light-weight documentation website, the configuration stays rather simple.

```nginx
server {
    if ($host = myproject.example.org) {
        return 301 https://$host$request_uri;
    }

        listen 80;
        server_name myproject.example.org;

}
server {
        listen 443 ssl;
        server_name myproject.example.org;

        access_log /var/log/nginx/myproject.example.org:443.access.log;
        error_log /var/log/nginx/myproject.example.org:443:error.log;

        location / {
                root /www;
        }

}
```

This configuration is used to redirect all **http** traffic to **https**. If you want to use **http** you can add delete the *if* part of the first *server* bracket and add the same *location*.

```nginx
server {
        listen 80;
        server_name myproject.example.org;

        access_log /var/log/nginx/myproject.example.org:80.access.log;
        error_log /var/log/nginx/myproject.example.org:80:error.log;

         location / {
                root /www;
        }

}
server {
        listen 443 ssl;
        server_name myproject.example.org;

        access_log /var/log/nginx/myproject.example.org:443.access.log;
        error_log /var/log/nginx/myproject.example.org:443:error.log;

        location / {
                root /www;
        }

}
```

As you can see, the root location of the webserver points to the directory ``/www`` in this case. This is the directory where you have to copy the contents of the `/site` folder, which was created during the compilation of the project. You can also change the directory of your nginx configuration to point wherever you want the contents of the web page to reside.

Once the configuration is done, we need to activate the configuration. To do this, we have to create a symbolic link of this file to the `sites-enabled` directory we created earlier.

```bash
[root@machine nginx]$ ln -s /etc/nginx/sites-available/myproject.example.org.conf /etc/nginx/sites-enabled/
```

We quickly test the configuration and if there are no errors, reload nginx.

```bash
[root@machine nginx]$ nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
[root@machine nginx]$ systemctl reload nginx
```

Your website should now be reachable. If you are using SSL, please make sure to setup a certificate or you will run into SSL erros. You can use **certbot** by **LetsEncrypt** to quickly get a valid certificate. The certbot will also edit your nginx configuration to insert your certificate.

## Conclusion
MkDocs is a very easy and simple tool to transform Markdown documentation collections into a simple and easy to navigate web page. With the help of nginx, you can quickly host your own collection.
