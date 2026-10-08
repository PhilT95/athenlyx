# Docker container has no internet access

Containers on a Docker Compose network can lose outbound access while the host and the default `docker0` bridge keep working. Typical symptoms are timeouts when a container downloads data, TLS handshakes that hang, or application errors that wait for a remote resource.

## Quick steps

If you have similar problems and need to isolate and narrow down the problem you can follow these few steps that you can run from inside the problematic container.


| Test | Result | Likely cause |
|:-----|:-------|:-------------|
| `ping 1.1.1.1` fails | No route | Forwarding, NAT, or firewall |
| Ping works, `nslookup` fails | No name resolution | DNS |
| Small requests work, HTTPS hangs | Large packets get dropped | **MTU mismatch** |
| `curl -4` works, default hangs | IPv6 route missing | IPv6 |
| Works on `docker0`, fails on Compose network | Network specific | MTU, `internal: true`, firewall rules |


## Troubleshooting steps with an example

Plausible CE, this websites analytics tool returned HTTP `500` errors on `/api/event` which stopped the analytics script from working at all. The cause was a `GenServer.call(ReferrerBlocklist, ...) time out`. The process downloads a spam list from GitHub and answers all requests only after the download finishes. The download hung because of an MTU mismatch on the Compose network.


### Step 1: test the network the container uses
Containers started with `docker run` use `docker0`. Compose uses its own bridge (`br-xxxx`), so always test on the Compose network. Find its name with `sudo docker network ls`.

```bash
NET=<compose-network>
URL=https://raw.githubusercontent.com/matomo-org/referrer-spam-list/master/spammers.txt

# Routing
sudo docker run --rm --network $NET --entrypoint ping curlimages/curl -c2 -W3 1.1.1.1
# DNS and HTTPS (-v shows the resolved addresses, -4 forces IPv4)
sudo docker run --rm --network $NET curlimages/curl -sv -m 10 -o /dev/null $URL
```

In the `curl -v` output, `Host ... was resolved` means DNS works and the `Trying` lines show which addresses are used. Compare the result with the table from before. In the example, ping and DNS worked but the connection timed out, which points to the MTU.

If ping fails, check forwarding and NAT:

```bash
sysctl net.ipv4.ip_forward            # must be 1
sudo iptables -t nat -S POSTROUTING   # needs a MASQUERADE rule for the Compose subnet
sudo docker network inspect $NET --format 'internal={{.Internal}} opts={{json .Options}}'
```

If firewalld is installed, see [firewalld basics](firewalld.md) and add the Docker bridges to the `trusted` zone.

### Step 2: compare the MTU
Large packets are dropped when a Docker bridge uses a higher MTU than the uplink. Small packets, pings and DNS still work, while TLS handshakes with large certificate chains hang.

```bash
ip link show | grep mtu
```

| Interface | MTU | Meaning |
|:----------|:----|:--------|
| `eth0` | 1450 | Uplink |
| `docker0` | 1400 | Works |
| `br-xxxx` (Compose) | 1500 | Higher than the uplink, **fails** |

The `mtu` option in `/etc/docker/daemon.json` only applies to the default bridge. Compose networks do not inherit it.

### Step 3: set the MTU on the compose network
Set an MTU equal to or lower than the uplink MTU in `compose.yml`:

```yaml
networks:
  default:
    driver: bridge
    driver_opts:
      com.docker.network.driver.mtu: 1400
```

Recreate the network so the change applies:

```bash
sudo docker compose down     # do not add -v, it deletes volumes
sudo docker compose up -d
```

Verify the new value and the connection:

```bash
ip link show | grep -E 'br-'
sudo docker run --rm --network $NET curlimages/curl -sS -m 10 -o /dev/null -w '%{http_code}\n' $URL
```

!!! note
    Every Compose project on the host that creates its own network needs the same setting.

## Other causes
- **IPv6 only fails:** `curl -4` works but the default hangs. Disable IPv6 for the service with `sysctls: net.ipv6.conf.all.disable_ipv6=1`.
- **DNS fails:** set `dns: [1.1.1.1, 8.8.8.8]` on the service or `"dns"` in `/etc/docker/daemon.json`.

## Reading container logs
```bash
sudo docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
sudo docker logs --since 15m <container> 2>&1 | grep -iE 'error|exception|\*\*' | tail -50
```
