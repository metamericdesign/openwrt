FILE=/root/systemStateFlags/macID.txt
if test -f "$FILE"; then
    echo "$FILE exists."
else 
    echo . /lib/functions/system.sh | get_mac_binary "/proc/device-tree/ethernet@1e100000/mac@0/mac-address" 0 > "$FILE"
fi