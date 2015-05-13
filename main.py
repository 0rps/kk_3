__author__ = 'orps'

import re

class Terminal:
	def __init__(self, token, isCheckIsRegex = False):
		self.isregex = token[0] == 'r' and isCheckIsRegex
		self.value = token
		if self.isregex:
			self.value = token[1:]
		self.isterm = True


	def __repr__(self):
		return self.value

	def char(self):
		return self.value

	def __cmp__(self, other):
		if self.isregex:
			return None != re.match(other.char(), self.value)

		if other.isRegex():
			return None != re.match(self.char(), other.char())

		return other.char() == self.char()

	def isRegex(self):
		return self.isregex

	def isTerminal(self):
		return self.isterm

class Nonterminal(Terminal):
	def __init__(self, char):
		Terminal.__init__(self,char)
		self.isterm = False

class Rule():
	def __init__(self, head, body):
		if head.isTerminal():
			raise Exception("Rule constructor: head is terminal")

		self.__head = head
		self.__body = body

	def head(self):
		return self.__head

	def body(self):
		return self.__body

	def isFinal(self):
		return len(self.__body) == 1 and self.__body[0].isTerminal()

	def at(self, index):
		return self.__body[index]

class Gramma():
	def __init__(self, nts, ts, rules, start):
		self.__nonterminals = nts
		self.__terminals = ts
		self.__rules = rules
		self.__start = start

	def index(self, element):
		if element.isTerminal():
			s = self.__terminals
		else:
			s = self.__nonterminals

		return s.index(element)

	def nonterminals(self):
		return self.__nonterminals

	def terminals(self):
		return self.__terminals

	def rules(self):
		return self.__rules

	def start(self):
		return self.__start

	def findNonterminalsForTerminal(self, terminal):
		result = []
		for rule in self.__rules:
			if rule.isFinal() and rule.at(0) == terminal:
				result.append(rule.head())

		return result

def getCombinationList(rules, i, j, matrix):
	result = []
	for k in range(1, j):
		for rule in rules:
			if rule.isFinal():
				continue
			A = rule.head()
			if A in result:
				continue
			B = rule.at(0)
			C = rule.at(1)
			if B in matrix[i][k] and C in matrix[i+k][j-k]:
				result.append(A)

	return result

def findRule(gramma, m, i, j, A):
	for k in range(1, j):
		for rule in gramma.rules():
			if rule.isFinal():
				continue

			if rule.head() != A:
				continue

			if rule.at(0) in m[i][k] and rule.at(1) in m[i+k][j-k]:
				return rule, k

	print 'find rule error'
	return None, None



def chainAnalysis(gramma, m, chain, i, j, A):
	if j == 1:
		char = chain[i-1]
		for rule in gramma.rules():
			if rule.head() == A and rule.isFinal() and rule.at(0).char() == char:
				print rule
				return

		print 'ERROR'
		return

	(rule, k) = findRule(gramma, m, i, j, A)

	if rule is None:
		return

	print rule

	chainAnalysis(i, k, rule.at(0))
	chainAnalysis(i + k, j - k, rule.at(1))


def CYK(gramma, instr):
	res= []

	n = len(instr)

	for i in range(0, n+1):
		res.append([])
		for j in range(0, n+1):
			res[i].append(None)

	for i in range(1, n+1):
		res[i][1] = gramma.findNonterminalsForTerminal(instr[i-1])

	for i in range(2, n+1):
		for j in range(1, n-i+1):
			res[i][j] = getCombinationList(gramma.rules(), i, j, res)

	return res


raw_nonterms = ['S','S0', 'S1', 'A', 'A1', 'T', 'T1', 'F', 'I', 'V', 'F0', 'F1', 'F2', 'C', 'S', 'M']
raw_terms = ['<', '<=', '=', '<>', '>', '>=', '+', '-', '*', '/', 'r^[0-9]+$', 'r^[a-z]+$', '(', ')']
raw_rules = [
	'S->S1 A|A1 T|T1 F|r^[0-9]+$|r^[a-z]+$|F0 F1',
	'S1->A C',
	'C-><|<=|=|<>|>|>=',
	'A->A1 T|T1 F|r^[0-9]+$|r^[a-z]+$|F0 F1',
	'A1->A S0',
	'S0->+|-',
	'T->T1 F|r^[0-9]+$|r^[a-z]+$|F0 F1',
	'T1->T M',
	'M->*|/',
	'F->r^[0-9]+$|r^[a-z]+$|F0 F1',
	'I->r^[0-9]+$',
	'V->r^[a-z]+$',
	'F1->A F2',
	'F0->(',
	'F2->)'
]


ar = {}

for char in raw_nonterms:
	ar[char] = Nonterminal(char)

for char in raw_terms:
	ar[char] = Terminal(char, True)

rules = []

start = ar['S']

for line in raw_rules:
	head, rules_str = line.split('->')
	head = ar[head]
	for rule in rules_str.split('|'):
		tokens = map(lambda x: ar[x], rule.split(' '))
		rules.append(Rule(head, tokens))

_g = Gramma([],[],rules, start)

string = 'var = 1234'
toks = map(lambda x: Terminal(x), string.split(' '))
m = CYK(_g, toks)
chainAnalysis(_g, m, toks, 1, len(toks), start)


