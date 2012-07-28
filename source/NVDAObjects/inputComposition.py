import eventHandler
import queueHandler
import controlTypes
import speech
import config
from NVDAObjects.window import Window
from behaviors import EditableTextWithAutoSelectDetection, CandidateItem as CandidateItemBehavior 
from textInfos.offsets import OffsetsTextInfo

def calculateInsertedChars(oldComp,newComp):
	oldLen=len(oldComp)
	newLen=len(newComp)
	minLen=min(oldLen,newLen)
	print "oldLen %d, newLen %d, minLen %d"%(oldLen,newLen,minLen)
	diffStart=0
	diffEnd=newLen
	for index in xrange(minLen):
		print "checking start: index %d, new %c, old %c"%(index,newComp[index],oldComp[index])
		if newComp[index]!=oldComp[index]:
			break
		diffStart=index+1
	for index in xrange(minLen,0,-1):
		backIndex=index-minLen-1
		print "checking end: index %d, backIndex %d, new %c, old %c"%(index,backIndex,newComp[backIndex],oldComp[backIndex])
		if newComp[backIndex]!=oldComp[backIndex]:
			break
		diffEnd=newLen+backIndex
	diffEnd=max(diffEnd,diffStart+(newLen-oldLen))
	print "diffStart %d, diffEnd %d"%(diffStart,diffEnd)
	return newComp[diffStart:diffEnd]

class InputCompositionTextInfo(OffsetsTextInfo):

	def _getSelectionOffsets(self):
		return self.obj.compositionSelectionOffsets

	def _getCaretOffset(self):
		return self._getSelectionOffsets()[0]

	def _getStoryLength(self):
		return len(self.obj.compositionString) if self.obj.compositionString else 0

	def _getStoryText(self):
		return self.obj.compositionString if self.obj.compositionString else u""

class InputComposition(EditableTextWithAutoSelectDetection,Window):

	TextInfo=InputCompositionTextInfo
	name=_("Composition")
	role=controlTypes.ROLE_EDITABLETEXT
	next=None
	previous=None
	firstChild=None
	lastChild=None
	states=set()
	location=None
	compositionString=""
	compositionSelectionOffsets=(0,0)

	def __init__(self,parent=None):
		self.parent=parent
		super(InputComposition,self).__init__(windowHandle=parent.windowHandle)

	def findOverlayClasses(self,clsList):
		clsList.append(InputComposition)
		clsList.append(InputComposition)
		return clsList

	def compositionUpdate(self,compositionString,selectionStart,selectionEnd,newText):
		if (config.conf["keyboard"]["speakTypedCharacters"] or config.conf["keyboard"]["speakTypedWords"]):
			newText=calculateInsertedChars(self.compositionString.strip(u'\u3000'),compositionString.strip(u'\u3000'))
			if newText:
				queueHandler.queueFunction(queueHandler.eventQueue,speech.speakText,newText)
		self.compositionString=compositionString
		self.compositionSelectionOffsets=(selectionStart,selectionEnd)
		eventHandler.queueEvent("valueChange",self)
		eventHandler.queueEvent("caret",self)

	def reportFocus(self):
		pass

class CandidateList(Window):

	name=_("Candidate")
	role=controlTypes.ROLE_LIST
	next=None
	previous=None
	firstChild=None
	lastChild=None
	states=set()

	def __init__(self,parent=None):
		self.parent=parent
		super(CandidateList,self).__init__(windowHandle=parent.windowHandle)

	def findOverlayClasses(self,clsList):
		clsList.append(CandidateList)
		return clsList

class CandidateItem(CandidateItemBehavior,Window):

	role=controlTypes.ROLE_LISTITEM
	next=None
	previous=None
	firstChild=None
	lastChild=None
	states=set()

	def __init__(self,parent=None,candidateStrings=[],candidateIndex=0):
		self.parent=parent
		self.candidateStrings=candidateStrings
		self.candidateIndex=candidateIndex
		super(CandidateItem,self).__init__(windowHandle=parent.windowHandle)

	def findOverlayClasses(self,clsList):
		clsList.append(CandidateItem)
		return clsList

	def _get_name(self):
		return self.candidateStrings[self.candidateIndex]

	def _get_value(self):
		return unicode(self.candidateIndex+1)
