import sublime, sublime_plugin, json
from os import listdir
from os.path import isfile, join
import requests

settings = sublime.load_settings('Package Share.sublime-settings')
sudo_settings = {
	'auth': {
		'id': 'ID',
		'secret': 'SECRET'
	},
	'current_config': 'Clock'
}

class remote():
	url = 'http://127.0.0.1:3000/api/'
	def get(self, api):
		try:
			r = requests.get(self.url + api, auth=(sudo_settings['auth']['id'], sudo_settings['auth']['secret']))
		except requests.exceptions.RequestException:
			sublime.status_message('Failed to get users package share profile')
		else:
			if(r.status_code == 200):
				return r.json()
			else:
				sublime.status_message('Failed to get users package share profile')
	def post(self, api, data):
		try:
			print(settings.get('fetch_on_start'))
			print(settings.get('auth'))
			headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
			r = requests.post(self.url + api,data=json.dumps(data), headers=headers, auth=(sudo_settings['auth']['id'], sudo_settings['auth']['secret']))
		except requests.exceptions.RequestException:
			sublime.status_message('Failed to save users package share profile')
		else:
			if(r.status_code == 200):
				print(r.json())
				sublime.status_message('Saved users subshare')
			else:
				print(r)
				sublime.status_message('Failed to save users package share profile')

class userFiles():
	def get(self):
		userPackagePath = join(sublime.packages_path(), "User")
		#self.files = [ f for f in listdir(userPackagePath) if (isfile(join(userPackagePath,f)) and f.endswith(".sublime-settings")) ]
		self.files = ["Preferences.sublime-settings", "Package Control.sublime-settings"]
		self.data = []
		for file in self.files:
			with open(join(userPackagePath, file)) as data_file:
				jsonData = json.load(data_file)
				jsonData['file_name'] = file
				self.data.append(jsonData)
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
	configs = None
	def run(self):
		configOptions = []
		self.configs = remote().get('configs')
		for config in self.configs:
			selectedConfig = ' ★' if (sudo_settings['current_config'] == config['name']) else ''
			configOptions.append([config['name'] + ' | ' + config['author']['name'] + selectedConfig, config['description'], 'Use v' + config['version']])
		return sublime.active_window().show_quick_panel(configOptions,self.selected,sublime.KEEP_OPEN_ON_FOCUS_LOST)
	def selected(self, option):
		print('PackageShare: loading ' + self.configs[option]['author']['name'] + "'s " + self.configs[option]['name'] + ' config')

class sharerUploadCommand(sublime_plugin.WindowCommand):
	def run(self):
		files = userFiles()
		remote().post('configs', files.get())

class sharerSaveCurrentAsNew(sublime_plugin.WindowCommand):
	configName = None
	configDescription = None
	def run(self):
		return sublime.active_window().show_input_panel("Configuration Name", "", self.on_named, None, None)
	def on_named(self, name):
		self.configName = name
		return sublime.active_window().show_input_panel("Configuration Description", "", self.save, None, None)
	def save(self, description):
		self.configDescription = description
		files = userFiles().get()
		config = {'name': self.configName, 'description': self.configDescription, 'files': files }
		config = json.dumps(config, separators=(',',':'))
		print(config)
		remote().post('configs', config)


class sharerSaveCurrent(sublime_plugin.WindowCommand):
	def run(self):
		print('Saving')

class sharerUpdateCurrent(sublime_plugin.WindowCommand):
	def run(self):
		print(sudo_settings['auth']['id'])
		print('Updating')