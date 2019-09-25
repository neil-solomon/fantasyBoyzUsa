import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

def generateChaos(length):
	with open('C:/Users/NeilS/Desktop/FantasyBoyzUSA/plots/chaosData.txt','w+') as file:
		x = 0
		for i in range(length):
			file.write(str(i)+','+str(x)+'\n')
			x = x**2 - 1.5


style.use('fivethirtyeight')
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def animate(i): 
	graph_data = open('C:/Users/NeilS/Desktop/FantasyBoyzUSA/plots/chaosData.txt','r').read()
	lines = graph_data.split('\n')
	xs = []
	ys = []
	for line in lines:
		if len(line) > 1:
			x, y = line.split(',')
			xs.append(float(x))
			ys.append(float(y))
	ax1.clear()
	if len(xs)>20:
		ax1.axes.set_xlim(len(xs)-20,len(xs))
	ax1.plot(xs, ys, 'ro')

ani = animation.FuncAnimation(fig, animate, interval=250, blit=False, repeat=False)
plt.show()
