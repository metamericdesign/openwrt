


## Quickstart

1. Run `./scripts/feeds update -a` to obtain all the latest package definitions
   defined in feeds.conf / feeds.conf.default

2. Run `./scripts/feeds install -a` to install symlinks for all obtained
   packages into package/feeds/

3. Run `make menuconfig` to select your preferred configuration for the
   toolchain, target system & firmware packages.

4. Run `make` to build your firmware. This will download all sources, build the
   cross-compile toolchain and then cross-compile the GNU/Linux kernel & all chosen
   applications for your target system.

### Extend File System
Prerequisites

`opkg update && opkg install block-mount kmod-fs-ext4 kmod-usb-storage kmod-usb-ohci kmod-usb-uhci e2fsprogs fdisk`

```
DEVICE="$(sed -n -e "/\s\/overlay\s.*$/s///p" /etc/mtab)"
uci -q delete fstab.rwm
uci set fstab.rwm="mount"
uci set fstab.rwm.device="${DEVICE}"
uci set fstab.rwm.target="/rwm"
uci commit fstab
mkfs.ext4 /dev/sda1

DEVICE="/dev/sda1"
eval $(block info "${DEVICE}" | grep -o -e "UUID=\S*")
uci -q delete fstab.overlay
uci set fstab.overlay="mount"
uci set fstab.overlay.uuid="${UUID}"
uci set fstab.overlay.target="/overlay"
uci commit fstab
mount /dev/sda1 /mnt
```
Copy files

`tar -C /overlay -cvf - . | tar -C /mnt -xf -`

Extend complete, just unmount and reboot.

`umount /mnt
reboot`


# OpenVPN
## Install and Add Users
Use the provided script in the home folder to install OpenVPN. Use the servers DNS name as the hostname.
The same script will be used to add users later.

## First time setup
A the following line to the main server config file (/etc/openvpn/server.conf):

`route 172.16.1.0 255.255.255.0`

`client-to-client`


If the server configuration file does not currently reference a client configuration directory, add one now:
`client-config-dir ccd`
In the above directive, ccd should be the name of a directory which has been pre-created in the default directory where the OpenVPN server daemon runs.

### Basestation Clients
Create a file called 'basestation' in the ccd directory. This file should contain the line:
`iroute 172.16.1.0 255.255.255.0`

This will tell the OpenVPN server that the 172.16.1.0/24 subnet (Production LAN) should be routed to from the cloud to the base station.

### Firewall and Routing

Basestation needs to be set to accept forwarding requests. 
Network > Firewall > Firewall - Zone Settings > General > Forward : Accept

Cloud to Production (should be setup on boot)
`iptables -A FORWARD -i tun0 -s 10.8.1.0/24 -d 172.16.1.0/24 -j ACCEPT`

Production to Cloud (should not need this)
`iptables -A FORWARD -i tun0 -s 172.16.0/24 -d 10.8.0.0/24 -j ACCEPT`
