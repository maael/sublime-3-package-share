import sublime, sublime_plugin, json
from os import listdir
from os.path import isfile, join
import requests

settings = sublime.load_settings('Package Share.sublime-settings')
print(settings.get('fetch_on_start'))

class remote():
	def get(self):
		try:
			r = requests.get('https://api.subshare.com/user')
		except requests.exceptions.RequestException:
			sublime.status_message('Failed to get users subshare')
		else:
			if(r.status_code == 200):
				sublime.status_message(r.json())
			else:
				sublime.status_message('Failed to get users subshare')
	def post(self, data):
		try:
			r = requests.post('https://api.subshare.com/user')
		except requests.exceptions.RequestException:
			sublime.status_message('Failed to save users subshare')
		else:
			sublime.status_message('Saved users subshare')

class userFiles():
	def get(self):
		userPackagePath = join(sublime.packages_path(), "User")
		#self.files = [ f for f in listdir(userPackagePath) if (isfile(join(userPackagePath,f)) and f.endswith(".sublime-settings")) ]
		self.files = ["Preferences.sublime-settings", "Package Control.sublime-settings"]
		self.data = {}
		for file in self.files:
			with open(join(userPackagePath, file)) as data_file:
				self.data[file] = json.load(data_file)
		return self.data
	def save(self, data):
		for file in data:
			filepath = join(sublime.packages_path(), "User", file + "-backup")
			with open(filepath, 'w') as fout:
				fout.write(json.dumps(data[file], indent=4, sort_keys=True))		

class sharerExportCommand(sublime_plugin.WindowCommand):
	def run(self):
		files = userFiles().get()

class sharerImportCommand(sublime_plugin.WindowCommand):
	def run(self):
		data = userFiles().get()
		files.save(data)

class sharerFetchCommand(sublime_plugin.WindowCommand):
	def run(self):
		remote().get()

class sharerUploadCommand(sublime_plugin.WindowCommand):
	def run(self):
		files = userFiles()
		remote().post(files.get())