#!/bin/bash

export RUN_DEFAULT_FUNCS="no"
export ROOT=/tmp/stage1root

source /tmp/chroot-functions.sh

update_env_settings
show_debug

# Right now these will parse the unpacked stage3 but change things
# inside of /tmp/stage1root due to ROOT env variable
setup_gcc
setup_binutils

# Stage1 is not going to have anything in zoneinfo, so save our Factory timezone
if [ -d "${ROOT}/usr/share/zoneinfo" ]
then
	rm -f "${ROOT}/etc/localtime"
	cp "${ROOT}/usr/share/zoneinfo/Factory" "${ROOT}/etc/localtime"
else
	echo UTC > "${ROOT}/etc/TZ"
fi

# Clean out man, info and doc files
rm -rf "${ROOT}"/usr/share/{man,doc,info}/*
# Zap all .pyc and .pyo files
find "${ROOT}"/ -iname "*.py[co]" -exec rm -f {} \;

# unset ROOT for safety (even though cleanup_stages doesn't use it)
unset ROOT
cleanup_stages
