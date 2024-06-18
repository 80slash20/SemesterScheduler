import tkinter as tk
from tkinter import *
from sklearn.linear_model import Ridge
import numpy as np

# Constants
PURPLE_COLOUR = (81, 36, 122)
BANNER_TEXT = "SEMESTER SCHEDULER"
BANNER_TEXT_SMALL = "SEM SCHED"
MIN_WIN_SIZE = (400, 200)

def _rgb_to_hex(rgb):
    """
	translates an rgb tuple of integers to (tkinter formatted) hex
    """
    return "#%02x%02x%02x" % rgb

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
		
		self._entry_subject_name = tk.Entry(self._controls_container)
		self._entry_subject_name.pack(side=tk.TOP)
		self._entry_subject_name.insert(0, "Subject name") 

		self._entry_subject_name_submit = tk.Button(text='[+]', action=self._create_new_subject)

		self._entry_profile = tk.Entry(self._controls_container)
		self._entry_profile.pack(side=tk.TOP)
		self._entry_profile.insert(0, "Link to subject profile") 

		self._root.bind("<Configure>", self._on_resize)

	def _on_resize(self, event):
		width = event.width
		if width < 580:
			self._label.config(text=BANNER_TEXT_SMALL)
		else:
			self._label.config(text=BANNER_TEXT)
	def _create_new_subject():
		pass

class Subject():
	def __init__(self, name, course_code, semester, year, type):
		self._name = name
		self._course_code = course_code
		self._semester = semester
		self._year = year
		self._type = type
	def get_course_code(self):
		return self._course_code
	def get_type(self):
		return self._type
	def __eq__(self, other):
		return other.get_course_code() == self.get_course_code()

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