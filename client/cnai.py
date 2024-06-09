import gensim
import numpy as np
from collections import defaultdict
from itertools import chain, combinations
from random import choice
from re import sub
from sys import argv
import nltk
from nltk.stem.snowball import SnowballStemmer


#========================================
#HELPERS

VERB = False

stemmer = SnowballStemmer(language='english')

def powerset(iterable, rng=range(2,4)): #range(2-5) instead?
	s = list(iterable)
	return chain.from_iterable(combinations(s, r) for r in rng)

#checks for valid hints:
#	not on board, one word only, no acronyms, all alphabetical chars
def isValid(word, board_words):
	word_stem = stemmer.stem(word)
	for w in board_words:
		curr_stem = stemmer.stem(w)
		if word_stem == curr_stem:
			return False
	return '_' not in word and not word.isupper() and word.isalpha()

#list of lists into one list
def flatten(t):
	return [item for sublist in t for item in sublist]

def w2vPreprocess(model, w):
	try:
		model.key_to_index[w]
	except KeyError:
		w = '_'.join([part[0].upper()+part[1:] for part in w.split('_')])
	return w
	
#========================================
#MODEL

w2v_model = None
def getW2vModel():
	global w2v_model
	if not w2v_model:
		print("loading w2v model")
		w2v_model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True, limit=500000)
	return w2v_model

#========================================
#GUESSERS

#NOTE: guess may be None for "pass"
#Maybe rename/refactor to SimilarityGuesser?
class Guesser:
	def __init__(self):
		self.hints = []
		self.num_guesses = 0 #increment with each guess, should never get higher than the num in hint[1]
	
	def isCheat(self):
		return False
	
	#hint is (word,num) tuple
	def newHint(self, hint):
		self.hints.append(hint)
		self.num_guesses = 0
	
	#returns one of the words from choices as the guess (not board, just list of possible words)
	#game class will only ask for guesses if the guesser has some left
	def nextGuess(self, choices):
		if VERB: print("inG choices:",choices)
		temp = self.preprocess(self.hints[0][0].lower())
		if VERB: print("inG prehint:",self.hints[0],temp,self.isKnown(temp))
		
		hint = None
		i = len(self.hints)-1
		while i >= 0:
			temp = self.preprocess(self.hints[i][0].lower())
			if VERB: print("inG in while temp:",temp)
			if self.isKnown(temp):
				hint = temp
				break
			i -= 1
		if VERB: print("inG hint:",hint)
		if hint is None:
			return None
		max_v = -9999
		max_w = None
		for ch in choices:
			ch = self.preprocess(ch)
			s = self.getSimilarity(hint, ch)
			if VERB: print("inG sim:",hint, ch,s)
			if s > max_v:
				max_v = s
				max_w = ch
		self.num_guesses += 1
		return max_w.lower()
	
	#return the similarity between 2 words
	#ABSTRACT
	def getSimilarity(self, a, b):
		raise NotImplementedError
	
	#preprocess word before getting embedding (e.g. w2v checks capitalization, gpt converts _ to space)
	def preprocess(self, w):
		raise NotImplementedError
	
	#opportunity for subclass to be picky about which words it knows (looking at you w2v)
	def isKnown(self, w):
		return True

class RandomGuesser(Guesser):
	def __init__(self):
		super().__init__()

	def nextGuess(self, choices):
		return choice(choices)

class W2VGuesser(Guesser):
	def __init__(self):
		super().__init__()
		self.model = getW2vModel()
	
	def getSimilarity(self, a, b): 
		return self.model.similarity(a, b)
	
	#return capitalized version of w if w not in model
	#kinda hacky, but w2v has New_York but not new_york etc
	def preprocess(self, w):
		return w2vPreprocess(self.model, w)
	
	def isKnown(self, w):
		try:
			self.model.key_to_index[w]
		except KeyError:
			return False
		return True

#========================================
#ASSOC

#associates words for a given set of positively and negatively associated words
#abstract superclass, implement for given LM
class Assoc:
	def __init__(self):
		pass
	
	#returns a list of potential associations with a confidence/prob for each
	#abstract function
	def getAssocs(self, pos, neg, topn):
		raise NotImplementedError
	
	#preprocess word before getting embedding (e.g. w2v checks capitalization, gpt converts _ to space)
	def preprocess(self, w):
		raise NotImplementedError
	
	#gives subclasses option of clearing cache after each hint gen cycle (balance between cached and not)
	def clearCache(self):
		return

class W2VAssoc(Assoc):
	def __init__(self):
		super().__init__()
		self.model = getW2vModel()
	
	def getAssocs(self, pos, neg, topn):
		#print("W2V",pos,neg)
		return self.model.most_similar(
			positive=pos,
			negative=neg,
			topn=topn,
			restrict_vocab=50000
		)
	
	def preprocess(self, w):
		return w2vPreprocess(self.model, w)

#========================================

#should be model-agnostic
class Spymaster:
	def __init__(self, assoc):
		self.assoc = assoc #subclass of Assoc class
	
	class Combo:
		def __init__(self):
			self.scores = [] #all similarity scores gen'd for this combo, regardless of hint
			#also track hint with max sim score
			self.max_hint = None
			self.max_sim = -9999
		
		def addOption(self, hint, sim):
			self.scores.append(sim)
			if self.max_sim < sim:
				self.max_sim = sim
				self.max_hint = hint
		
		def getAvgSim(self):
			return sum(self.scores)/len(self.scores)
	
	#returns (hint, number) tuple
	#IDEA: if there are only 3-4 words left, lean more toward hail marys
	def makeHint(self, board, blue):
		board_words = set([item for sublist in list(board.values()) for item in sublist])
		neg = board['N'] + board['A'] + (board['R'] if blue else board['U'])
		pos = board['U'] if blue else board['R']
		
		#hacky, but w2v is picky about capitals
		neg = [self.assoc.preprocess(w) for w in neg]
		pos = [self.assoc.preprocess(w) for w in pos]
		
		#Game AI approach:
		#1. find combo with highest avg hint similarity (hyp: most likely to be closest related combo)
		#2. pick the highest-scoring hint for that combo as our hint (# is just len of combo ofc)
		
		self.assoc.clearCache() #each assoc knows how to handle this itself
		
		combos = defaultdict(Spymaster.Combo)
		
		if len(pos) == 1: #powerset 2-4 will return []!
			pow_set = [tuple(pos)] #needs to be formatted JUST like powerset
		else:
			pow_set = powerset(pos)
		for combo in pow_set:
			curr = self.assoc.getAssocs(list(combo),neg, 10)
			
			any_added = False #DEBUG
			for hint,sim in curr:
				hint = hint.lower() #something more robust?
				if isValid(hint, board_words):
					combos[combo].addOption(hint, sim)
					any_added = True
			if not any_added:
				print("NONE ADDED:", combo, [hint for hint,sim in curr]) #pass
		
		if VERB: print("mH combos:",combos)
		
		max_avg_sim = -9999
		max_combo = None
		
		 # bc I got "TypeError: object of type 'NoneType' has no len()" for len(max_combo) below???
		if not combos.keys():
			print("NO HINT!",board,blue,pos,neg)
			return ("None",1)
		
		for combo in combos.keys():
			avg_sim = combos[combo].getAvgSim()
			if VERB: print("mH combo+avg\t:",combo, avg_sim)
			if max_avg_sim < avg_sim:
				max_avg_sim = avg_sim
				max_combo = combo
		
		if VERB: print("mH max_combo:",max_combo) #DEBUG
		return (combos[max_combo].max_hint, len(max_combo)), max_combo


#=TEST======================================

if __name__ == "__main__":
	
	VERB = "-v" in argv
	
	board = {
		'U': [
			'ambulance', 'hospital', 'spell', 'lock', 
			'charge', 'tail', 'link', 'cook', 'web'
		],
		'R': [
			'cat', 'button', 'pipe', 'pants', 
			'mount', 'sleep', 'stick', 'file'
		],
		'N': ["giant", "nail", "dragon", "stadium", "flute", "carrot", "wake"],
		'A': ['doctor']
	}
	
	pos = board['U']
	neg = board['R'] + board['A']
	
	m = Spymaster(W2VAssoc())
	hint = m.makeHint(board, True)
	
	print(hint)
	
	gg = W2VGuesser()

	print(gg.getSimilarity("dog","brick"))
	print(gg.getSimilarity("dog","cat"))
	print(gg.getSimilarity("dog","hound"))

	gg.newHint(hint)
	choices = sum(board.values(), [])
	print(gg.nextGuess(choices))
	print(VERB)

#

'''
GUESSER TEST with hardcoded
hint = ("fast",2)

flute	-0.01920261
charge	-0.005023578
doctor	0.02332398
hospital	0.027558524
stadium	0.041338284
ambulance	0.051199097
link	0.054826703
cat	0.05885695
pipe	0.06645677
pants	0.0702359
carrot	0.07023594
button	0.072394334
wake	0.091219224
lock	0.09222474
file	0.093515135
sleep	0.093738094
dragon	0.09670608
web	0.09714937
nail	0.11437844
spell	0.11791275
stick	0.1194138
mount	0.12234473
cook	0.13407777
giant	0.15742585
tail	0.1750035
'''

