import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *
import json
import re
import platform

lexers = {
	"py": QsciLexerPython,
	"css": QsciLexerCSS,
	"cs": QsciLexerCSharp,
	"coffee": QsciLexerCoffeeScript,
	"json": QsciLexerJSON,
	"html": QsciLexerHTML,
	"yml": QsciLexerYAML,
	"md": QsciLexerMarkdown,
}


class CustomMainWindow(QMainWindow):
	def __init__(self):
		super(CustomMainWindow, self).__init__()

		self.setWindowTitle("Chai")

		# load the json config
		with open("config.json", "r") as f:
			self.jsonConfig = f.read()

		self.loadTheme("minute")

		self.Config = json.loads(self.jsonConfig)

		with open("main.css", "r") as f:
			self.__styles = f.read()

		print(self.Config)

		#  make frame
		self.__frm = QFrame(self)

		self.__openFilePath = ""

		self.__lyt = QVBoxLayout()
		self.__frm.setStyleSheet(self.__styles)
		self.__frm.setLayout(self.__lyt)
		self.setCentralWidget(self.__frm)
		self.__myFont = QFont(self.Config['fontFamily'])
		print("set font to " + self.Config['fontFamily'])
		self.__myFont.setPointSize(self.Config['fontSize'])


		self.__bgcolor = QColor(self.Config["backgroundColor"])
		self.__bglight = QColor(self.Config['backgroundLight'])
		self.__fgcolor = QColor(self.Config['foregroundColor'])
		self.__fglight = QColor(self.Config['foregroundLight'])

		# QScintilla editor setup
		# ------------------------

		# ! Make instance of QsciScintilla class!
		self.__editor = QsciScintilla()
		self.__editor.setText("")
		self.__editor.setLexer(None)
		self.__editor.setUtf8(self.Config['utf8'])  # Set encoding to UTF-8
		self.__editor.setFont(self.__myFont)  # Will be overridden by lexer!
		# these parameters will be eventually editable via a json file
		if self.Config['wrapMode'] == "word":
			self.__editor.setWrapMode(QsciScintilla.WrapWord)
		elif self.Config['wrapMode'] == "none":
			self.__editor.setWrapMode(QsciScintilla.WrapNone)
		elif self.Config['wrapMode'] == "character":
			self.__editor.setWrapMode(QsciScintilla.WrapCharacter)
		else:
			self.__editor.setWrapMode(QsciScintilla.WrapWhitespace)
		self.__editor.setWrapVisualFlags(QsciScintilla.WrapFlagNone, QsciScintilla.WrapFlagInMargin, QsciScintilla.WrapIndentSame)
		self.__editor.setIndentationsUseTabs(True)
		self.__editor.setTabWidth(self.Config["tabSize"])
		self.__editor.setIndentationGuides(self.Config["indentationGuides"])
		self.__editor.setIndentationGuidesForegroundColor(self.__fglight)
		self.__editor.setIndentationGuidesBackgroundColor(self.__fglight)
		self.__editor.setAutoIndent(True)
		self.__editor.setPaper(self.__bgcolor)
		self.__editor.setColor(self.__fgcolor)
		self.__editor.setCaretForegroundColor(self.__fglight)
		self.__editor.setCaretLineBackgroundColor(self.__bglight)

		self.__editor.setCaretLineVisible(True)
		self.__editor.setCaretWidth(3)

		# Margin Stuff
		self.__editor.setMarginType(1, QsciScintilla.NumberMargin)
		# TODO: set dynamic calculation of margin width
		contentLength = len(str(self.__editor.text()))
		self.__editor.setMarginWidth(1, "00000")
		self.__editor.setMarginsBackgroundColor(self.__bgcolor)
		self.__editor.setMarginsForegroundColor(self.__fglight)

		# EOL
		self.__editor.setEolMode(QsciScintilla.EolUnix)

		# Lexer Implementation:

		# move the editor!

		self.__editor.setStyleSheet("border: 0px; margin: 15px;")

		# ! Add editor to layout !
		self.__lyt.addWidget(self.__editor)

		# initialize menubar

		menubar = self.menuBar()

		
		openAction = QAction('&Open', self)
		openAction.setStatusTip('Open File') 
		openAction.triggered.connect(self.openDialog)

		saveAction = QAction('&Save', self)
		saveAction.setStatusTip('Save File') 
		saveAction.triggered.connect(self.saveFile)

		toggleLineNumAction = QAction('&Toggle Line Nums', self)
		toggleLineNumAction.setStatusTip('Toggle Line Numbers')
		toggleLineNumAction.triggered.connect(self.toggleLines)
		fileMenu = menubar.addMenu('&File')
		viewMenu = menubar.addMenu('&View')
		
		if platform.system() != "Darwin":
			openAction.setShortcut('Ctrl+O')
			saveAction.setShortcut('Ctrl+S')
			menubar.setStyleSheet("background-color: " + self.Config['backgroundColor'] + "; color: " + self.Config['foregroundLight'])
		else:
			openAction.setShortcut('Cmd+O')
			saveAction.setShortcut('Cmd+S')
		fileMenu.addAction(openAction)
		fileMenu.addAction(saveAction)
		viewMenu.addAction(toggleLineNumAction)

		self.show()

	def toggleLines(self):
		if self.__editor.marginWidth(1) > 0:
			self.__editor.setMarginWidth(1, 0)
		else:
			self.__editor.setMarginWidth(1, "0000")

	def openFile(self, path):
		# get content of file
		with open(path, "r") as f:
			self.fileContent = f.read()
			self.__editor.setText(self.fileContent)
		self.setLexerFromFileExtension(path)

		self.__openFilePath = path

	def openDialog(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
		if fileName:
			print("opening",fileName)
			self.openFile(fileName)

	def saveFile(self):
		
		if self.__openFilePath != "":
			dtext = self.__editor.text()
			print(dtext)
			with open(self.__openFilePath, "w+") as f:
				f.write(dtext)
		else:
			self.saveDialog()


	def saveDialog(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()", "","All Files (*);;Python Files (*.py)", options=options)
		if fileName:
			print("\""+fileName+"\"")
			self.__openFilePath = fileName
			self.saveFile()

	def setLexerFromFileExtension(self, path):

		regex = r".+\.(\w+)"
		result = re.search(regex, path)
		print(result[1])
		l = result[1]

		lexer = lexers[l]()

		languageTheme = self.__theme[l]

		"""
		for index, value in lexers.items():
			print(index)
			for n in list(range(30)):
				print(lexers[index]().description(n))
			
			print("\n\n")
		"""

		#self.__editor.Styles[lexer.commentLine.size] = 18

		lexer.setDefaultFont(self.__myFont)
		lexer.setDefaultPaper(self.__bgcolor)
		lexer.setDefaultColor(self.__fgcolor)

		print(languageTheme)
		for name, value in languageTheme.items():
			print(value, name)
			lexer.setColor(QColor(value), getattr(lexers[l](), name))
			lexer.setPaper(self.__bgcolor, getattr(lexers[l](), name))
			lexer.setFont(self.__myFont, getattr(lexers[l](), name))

		

		self.__editor.setLexer(lexer)

	def loadTheme(self, themename):
		with open("./themes/{}.json".format(themename), "r") as f:
			self.__theme = json.loads(f.read())
''' END CLASS '''


if __name__ == '__main__':
	print(platform.system())
	app = QApplication(sys.argv)
	QApplication.setStyle(QStyleFactory.create('Fusion'))
	myGUI = CustomMainWindow()

	sys.exit(app.exec_())
