"""
netboot target, version 2
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

import os

from catalyst import log
from catalyst.support import (CatalystError, normpath, cmd)
from catalyst.fileops import (ensure_dirs, clear_dir, clear_path)

from catalyst.base.stagebase import StageBase


class netboot2(StageBase):
	"""
	Builder class for a netboot build, version 2
	"""
	def __init__(self,spec,addlargs):
		self.required_values=[
			"boot/kernel"
		]
		self.valid_values=self.required_values[:]
		self.valid_values.extend([
			"netboot2/packages",
			"netboot2/use",
			"netboot2/extra_files",
			"netboot2/overlay",
			"netboot2/busybox_config",
			"netboot2/root_overlay",
			"netboot2/linuxrc"
		])

		try:
			if "netboot2/packages" in addlargs:
				if isinstance(addlargs['netboot2/packages'], str):
					loopy=[addlargs["netboot2/packages"]]
				else:
					loopy=addlargs["netboot2/packages"]

				for x in loopy:
					self.valid_values.append("netboot2/packages/"+x+"/files")
		except:
			raise CatalystError("configuration error in netboot2/packages.")

		StageBase.__init__(self,spec,addlargs)
		self.settings["merge_path"]=normpath("/tmp/image/")

	def set_target_path(self):
		self.settings["target_path"]=normpath(self.settings["storedir"]+"/builds/"+\
			self.settings["target_subpath"])
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("setup_target_path"):
			log.notice('Resume point detected, skipping target path setup operation...')
		else:
			# first clean up any existing target stuff
			clear_path(self.settings['target_path'])
			self.resume.enable("setup_target_path")
		ensure_dirs(self.settings["storedir"]+"/builds/")

	def copy_files_to_image(self):
		# copies specific files from the buildroot to merge_path
		myfiles=[]

		# check for autoresume point
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("copy_files_to_image"):
			log.notice('Resume point detected, skipping target path setup operation...')
		else:
			if "netboot2/packages" in self.settings:
				if isinstance(self.settings['netboot2/packages'], str):
					loopy=[self.settings["netboot2/packages"]]
				else:
					loopy=self.settings["netboot2/packages"]

			for x in loopy:
				if "netboot2/packages/"+x+"/files" in self.settings:
					if isinstance(self.settings['netboot2/packages/'+x+'/files'], list):
						myfiles.extend(self.settings["netboot2/packages/"+x+"/files"])
					else:
						myfiles.append(self.settings["netboot2/packages/"+x+"/files"])

			if "netboot2/extra_files" in self.settings:
				if isinstance(self.settings['netboot2/extra_files'], list):
					myfiles.extend(self.settings["netboot2/extra_files"])
				else:
					myfiles.append(self.settings["netboot2/extra_files"])

			try:
				cmd([self.settings['controller_file'], 'image'] +
					myfiles, env=self.env)
			except CatalystError:
				self.unbind()
				raise CatalystError("Failed to copy files to image!",
					print_traceback=True)

			self.resume.enable("copy_files_to_image")

	def setup_overlay(self):
		if "autoresume" in self.settings["options"] \
		and self.resume.is_enabled("setup_overlay"):
			log.notice('Resume point detected, skipping setup_overlay operation...')
		else:
			if "netboot2/overlay" in self.settings:
				for x in self.settings["netboot2/overlay"]:
					if os.path.exists(x):
						cmd(['rsync', '-a', x + '/',
							self.settings['chroot_path'] + self.settings['merge_path']],
							env=self.env)
				self.resume.enable("setup_overlay")

	def move_kernels(self):
		# we're done, move the kernels to builds/*
		# no auto resume here as we always want the
		# freshest images moved
		try:
			cmd([self.settings['controller_file'], 'final'], env=self.env)
			log.notice('Netboot Build Finished!')
		except CatalystError:
			self.unbind()
			raise CatalystError("Failed to move kernel images!",
				print_traceback=True)

	def remove(self):
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("remove"):
			log.notice('Resume point detected, skipping remove operation...')
		else:
			if self.settings["spec_prefix"]+"/rm" in self.settings:
				for x in self.settings[self.settings["spec_prefix"]+"/rm"]:
					# we're going to shell out for all these cleaning operations,
					# so we get easy glob handling
					log.notice('netboot2: removing %s', x)
					clear_path(self.settings['chroot_path'] +
						self.settings['merge_path'] + x)

	def empty(self):
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("empty"):
			log.notice('Resume point detected, skipping empty operation...')
		else:
			if "netboot2/empty" in self.settings:
				if isinstance(self.settings['netboot2/empty'], str):
					self.settings["netboot2/empty"]=self.settings["netboot2/empty"].split()
				for x in self.settings["netboot2/empty"]:
					myemp=self.settings["chroot_path"] + self.settings["merge_path"] + x
					if not os.path.isdir(myemp):
						log.warning('not a directory or does not exist, skipping "empty" operation: %s', x)
						continue
					log.info('Emptying directory %s', x)
					# stat the dir, delete the dir, recreate the dir and set
					# the proper perms and ownership
					clear_dir(myemp)
		self.resume.enable("empty")

	def set_action_sequence(self):
		self.settings["action_sequence"]=["unpack","unpack_snapshot","config_profile_link",
			"setup_confdir","portage_overlay","bind","chroot_setup",\
			"setup_environment","build_packages","root_overlay",\
			"copy_files_to_image","setup_overlay","build_kernel","move_kernels",\
			"remove","empty","unbind","clean","clear_autoresume"]
