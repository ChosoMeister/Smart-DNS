# private-shecan
# Build Your Own Shecan

`Shecan` is an anti-sanction service offered by a group of researchers in Iran. It allows you to use a different DNS server and have a transparent proxy for the whitelisted domains. 

Since Security and Privacy audits have no place in Iran, and `Shecan` obviously hasn't been through proper vetting, I decided to re-engineer something similar to it for personal use.

# Requirements

- Docker/podman(recommended)

# Proxied Domains

- Included in `domains` file inside the repository. "borrowed" from [fod](https://github.com/freedomofdevelopers/fod)

# How to Use

- make sure ports 80, 443 and 53 are not used in your system (probably a good idea to disable `systemd-resolvd` service)
- run the command in your server (remember to replace YOUR_PUBLIC_IP with you public facing IP address)

`docker run -d -p 53:53/udp -p 443:443 -p 80:80 --net=host -e PUB_IP=YOUR_PUBLIC_IP --name some-private-shecan chosomeister/private-shecan:latest`

# FAQ

## Why all these ports and also --net=host

Port 53 is used to recieve DNS and act as a DNS server. port 80 and 443 recieve HTTP traffic and handle the proxy side.

`--net=host` is needed because your Container engine will use NAT to push traffic to 443, and since your original IP will be masked from Nginx, it won't be able to handle proxy requests. 
