import gensim
import numpy as np

#========================================
#HELPERS

def powerset(iterable, rng=range(2,5)):
	s = list(iterable)
	return chain.from_iterable(combinations(s, r) for r in rng)

#checks for valid hints:
#	not on board, one word only, no acronyms, all alphabetical chars
def isValid(word, board_words):
	if word in board_words:
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
		print("building w2v model")
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
		hint = None
		i = len(self.hints)-1
		while i > 0:
			temp = self.preprocess(self.hints[-1][0].lower())
			if self.isKnown(temp):
				hint = temp
				break
			i -= 1
		if hint is None:
			return None
		max_v = -9999
		max_w = None
		for ch in choices:
			ch = self.preprocess(ch)
			s = self.getSimilarity(hint, ch)
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

#make sure to pair with Cheatmaster, otherwise the num in the hint might be less than self.n
class CheatGuesser(Guesser):
	def __init__(self, n):
		super().__init__()
		self.answers = None
		self.n = n
	
	def isCheat(self):
		return True
	
	#call this before every guess because board changes
	def cheat(self, board, isBlue):
		self.answers = board['U'] if isBlue else board['R']
	
	def nextGuess(self, choices):
		if self.answers is None:
			raise ValueError("CheatGuesser was never given answers via cheat()")
		if self.num_guesses < self.n:
			self.num_guesses += 1
			return self.answers.pop()
		else:
			return None

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
				pass #print("NONE ADDED:", combo, [hint for hint,sim in curr])
		
		max_avg_sim = -9999
		max_combo = None
		
		 # bc I got "TypeError: object of type 'NoneType' has no len()" for len(max_combo) below???
		if not combos.keys():
			print("NO HINT!",board,blue,pos,neg)
			return ("None",1)
		
		for combo in combos.keys():
			avg_sim = combos[combo].getAvgSim()
			if max_avg_sim < avg_sim:
				max_avg_sim = avg_sim
				max_combo = combo
		
		#print(max_combo) #DEBUG
		return (combos[max_combo].max_hint, len(max_combo))
		

class Cheatmaster(Spymaster):
	def __init__(self):
		super().__init__(None) #doesn't need Assoc
	
	def makeHint(self, board, blue):
		return ("CHEAT", 9999) #this is so the cheat guesser can (perfectly) guess as many times as it needs

#=TEST======================================

if __name__ == "__main__":
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
	gg = W2VGuesser()

	test = gg.getSimilarity("dog","cat")
	print(test, type(test))

	gg.newHint(hint)
	choices = sum(board.values(), [])
	print(gg.nextGuess(choices))

#


