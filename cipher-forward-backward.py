import math
import random
import matplotlib.pyplot as plt
import sys

# Adding log values
def add_log(x, y):
	if x==float('-Inf'):
		return y
	if y==float('-Inf'):
		return x
	if isinstance(x,float) and isinstance(y, float) and (x-y)>16:
		return x
	if x>y:
		return x + math.log(1 + math.exp(y-x))
	if isinstance(x,float) and isinstance(y, float) and (y-x)>16:
		return y
	if y>x:
		return y + math.log(1 + math.exp(x-y))
	if x==y:
		ex = math.exp(x)
		return math.log(2*ex)

# Function to run forward-backward algorithm
def runfb(englishdatafile, cipherfile, iterations, randomflag, plot):

	# All possible tags for each character
	tags = []
	for a in range(65,91):
		tags.append(chr(a))
	tags.append(' ')
	

	# Calculate Unigram and bigram probabilities (Grammer or structure)
	fo = open(englishdatafile)
	lines = fo.readlines()
	fo.close()

	unigram = dict()
	bigram = dict()
	pch = -1
	for line in lines:
		line = line.replace('\n','')
		for ch in line:
			if ch not in unigram.keys():
				unigram[ch] = 1
			else:
				unigram[ch] += 1

			if pch!=-1:
				if pch not in bigram.keys():
					bigram[pch] = dict()

				if ch not in bigram[pch].keys():
					bigram[pch][ch] = 1
				else:
					bigram[pch][ch] += 1

			pch = ch
	
	total = 0
	for key in unigram.keys():
		total += unigram[key]
	for key in unigram.keys():
		unigram[key] = math.log(unigram[key]) - math.log(total)

	for key in bigram.keys():
		total = 0
		for subkey in bigram[key].keys():
			total += bigram[key][subkey]
		for subkey in bigram[key].keys():
			bigram[key][subkey] = math.log(bigram[key][subkey]) - math.log(total)

	onegram = dict()
	for i in range(65, 91):
		onegram[chr(i)] = math.log(1.0/(len(tags)-1))
		onegram[' '] = float('-Inf')


	rprob = list()
	ranswer = list()
	rbestscore = list()
	for ran in range(randomflag+1):
		# Setting substitution probabiities - Uniform
		prob = dict()
		count = dict()
		if randomflag==0:

			for a in range(65,91):
				prob[chr(a)] = dict()
				count[chr(a)] = dict()
				for sa in range(65,91):
					prob[chr(a)][chr(sa)] = math.log(1.0/26)
					count[chr(a)][chr(sa)] = 0
		else:
			print 'Restart Number', ran
			for a in range(65,91):
				prob[chr(a)] = dict()
				count[chr(a)] = dict()
				rtotal = 0.0
				for sa in range(65,91):
					prob[chr(a)][chr(sa)] = random.randint(1,500)
					rtotal += prob[chr(a)][chr(sa)]
					count[chr(a)][chr(sa)] = 0

				for sa in range(65,91):
					prob[chr(a)][chr(sa)] /= rtotal*1.0
					prob[chr(a)][chr(sa)] = math.log(prob[chr(a)][chr(sa)])



		prob[' '] = dict()
		prob[' '][' '] = math.log(1)

		count[' '] = dict()
		count[' '][' '] = 0
		rprob.append(prob)
	
		# Getting training data
		tfile = open(cipherfile)
		datalines = tfile.readlines()
		tfile.close()
		data = ''
		for dline in datalines:
			dline = dline.replace('\n','')
			data += dline
	
		pcipher = []
		for iteration in range(iterations):
			print "--------------------------------------Iteration" + str(iteration+1) + '--------------------------------------'
			fb(tags, bigram, prob, count, data, pcipher, rbestscore)
			#ans = viterbi(onegram, bigram, prob, data)
			#print "".join(ans)
		

		if plot==1:
			plt.plot(pcipher)
			plt.ylabel('log(P(cipher))')
			plt.xlabel('iterations')
			plt.show()
		
		ans = viterbi(onegram, bigram, prob, data)
		
		ranswer.append("".join(ans))
		rbestscore.append(pcipher[len(pcipher)-1])


	inde = rbestscore.index(max(rbestscore))
	print ranswer[inde]
	


def fb(tags, bigram, prob, count, data, pcipher, rbestscore):
	
	string = data
	
	# Forward Algorithm
	alpha = Matrix = [[float('-Inf') for x in xrange(len(string)*2)] for x in xrange(len(tags))] 

	for i in range(0,len(string)*2,2):
		char = string[i/2]
		if i==0:
			for tag_no in range(len(tags)-1):
				alpha[tag_no][i] = math.log(1.0/26)
				alpha[tag_no][i+1] = prob[tags[tag_no]][char] + alpha[tag_no][i]
		else:
			if char != ' ':
				for tag_no in range(len(tags)-1):
					for t in range(len(tags)):
						if not bigram[tags[t]].has_key(tags[tag_no]):
							continue
						alpha[tag_no][i] = add_log( alpha[tag_no][i], (alpha[t][i-1] + bigram[tags[t]][tags[tag_no]]))
					alpha[tag_no][i+1] = prob[tags[tag_no]][char] + alpha[tag_no][i]
			else:
				for t in range(len(tags)-1):
					if not bigram[tags[t]].has_key(' '):
						continue
					alpha[len(tags)-1][i] = add_log( alpha[len(tags)-1][i], (alpha[t][i-1] + bigram[tags[t]][' ']))
				alpha[len(tags)-1][i+1] = prob[' '][char] + alpha[len(tags)-1][i]

	alpha_end = float('-Inf')
	for i in range(len(tags)):
		alpha_end = add_log(alpha_end, alpha[i][len(alpha[i])-1])
	
	
	pcipher.append(alpha_end)
	

	# Backward Algorithm
	
	beta = Matrix = [[float('-Inf') for x in xrange(len(string)*2)] for x in xrange(len(tags))] 

	for i in range(len(string)*2-1,-1,-2):
		char = string[(i-1)/2]
		if i==len(string)*2-1:
			for tag_no in range(len(tags)-1):
				beta[tag_no][i] = math.log(1)
				beta[tag_no][i-1] = prob[tags[tag_no]][char] + beta[tag_no][i]
		else:
			if char != ' ':
				for tag_no in range(len(tags)-1):
					for t in range(len(tags)):
						if not bigram[tags[tag_no]].has_key(tags[t]):
							continue
						beta[tag_no][i] = add_log( beta[tag_no][i], (beta[t][i+1] + bigram[tags[tag_no]][tags[t]]))
					beta[tag_no][i-1] = prob[tags[tag_no]][char] + beta[tag_no][i]
			else:
				for t in range(len(tags)-1):
					if not bigram[' '].has_key(tags[t]):
						continue
					beta[len(tags)-1][i] = add_log( beta[len(tags)-1][i], beta[t][i+1] + bigram[' '][tags[t]])
				beta[len(tags)-1][i-1] = prob[' '][char] + beta[len(tags)-1][i]


	beta_end = float('-Inf')
	for i in range(len(tags)-1):
		beta_end = add_log( beta_end, beta[i][0] + math.log(1.0/26))


	


	# Counting pass
	
	for key in count.keys():
		for subkey in count[key].keys():
			count[key][subkey] = 0

	for i in range(len(tags)-1):
		for key in count[tags[i]].keys():
			findex = string.find(key,0)
			while findex!=-1:
				count[tags[i]][key] = add_log(count[tags[i]][key], (alpha[i][findex*2] +  prob[tags[i]][key] + beta[i][findex*2+1] - alpha_end))
				findex = string.find(key,findex+1)
		

	
	
	for key in count.keys():
		total = 0
		if key!=' ':
			for subkey in count[key].keys():
				total = (total +  math.exp(count[key][subkey]))
			for subkey in count[key].keys():
				prob[key][subkey]= math.log(math.exp(count[key][subkey]) / total)
		else:
			prob[' '][' '] = math.log(1)



def viterbi(tag_prob, tag_tag_prob, word_tag_prob, sentence):

	sentence = list(sentence)
	

	tags = tag_prob.keys()
	rows = len(tag_prob)
	cols = len(sentence)
	Q =  [[float('-Inf') for x in xrange(cols)] for x in xrange(rows)] 
	best_pred =  [[0 for x in xrange(cols)] for x in xrange(rows)] 
	new_tags = ['' for x in xrange(cols)]
	for j in range(0,rows):
		if sentence[0] in word_tag_prob[tags[j]].keys():
			Q[j][0] =  (tag_prob[tags[j]]) + (word_tag_prob[tags[j]][sentence[0]])

	for i in range(1,cols):
		for j in range(0, rows):
			Q[j][i] = float('-Inf')
			best_pred[j][i] = 0
			best_score = float("-Inf")
			for k in range(0,rows):
				if tags[j] in tag_tag_prob[tags[k]].keys():
					if sentence[i] in word_tag_prob[tags[j]]:
					
						r =(tag_tag_prob[tags[k]][tags[j]]) + (word_tag_prob[tags[j]][sentence[i]]) + Q[k][i-1]
						if r> best_score:
							best_score = r
							best_pred[j][i] = k
							Q[j][i] = r

	
	final_best = 0
	final_score = float("-Inf")

	for j in range(0, rows):
		if Q[j][cols-1] > final_score:
			final_score = Q[j][cols-1]
			final_best = j

	new_tags[cols-1] = tags[final_best]
	current = final_best
	for i in range(cols-2,-1,-1):
		current = best_pred[current][i+1]
		new_tags[i] = tags[current]

	
	return new_tags

def main():
	englishdatafile = sys.argv[2]
	cipherfile = sys.argv[4]
	iterns = int(sys.argv[6])
	randrestarts = int(sys.argv[8])
	plot = int(sys.argv[10])
	runfb(englishdatafile, cipherfile, iterns, randrestarts, plot)

main()
