#coding: utf-8
#date: 2016-06-03
#mail: artorius.mailbox@qq.com
#author: xinwangzhong -version 0.1

from math import log
import re
import sys

MIN_NUM = -1.0e10000

class HMM():
	"""docstring for HMM"""
	def __init__(self):
		self.A = [[0]*4 for i in range(4)]
		# 0: 表示隐藏层begin状态
		# 1：表示sigle
		# 2：表示end
		# 3：表示middle
		self.len_hidden = len(self.A)
		self.hidden = ["0", "1", "2", "3"]
		self.B = {0:{}, 1:{}, 2:{}, 3:{} }
		self.pi = [log(0.5), log(0.5), 0, 0] # 将概率转化为对数形式
		self.train_data_path = r"msr_training.utf8"

	def train_HMM(self):
		chinese = re.compile(u"([\u4e00-\u9fffa-zA-Z]+)")
		for line in open(self.train_data_path):
			line = line.strip().decode("utf8").split("  ")
			new_line = []
			tran_str = ""
			for item in line:
				# print item.encode("utf8")
				rlst = chinese.findall(item)
				if len(rlst) == 1 and len(rlst[0])==len(item):
					new_line.append(item)
					if len(item) == 1:
						tran_str += "1"
					elif len(item) == 2:
						tran_str += "02"
					else:
						tran_str += "0"+"3"*(len(item)-2)+"2"
			# print " ".join(new_line).encode("utf8"), len(new_line)
			# print tran_str
			line_str = "".join(new_line)
			for idx in range(len(tran_str)-1):
				obser = line_str[idx]
				state = int(tran_str[idx])
				next_state = int(tran_str[idx+1])
				self.A[state][next_state] += 1
				if obser not in self.B[state]:
					self.B[state][obser] = 0
				self.B[state][obser] += 1
			# print self.A, self.B
			# break
		raw_sum = map(lambda x:sum(x) , self.A)
		opt_a = open("A", "w")
		for idx in range(4):
			for j in range(len(self.A[idx])):
				if self.A[idx][j] != 0:
					self.A[idx][j] = log(self.A[idx][j]/(1.0*raw_sum[idx]))
				else:
					self.A[idx][j] = MIN_NUM
				# self.A[idx][j] = str(self.A[idx][j])
			opt_a.write("\t".join([str(x) for x in self.A[idx]])+"\n")
			opt = open(str(idx), "w")
			for key in self.B[idx]:
				self.B[idx][key] = log((self.B[idx][key])/(1.0*raw_sum[idx]))# 概率取log对数
				opt.write(key.encode("utf8")+"\t"+str(self.B[idx][key])+"\n")
			opt.close()
		opt_a.close()
		# print self.A
		# print self.A, self.B

	def load_HMM(self):
		self.A = map(lambda x:[float(s) for s in x.split("\t")], open("A").readlines())
		for idx in range(4):
			for line in open(str(idx)):
				key, value = line.strip().decode("utf8").split("\t")
				self.B[idx][key] = float(value)
		# print self.A
		# print self.B[0]
	
	def viterbi(self, observed):
		state = []
		len_observed = len(observed)
		alpha = [([0]*self.len_hidden) for i in range(len_observed)]
		path = [([0]*self.len_hidden) for i in range(len_observed)]
		#第一天计算，状态的初始概率*隐藏状态到观察状态的条件概率
		for j in range(self.len_hidden):
			# print self.pi[j], self.B[j][observed[0]]
			alpha[0][j] = self.pi[j]+self.B[j][observed[0]]
			path[0][j] = -1
		# print alpha
		# 第一天以后的计算
		# 前一天的每个状态转移到当前状态的概率最大值
		# 隐藏状态到观察状态的条件概率
		for i in range(1,len_observed):
			for j in range(self.len_hidden):
				max_ = MIN_NUM
				index = 0
				for k in range(self.len_hidden):
					if(alpha[i-1][k]+self.A[k][j] > max_):# k转移到j
						max_ = alpha[i-1][k]+self.A[k][j]
						index = k
				try:
					alpha[i][j] = max_+self.B[j][observed[i]]
				except KeyError:
					print observed[i].encode("utf8")+" "
					sys.exit()
				path[i][j] = index
		max_ = MIN_NUM
		idx = 0
		for i in range(self.len_hidden):
			if(alpha[len_observed-1][i]>max_):
				max_ = alpha[len_observed-1][i]
				idx = i
		print "最可能隐藏序列的概率："+str(max_)
		state.append(self.hidden[idx])
		#逆推回去找到每天出现哪个隐藏状态的概率最大
		for i in range(len_observed-1,0,-1):
			idx = path[i][idx]
			state.append(self.hidden[idx])
		state.reverse()
		return state

	def check_new_word( self, observed ):
		state = self.viterbi(observed)
		result = []
		for idx in range(len(observed)):
			result.append(observed[idx])
			if int(state[idx])==1 or int(state[idx])==2:
				result.append("`1")
		result = " ".join(result).strip().replace(" ", "").split("`1")
		return filter(lambda x:len(x)>=1, result)

if __name__ == '__main__':
	hmm = HMM()
	hmm.train_HMM()
	hmm.load_HMM()
	test = u"迈向充满希望的新世纪"
	print " ".join(hmm.check_new_word(test)).encode("utf8")
