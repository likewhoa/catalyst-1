#!/bin/bash

source ${clst_shdir}/support/functions.sh

case $1 in
	enter)
		${clst_CHROOT} ${clst_chroot_path}
	;;

	run)
		shift
		export clst_grp_type=$1
		shift
		export clst_grp_target=$1
		shift

		export clst_grp_packages="$*"
		exec_in_chroot ${clst_shdir}/grp/grp-chroot.sh
	;;

	preclean)
		exec_in_chroot ${clst_shdir}/grp/grp-preclean-chroot.sh
	;;

	clean)
		exit 0
	;;

	*)
		exit 1
	;;

esac
exit $?
