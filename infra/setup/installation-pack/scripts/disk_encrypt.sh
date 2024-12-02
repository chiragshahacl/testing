#!/bin/bash

DISK="$1"
KEYFILE="$2"

if [[ -z "$DISK" || -z "$KEYFILE" ]]; then
	echo "Usage: $0 /dev/<device-name> /etc/data-disk-keyfile"
	exit 1
fi

# Unmount the filesystem
umount "$DISK"

# Eliminate any existing processes that might be using the disk
fuser -cuk "$DISK"

# Run a filesystem check
e2fsck -f "$DISK"

# Make the filesystem slightly smaller to make space for the LUKS header
BLOCK_SIZE=`dumpe2fs -h $DISK | grep "Block size" | cut -d ':' -f 2 | tr -d ' '`
BLOCK_COUNT=`dumpe2fs -h $DISK | grep "Block count" | cut -d ':' -f 2 | tr -d ' '`
SPACE_TO_FREE=$((1024 * 1024 * 32)) # 16MB should be enough
NEW_BLOCK_COUNT=$(($BLOCK_COUNT - $SPACE_TO_FREE / $BLOCK_SIZE))
resize2fs -p "$DISK" "$NEW_BLOCK_COUNT"

# Create a keyfile if it doesn't exist
if [[ -f ${KEYFILE} ]]; then
  echo "Keyfile already exists."
else
  echo "Creating keyfile"
  dd if=/dev/urandom of=${KEYFILE} bs=2048 count=2
fi

# Run the encryption process
echo "yes" | cryptsetup reencrypt --encrypt --reduce-device-size 16M "$DISK" --key-file=${KEYFILE}

# Resize the filesystem to fill up the remaining space (i.e. remove the safety margin from earlier)
cryptsetup open "$DISK" cryptdata --key-file=${KEYFILE}
resize2fs /dev/mapper/cryptdata
mount /dev/mapper/cryptdata /opt/local-path-provisioner/
