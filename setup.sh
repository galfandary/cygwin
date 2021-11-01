#!/bin/bash
url=https://mirrors.kernel.org/sourceware/cygwin
ini=/etc/setup/setup.ini
pkg=setup
ext=xz
tmp=/tmp/$pkg
rm -f $tmp
echo "Downloading new setup ..."
if ! wget -qO $tmp.$ext $url/$MACHTYPE/$pkg.$ext; then
    echo "Failed to download setup"
    exit 1
fi
if ! unxz $tmp.$ext; then
    echo "Failed to unzip setup"
    exit 1
fi
if diff -q $tmp $ini 1>/dev/null 2>&1; then
    echo "No change to setup"
    rm -f $tmp
    exit 0
fi
while [[ ${1:0:1} == - ]]; do
    if [[ $1 == -m ]]; then
        mirror=$2
        shift 2
    elif [[ $1 == -i ]]; then
        cache=$2
        shift 2
    else
        echo "Unknown option: $1"
        exit 1
    fi
done
echo "Updating setup ..."
[[ -s $ini ]] && cp -p $ini $tmp.old
mkdir -p $(dirname $ini)
cp -p $tmp $ini
