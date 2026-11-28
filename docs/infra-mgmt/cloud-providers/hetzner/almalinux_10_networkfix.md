# AlmaLinux 10 Hetzner private networking fix

AlmaLinux 10 VMs on Hetzner Cloud that only have private network interfaces lose their outbound connection after every reboot. You can still connect to the VM from inside the private network, but the VM itself can't reach any other device in the network or the internet. This can make services like a web server fail and users can't connect to these services after a reboot.

This guide explains the cause and shows how to fix it permanently, so that the system boots back up with a working connection after every reboot.

## Requirements

- [x] An AlmaLinux 10 VM on Hetzner Cloud with
    - [x] Only a private network interface (no public IPv4 or IPv6)
    - [x] Root access to this VM
- [x] Access to the Hetzner web console
- [x] A private network with a gateway at `10.0.0.1` that routes traffic to the internet, for example through a NAT gateway (custom gateway on a Hetzner VM)

!!! note
    The commands in this guide use the interface `eth0` and the gateway `10.0.0.1`. If your VM uses a different interface name or your network uses a different gateway, adjust the commands accordingly.

## Symptoms

After a reboot the VM has its private IP address, but no default route. Running these two commands brings the connection back until the next reboot:

```bash
nmcli device set eth0 managed yes
ip route add default via 10.0.0.1
```

`nmcli device status` shows `eth0` as `connected (externally)`, and NetworkManager may have created a throwaway profile called `Wired connection 1`.

## Cause

The VM image includes Hetzner's `hc-utils` package. It ships the `udev` rule `/usr/lib/udev/rules.d/81-hc-network-interfaces.rules`, which matches network interfaces with a Hetzner private network MAC address (starting with `86:00:00`). For these interfaces the rule:

1. Starts the `hc-net-ifup@eth0` service, which configures the IP address of the interface.
2. Sets `NM_UNMANAGED=1`, which tells NetworkManager to leave the interface alone.

The `hc-net-ifup` service assigns the IP address, which is why inbound connections still work. It doesn't set a default route, though. Hetzner's private network DHCP doesn't provide a default gateway either, so the VM has no route for outbound traffic.

## Check whether a VM is affected

Run the following commands on the VM:

```bash
udevadm info /sys/class/net/eth0 | grep NM_UNMANAGED
grep -n NM_UNMANAGED /usr/lib/udev/rules.d/81-hc-network-interfaces.rules
systemctl list-units 'hc-net-ifup@*'
nmcli device status
ip route | grep default
```

The VM is affected if one or more of these are true:

- `udevadm` prints `E: NM_UNMANAGED=1`.
- The `hc-utils` rule exists and sets `NM_UNMANAGED`.
- An `hc-net-ifup@eth0` service is running.
- `eth0` shows as `unmanaged`
- No default route exists, or only one you added manually with `ip route add`.

## Fix

This fix turns off the network handling of `hc-utils` and lets NetworkManager configure the interface, including a persistent default route.

!!! warning
    Create a snapshot first if there are not viable backups in place before implementing these changes. Alternatively you can run these steps from the **Hetzner web console** instead of SSH. If something goes wrong during the reboot, you can roll back using any of these ways.

    The console can also be used to avoid a sudden SSH connection drop. 

### Disable the hc-utils network rule

If a file with the same name exists in `/etc/udev/rules.d/`, `udev` uses it instead of the one in `/usr/lib/udev/rules.d/`. A symbolic link to `/dev/null` disables the rule, and package updates don't undo this:

```bash
ln -s /dev/null /etc/udev/rules.d/81-hc-network-interfaces.rules
udevadm control --reload
```

The other `hc-utils` features, such as the volume auto-mount rule `99-hc-volume-automount.rules`, keep working.

### Create a persistent NetworkManager profile

Remove the throwaway profile and create a new one with the default route through `10.0.0.1`:

```bash
nmcli connection delete "Wired connection 1" 2>/dev/null
nmcli connection add type ethernet ifname eth0 con-name private-eth0 \
    ipv4.method auto ipv6.method ignore \
    ipv4.routes "0.0.0.0/0 10.0.0.1 onlink=true" \
    connection.autoconnect yes connection.autoconnect-priority 100
```

The route goes into `ipv4.routes` instead of `ipv4.gateway`, because NetworkManager ignores the gateway setting when the address comes from DHCP. `onlink=true` stops the kernel from rejecting the route if NetworkManager adds it before the `10.0.0.0/16` route exists.

!!! tip
    Don't activate the profile with `nmcli connection up` yet. Leave the current configuration running until the reboot.

### Reboot

Reboot the VM from the web console:

```bash
reboot
```

## Verify

After the reboot, log in through the web console and check the configuration:

```bash
udevadm info /sys/class/net/eth0 | grep NM_UNMANAGED   # prints nothing
systemctl list-units 'hc-net-ifup@*'                   # lists no units
nmcli device status                                    # eth0  ethernet  connected  private-eth0
ip route | grep default                                # default via 10.0.0.1 dev eth0 proto static ...
ping -c3 1.1.1.1
getent hosts almalinux.org
```

The default route must show `proto static`. That means it comes from the NetworkManager profile and survives the next reboot.

## Roll back

To undo the fix, remove the profile and the symbolic link, then reboot:

```bash
nmcli connection delete private-eth0
rm /etc/udev/rules.d/81-hc-network-interfaces.rules
reboot
```

!!! warning
    Run these command from the **Hetzner Web console** instead of using SSH since the connection is going to get cut immediately.

## New VMs

To apply the fix to new VMs right away, add the following cloud-init configuration to the **Cloud config** field when you create the server in the Hetzner Cloud Console:

```yaml
#cloud-config
runcmd:
  - ln -sf /dev/null /etc/udev/rules.d/81-hc-network-interfaces.rules
  - nmcli connection add type ethernet ifname eth0 con-name private-eth0 ipv4.method auto ipv6.method ignore ipv4.routes "0.0.0.0/0 10.0.0.1 onlink=true" connection.autoconnect yes connection.autoconnect-priority 100
power_state:
  mode: reboot
```
