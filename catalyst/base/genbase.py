
import io
import os


class GenBase(object):
	"""
	This class does generation of the contents and digests files.
	"""
	def __init__(self,myspec):
		self.settings = myspec


	def gen_contents_file(self, path):
		contents = path + ".CONTENTS"
		if os.path.exists(contents):
			os.remove(contents)
		if "contents" in self.settings:
			contents_map = self.settings["contents_map"]
			if os.path.exists(path):
				with io.open(contents, "w", encoding='utf-8') as myf:
					keys={}
					for i in self.settings["contents"].split():
						keys[i]=1
						array = sorted(keys.keys())
					for j in array:
						contents = contents_map.contents(path, j,
							verbose=self.settings["VERBOSE"])
						if contents:
							myf.write(contents)

	def gen_digest_file(self, path):
		digests = path + ".DIGESTS"
		if os.path.exists(digests):
			os.remove(digests)
		if "digests" in self.settings:
			hash_map = self.settings["hash_map"]
			if os.path.exists(path):
				with io.open(digests, "w", encoding='utf-8') as myf:
					keys={}
					for i in self.settings["digests"].split():
						keys[i]=1
						array = sorted(keys.keys())
					for f in [path, path + '.CONTENTS']:
						if os.path.exists(f):
							if "all" in array:
								for k in list(hash_map.hash_map):
									digest = hash_map.generate_hash(f, hash_=k)
									myf.write(digest)
							else:
								for j in array:
									digest = hash_map.generate_hash(f, hash_=j)
									myf.write(digest)
