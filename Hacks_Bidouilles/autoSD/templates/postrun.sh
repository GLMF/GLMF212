#!/bin/bash -e

img_name="$(date +%Y-%m-%d)-${IMG_NAME}${IMG_SUFFIX}"

if [ ! -f ${DEPLOY_DIR}/${img_name}.img ]; then
    sudo unzip ${DEPLOY_DIR}/image_${img_name}.zip -d ${DEPLOY_DIR}
fi

offset_boot=$(sudo parted --script ${DEPLOY_DIR}/${img_name}.img unit B print | tail -n3 | head -n2 | tr -s ' ' | cut -d' ' -f3 | sed s'/B//' | head -n1)
offset_root=$(sudo parted --script ${DEPLOY_DIR}/${img_name}.img unit B print | tail -n3 | head -n2 | tr -s ' ' | cut -d' ' -f3 | sed s'/B//' | tail -n1)

### Operations on boot
log 'Operations on boot'
# Mount /boot
log 'Mount image'
sudo mount -o loop,offset=${offset_boot} ${DEPLOY_DIR}/${img_name}.img /mnt

# Activate ssh
log 'Activate ssh'
sudo touch /mnt/ssh

# Umount /boot
log 'Umount image'
sudo umount /mnt


### Operations on root
log 'Operations on root'
# Mount /
log 'Mount image'
sudo mount -o loop,offset=${offset_root} ${DEPLOY_DIR}/${img_name}.img /mnt

# Copy files
{{#filesLength}}
    log 'Copy files'
    {{#files}}
        sudo cp -R {{{.}}}
    {{/files}}
{{/filesLength}}
{{^filesLength}}
    log 'No file to copy'
{{/filesLength}}

# Copy emulator
log 'Copy emulator'
sudo cp /usr/bin/qemu-arm-static /mnt/usr/bin/

# Mount devices
sudo mount --bind /dev /mnt/dev
sudo mount --bind /sys /mnt/sys
sudo mount -t proc none /mnt/proc

# WORK !
cat << EOF | sudo chroot /mnt 
{{#commands}}
    {{{.}}}
{{/commands}}
EOF

# Remove emulator
log 'Remove emulator'
sudo rm /mnt/usr/bin/qemu-arm-static

# Umount all
sudo umount /mnt/{dev,sys,proc}


### Finalise
# Zip image
log 'Zip image'
sudo 7z a ${DEPLOY_DIR}/image_${img_name}.zip ${DEPLOY_DIR}/${img_name}.img
