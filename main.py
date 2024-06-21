import tkinter as tk
from tkinter import *
import requests
from typing import *

# Constants
PURPLE_COLOUR = (81, 36, 122)
BANNER_TEXT = "SEMESTER SCHEDULER"
BANNER_TEXT_SMALL = "SEM SCHED"
MIN_WIN_SIZE = (400, 200)
COURSE_WORDS = ['Course Code', 'Course Title', 'Coordinating Unit', 'Semester', 'Mode', 'Level', 'Delivery Location', 'Number of Units', 'Contact Hours Per Week']
ASSESSMENT_WORDS = ['Type', 'Learning Objectives Assessed', 'Due Date', 'Weight', 'Task Description']
TYPE_TO_KEYWORDS = {'Assessment': ASSESSMENT_WORDS, 'Subject': COURSE_WORDS}

# Functions
def create_subject_class(identifier: str, name: str, **attrs: Optional[List[str]]) -> classmethod:
	"""
	A class factory for the Subject classmethod. 
	This will be defined by the user based on how their university stores Subject data.

	Parameters:
		<identifier>: string or int that uniquely identifies the subject.
		The identifier is the NAME of the attribute that identifies the subject.
		Examples of good identifier names: 'Course code' 'Subject ID'
		<name>: string that is the subject name.
		The name is the NAME of the attribute that is the subject name.
		Examples of good name names: 'Subject name' 'Name'
		<attrs>: list of strings that serve to be the names of required attributes in any instance.

	Preconditions:
		An <identifier> and <name> are supplied. The <identifier> is either a string or int and
		the name is a string.

	Note:
		Please, please, please DO NOT provide values as the names of the class attributes.
		Once you have created the class using the class factory with relevant names,
		you then may create instances of the class.
		The reason why a user is allowed to 'define' the subject attributes is that
		different universities may store their subject data differently and have different attributes!
		This just makes it easier to then convert the Subject instance into a row in a DB.
		(We can then update the table definition to have more fields/attributes)
	"""
	class Subject():
		IDENTIFIER = identifier
		NAME = name
		def __init__(self, **kwargs):
			for key, value in kwargs.items():
				if key in attrs or key == Subject.IDENTIFIER:
					setattr(self, key, value)
				else:
					raise AttributeError(f"Attribute '{key}' not allowed for {self.__class__.__name__}")
				
				undefined = [attr for attr in attrs if attr not in vars(self)]

				if undefined:
					raise AttributeError(f"Undefined attributes '{undefined}' in instance of {self.__class__.__name__}")
		def __eq__(self, other):
			if type(self) == type(other):
				return bool(self.IDENTIFIER == other.IDENTIFIER)
			else:
				return bool(self.IDENTIFIER == other)
		def __repr__(self):
			return self.NAME
		def __str__(self):
			return self.NAME
		def get_type(self):
			if len(self.IDENTIFIER) == 8 and self.IDENTIFIER[0:5].isalpha() and self.IDENTIFIER[4:].isnumeric():
				return self.IDENTIFIER[0:5]
	return Subject()


def create_assessment_class(identifier: str, name: str, **attrs: List[str]) -> classmethod:
	"""
	A class factory for the Assessment classmethod. 
	This will be defined by the user based on how their university stores Assessment data.

	Parameters:
		<identifier>: string or int that uniquely identifies the assessment.
		The identifier is the NAME of the attribute that identifies the assessment.
		Examples of good identifier names: 'Assessment code' 'Assessment ID'
		<name>: string that is the assessment name.
		The name is the NAME of the attribute that is the assessment name.
		Examples of good name names: 'Assessment name' 'Name'
		<attrs>: list of strings that serve to be the names of required attributes in any instance.

	Preconditions:
		An <identifier> and <name> are supplied. The <identifier> is either a string or int and
		the name is a string.

	Note:
		Please, please, please DO NOT provide values as the names of the class attributes.
		Once you have created the class using the class factory with relevant names,
		you then may create instances of the class.
		The reason why a user is allowed to 'define' the assessment attributes is that
		different universities may store their assessment data differently and have different attributes!
		This just makes it easier to then convert the Assessment instance into a row in a DB.
		(We can then update the table definition to have different fields/attributes)
	"""
	class Assessment():
		IDENTIFIER = identifier
		NAME = name
		def __init__(self, **kwargs):
			for key, value in kwargs.items():
				if key in attrs or key in (Assessment.IDENTIFIER, Assessment.NAME):
					setattr(self, key, value)
				else:
					raise AttributeError(f"Attribute '{key}' not allowed for {self.__class__.__name__}")
				
				undefined = [attr for attr in attrs if attr not in vars(self)]

				if undefined:
					raise AttributeError(f"Undefined attributes '{undefined}' in instance of {self.__class__.__name__}")
			
		def get_result(self):
			return self._result
		def get_subject(self):
			return self._subject
		def predict_result(self, past_assesments):
			filtered = [assessment.get_result() for assessment in past_assesments if assessment.get_subject().get_type() == self.get_subject().get_type()]
	return Assessment()


def rgb_to_hex(rgb: Tuple[int]):
    """
	Translates an rgb tuple of integers to hex.

	Parameters:
		<rgb>: tuple of three integers from 0-255. E.g. (255, 255, 255) - white.

	Preconditions:
		<rgb> is a tuple of three integers that are integers between 0-255 inclusive.
	
	Notes:
		Does not check validity.

	>>> rgb_to_hex(1,1,1)
	
    """
	# %02x is a format specifier that converts an integer to hex. 
	# see: https://www.geeksforgeeks.org/string-formatting-in-python/
    return "#%02x%02x%02x" % rgb


def html_cleaner(html_content: str):
	"""
	A cleaner that removes HTML tags, double spaces and comments from a string of HTML content.
	Also removes \xa0 (non-breaking space)
	Does not remove scripts or superfluous newlines.

	Parameters:
		<html_content>: string of a HTML webpage.

	Preconditions:
		Properly formatted HTML with no malformed tags. 
		Comments are of the form //% where % is a wildcard for a string of any length.

	Note:
		For more sophisicated cleaning, BeautifulSoup should be used.
		This is sufficient for my purposes.
	"""
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
		elif not in_tag and not in_comment and (not character.isspace() or not prev.isspace()):
			if character == '\xa0':
				character = ' '
			cleaned_html.append(character)
		prev = character
	return ''.join(cleaned_html) 


def find_links(html_content):
	"""
	Finds all strings in the following format:
	'https://%'
	Where % is a wildcard character representing a string of any length. 

	Parameters:
		<html_content>: string of a html webpage.
	
	Preconditions:
		HTML syntax is correct.
		All links in <html_content> are HTTPS not HTTP etc.
		This is because in properly formatted HTML, all links will be of the form href='https://%' or src='https://%'.
		Also assumes that the link is not broken - no links can contain spaces.
	
	Note:
		Does not check whether a url is valid. Just finds 'link-like' strings.

	>>> html_content = "<h1>Look at this lovely link:</h1><a href='https://google.com'>Lovely Link</a>"
	>>> find_links(html_content)
	https://google.com
	"""
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
	"""
	Pings the <url> and gets the html content.
	The keywords are found based on the <focus> of the scraping.
	Finds all strings that succeed the keyword in the same line.
	Returns a dictionary that maps all the keywords to those
	relevant strings.

	Parameters:
		<url>: string which is a valid url.
		<focus>: string that is mapped to some set of user-defined keywords.

	Preconditions:
		<focus> is either Subject or Assessment.
	"""
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
	"""
	Finds all link-like strings in <url>
	and gets the html_content. That html content is then 'cleaned.'
	Then scrapes the webpage data for user-defined keywords.
	"""
	response = requests.get(url, verify=False)
	html_content = response.text

	links = find_links(html_content)
	
	keyword_values = []
	
	course_info_link = [link for link in links if 'section_1' in link][0]
	assesment_info_link = [link for link in links if 'section_5' in link][0]

	keyword_values.extend(scrape_webpage(course_info_link, 'Course'))
	keyword_values.extend(scrape_webpage(assesment_info_link, 'Assessment'))

def create_new_subject(url):
	print(url)

class Controller():
	"""
	The controller class of the app.
	Generates the callables for button binds in view.
	Manages indirect interaction between the view and model.
	"""
	pass

class QuickActions():
	def __init__(self, root):
		self._root = root

		self._controls_container = tk.Frame(self._root, height=200, bg=rgb_to_hex(PURPLE_COLOUR))
		self._controls_container.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
		
		self._entry_profile = tk.Entry(self._controls_container)
		self._entry_profile.pack(side=tk.TOP)
		self._entry_profile.insert(0, "Link to subject profile") 

		self._entry_profile_button = tk.Button(self._controls_container, text='Scrape profile', action=create_new_subject(self._entry_profile.get()))
		self._entry_profile_button.pack(side=tk.TOP)

class View():
	"""
	The view class of the app.
	Handles all tkinter widgets.

	Note:
		button binds are generated in the controller class.
	"""
	def __init__(self, root, button_binds: Optional[List[Callable]]):
		self._root = root
		self._root.geometry("1000x1000")
		self._root.wm_minsize(300, 200)

		self._banner = tk.Frame(self._root, bg=rgb_to_hex(PURPLE_COLOUR))
		self._banner.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

		self._label = tk.Label(self._banner, text=BANNER_TEXT, font=("Helvetica Neue", "50"), fg=rgb_to_hex((255, 255, 255)))
		self._label.pack(side=tk.TOP)

		self._label.config(bg=self._banner.cget("bg"))

		self._root.bind("<Configure>", self._on_resize)

	def _on_resize(self, event):
		"""
		Yucky little function that resizes the certain
		features of the GUI based on window size.
		"""
		width = event.width
		if width < 580:
			self._label.config(text=BANNER_TEXT_SMALL)
		else:
			self._label.config(text=BANNER_TEXT)

if __name__ == "__main__":
	root = tk.Tk()
	app = View(root)
	root.mainloop()
