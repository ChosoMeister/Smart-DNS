# Smart DNS

A minimal implementation of a Shecan-like service. It combines a lightweight DNS server written in Python with an Nginx based transparent proxy. Whitelisted domains resolve to your public IP while all other lookups are resolved normally.

## Repository Structure

| File | Description |
|------|-------------|
| `dns.py` | DNS server using [dnslib](https://github.com/paulc/dnslib). It serves a fixed IP for domains listed in the whitelist and falls back to real DNS resolution for others. |
| `domains` | Default whitelist. Borrowed from [fod](https://github.com/freedomofdevelopers/fod). |
| `nginx.conf` | Nginx configuration that redirects HTTP to HTTPS and forwards TCP traffic on port `443` based on SNI. |
| `entrypoint.sh` | Start script that launches Nginx and the DNS server. |
| `Dockerfile` | Build instructions for the container image. |

## Requirements

- Docker/Podman (recommended)
- Python 3 with `dnslib` if running the DNS server outside of a container

## Usage

1. Ensure ports **53/udp**, **80**, and **443** are free. Disable `systemd-resolved` if necessary.
2. Build the image (optional if using the published one):

   ```bash
   docker build -t smart-dns .
   ```

3. Run the container, replacing `YOUR_PUBLIC_IP` with the address you want whitelisted domains to resolve to:

   ```bash
   docker run -d --net=host -p 53:53/udp -p 80:80 -p 443:443 \
     -e PUB_IP=YOUR_PUBLIC_IP --name smart-dns smart-dns:latest
   ```

### Environment Variables

- `PUB_IP`: IP address returned for whitelisted domains.
- `DNS_ALLOW_ALL=YES`: Ignore the whitelist and respond with `PUB_IP` for every domain.

### Running the DNS server manually

```bash
python3 dns.py --ip ENV --whitelist domains --port 53
```

Use `--ip ENV` to read the IP from the `PUB_IP` environment variable, or supply the IP directly. Set `--whitelist ALL` (or `DNS_ALLOW_ALL=YES`) to allow every domain.

### Testing

Verify functionality with `dig`:

```bash
dig @127.0.0.1 -p 53 fodev.org +short   # returns PUB_IP for whitelisted domain
dig @127.0.0.1 -p 53 google.com +short  # returns real IP for others
```

## FAQ

### Why ports 53, 80, 443 and `--net=host`?

- Port 53 handles DNS queries.
- Ports 80 and 443 receive HTTP/HTTPS traffic for the transparent proxy.
- `--net=host` avoids NAT so Nginx can see the original client IP and process SNI correctly.

## Disclaimer

This project is for educational use. Review the code and configuration before exposing it to untrusted networks.
