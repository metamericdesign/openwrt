


### Quickstart

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

`tar -C /overlay -cvf - . | tar -C /mnt/sda1 -xf -`

Extend complete, just unmount and reboot.

`umount /mnt
reboot`

