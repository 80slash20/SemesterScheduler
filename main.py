import tkinter as tk
from tkinter import *
import validators
import requests

# Constants
PURPLE_COLOUR = (81, 36, 122)
BANNER_TEXT = "SEMESTER SCHEDULER"
BANNER_TEXT_SMALL = "SEM SCHED"
MIN_WIN_SIZE = (400, 200)
COURSE_WORDS = ['Course Code', 'Course Title', 'Coordinating Unit', 'Semester', 'Mode', 'Level', 'Delivery Location', 'Number of Units', 'Contact Hours Per Week']
ASSESSMENT_WORDS = ['Type', 'Learning Objectives Assessed', 'Due Date', 'Weight', 'Task Description']
TYPE_TO_KEYWORDS = {'Assessment': ASSESSMENT_WORDS, 'Course': COURSE_WORDS}

# Functions
def _rgb_to_hex(rgb):
    """
	translates an rgb tuple of integers to (tkinter formatted) hex
    """
    return "#%02x%02x%02x" % rgb

def html_cleaner(html_content: str):
	cleaned_html = []
	in_tag = False
	in_comment = False
	prev = ''
	for character in html_content:
		if character == '<':
			in_tag = True
		elif in_tag and character == '>':
			in_tag = False
		elif character == '/' and prev == '/':
			in_comment = True
		elif in_comment and character == '\n':
			in_comment = False
		elif not in_tag and not in_comment and (not character.isspace() or not prev.isspace()) and character != '\xa0':
			cleaned_html.append(character)
		elif character == '\xa0':
			cleaned_html.append(' ')
		prev = character
	return ''.join(cleaned_html) 

def find_links(html_content):
	links = []
	for word in html_content.split(' '):
		in_link = None
		if "https://" in word:
			link = ""
			for character in word:
				if not in_link and character == "\"":
					in_link = True
				elif in_link and character == "\"":
					in_link = False
				elif in_link:
					link += character
			links.append(link)
	return links

def scrape_webpage(url, focus):
	response = requests.get(url, verify=False)
	html_content = response.text

	cleaned = html_cleaner(html_content)
	
	split_cleaned = cleaned.split('\n')
	
	keyword_values = []
	keywords = TYPE_TO_KEYWORDS[focus]
	keywords_iter = iter(keywords)
	keyword = next(keywords_iter)
	item_found = {keyword: None for keyword in keywords}

	for index, line in enumerate(split_cleaned):
		if keyword in line:
			try:
				value = (line.split(': '))[1]
			except IndexError:
				if keyword == 'Weight':
					value = (split_cleaned[index+1]).split(' ')[0]
				else:
					value = split_cleaned[index+1]
			item_found[keyword] = value
			try:
				keyword = next(keywords_iter)
			except StopIteration:
				keywords_iter = iter(keywords)
				keyword = next(keywords_iter)
				keyword_values.append(item_found)
				item_found = {}
	return keyword_values

def scrape_course_profile(url):
	response = requests.get(url, verify=False)
	html_content = response.text

	links = find_links(html_content)
	
	keyword_values = []
	
	course_info_link = [link for link in links if 'section_1' in link][0]
	assesment_info_link = [link for link in links if 'section_5' in link][0]

	keyword_values.extend(scrape_webpage(course_info_link, 'Course'))
	keyword_values.extend(scrape_webpage(assesment_info_link, 'Assessment'))

# App
class App():
	def __init__(self, root):
		self._root = root
		self._root.geometry("1000x1000")
		self._root.wm_minsize(300, 200)

		self._banner = tk.Frame(self._root, bg=_rgb_to_hex(PURPLE_COLOUR))
		self._banner.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

		self._label = tk.Label(self._banner, text=BANNER_TEXT, font=("Helvetica Neue", "50"), fg=_rgb_to_hex((255, 255, 255)))
		self._label.pack(side=tk.TOP)

		self._label.config(bg=self._banner.cget("bg"))

		self._controls_container = tk.Frame(self._root, height=200, bg=_rgb_to_hex(PURPLE_COLOUR))
		self._controls_container.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
		
		self._entry_profile = tk.Entry(self._controls_container)
		self._entry_profile.pack(side=tk.TOP)
		self._entry_profile.insert(0, "Link to subject profile") 

		self._entry_profile_button = tk.Button(self._controls_container, text='Scrap profile', action=self.create_new_subject(self._entry_profile.get()))
		self._entry_profile.pack(side=tk.RIGHT)

		self._root.bind("<Configure>", self._on_resize)

	def _on_resize(self, event):
		width = event.width
		if width < 580:
			self._label.config(text=BANNER_TEXT_SMALL)
		else:
			self._label.config(text=BANNER_TEXT)
	def create_new_subject(url):
		if validators.url(url):
			scrape_course_profile(url)

class Subject():
	def __init__(self, course_code, course_title, ):
		self._course_code = course_code
		self._course_title = course_title
		pass
	def get_course_code(self):
		return self._course_code
	def get_type(self):
		return self._type
	def __eq__(self, other):
		return other.get_course_code() == self.get_course_code()
	def __repr__(self):
		return str(self._course_code)

class Assessment():
	def __init__(self, name, subject, releasedate, duedate, result, weight):
		self._name = name
		self._subject = subject
		self._releasedate = releasedate
		self._duedate = duedate
		self._result = result
		self._weight = weight
	def get_result(self):
		return self._result
	def get_subject(self):
		return self._subject
	def predict_result(self, past_assesments):
		filtered = [assessment.get_result() for assessment in past_assesments if assessment.get_subject().get_type() == self.get_subject().get_type()]
		
if __name__ == "__main__":
	root = tk.Tk()
	app = App(root)
	root.mainloop()
