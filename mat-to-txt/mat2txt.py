import scipy.io as sio
import numpy as np  
mat_path = r"F:\algorithm\dataset\data.mat"
data=sio.loadmat(mat_path)
data = list(data["data"])
x = [[data[0][idx], data[1][idx]] for idx in range(2000) ]
y = [data[2][idx] for idx in range(2000)]
print len(x), len(y)
print set(y)
x, y = [], []
for idx in range(1000):
	label = idx%5
	x_tmp = np.random.random(2)+label
	y_tmp = label
	x.append(x_tmp)
	y.append(y_tmp)
print x
print y
