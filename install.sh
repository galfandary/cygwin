#!/bin/bash
mirror=https://mirrors.kernel.org/sourceware/cygwin
target=/tmp/install
cache=/tmp/cache
dwn=0
ist=0
err=0
function hash_check {
    sha512sum -c <<< "$@" 1>/dev/null 2>&1
}
function hash_check_2 {
    local pkg=$1
    local path=$2
    local hash=$3
    local file=$4
    hash_check $hash $file && return 0
    if ((dwn)); then
        echo "Downloading '$pkg' ..."
        mkdir -p $(dirname $file)
        wget -qO $file $mirror/$path
        hash_check $hash $file && return 0
    fi
    echo "Hash check failed: '$hash $file'"
    return 1
}
function do_line {
    local line=$1
    set -- ${line//,/ }
    local level=$1
    local pkg=$2
    local ver=$3
    local path=$4
    local hash=$5
    if [[ -z $hash ]]; then
        echo "Bad line:"
        echo $line
        return 1
    fi
    local file=$cache/$path
    hash_check_2 $pkg $path $hash $file || return 1
    ((ist)) || return 0
    echo "Installing '$pkg' ..."
    mkdir -p $target
    tar -xf $file -C $target
}
function run {
    local line
    while read line; do
        do_line $line || $((err++))
    done
}
while [[ ${1:0:1} == - ]]; do
    if [[ $1 == -m ]]; then
        mirror=$2
        shift 2
    elif [[ $1 == -c ]]; then
        cache=$2
        shift 2
    elif [[ $1 == -i ]]; then
        ist=1
        shift
    elif [[ $1 == -d ]]; then
        dwn=1
        shift
    else
        echo "Unknown option: $1"
        exit 1
    fi
done
run
if ((err)); then
    echo "$err ERRORS"
else
    echo "Done"
fi
