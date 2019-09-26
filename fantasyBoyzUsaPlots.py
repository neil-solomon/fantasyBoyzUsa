import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
from scipy import stats
from itertools import combinations # used for generating powerSet
from math import pi
import pickle
import json


def probDist(probList):
	"""
	Calcuates the discrete probability distribution of n events occurring. The output is a list, where
	outList[i] is the probability that exactly i events will occur. The input is a list of 
	probabilities where inList[i] is probability of event i occuring. 
	Argument: list of probabilities 'probList'
	Return: discrete probability distribution as a list 'discreteDist'
	"""
	discreteDist = []
	invProbList = [] # 1 - probList
	numEvents = len(probList)
	for i in range(len(probList)): # watch out for floating-point rounding errors
		invProbList.append(1-probList[i])
	powerSet = []
	eventList = [i for i in range(numEvents)]
	#print(eventList)
	for i in range(numEvents+1):
		powerSet.append(list(combinations(eventList,i)))
	#print(powerSet)
	for subSet in powerSet: # subSets are grouped according to size, 0 to numEvents
		#print(subSet)
		totalProb = 0
		for subSubSet in subSet: # subSubSets are tuples (the actual subsets of the powerSet)
			#print(subSubSet)
			prob = 1
			for ix in range(numEvents):
				if ix not in subSubSet:
					#print(ix,'loss')
					prob *= invProbList[ix]
				else:
					#print(ix,'win')
					prob *= probList[ix]
			totalProb += prob
		discreteDist.append(totalProb)
	return discreteDist



def makeProjectedWins(fantasyTeams, weekStart, weekEnd):
	"""
	Projects the total number of wins for each team from weekStart to weekEnd. Projection is based on projected 
	points vs opponents projected points. 
	Argument: dictionary of fantasyTeam objects 'fantasyTeams', weeks to plot from int 'weekStart' to int 'weekEnd'
	Return: dictionary with key:teamName and value:projectedWins 'projectedWins'
	"""
	projectedWinsDict = {}
	for team in fantasyTeams:
		projectedWins = 0
		for i in range(weekStart, weekEnd+1):
			try:
				if fantasyTeams[team].projectedPoints[i] > fantasyTeams[team].projectedPointsAgainst[i]:
					projectedWins += 1
			except Exception as e:
				pass
		projectedWinsDict.update({team:projectedWins})
	return projectedWinsDict



def makeMatchupData(fantasyTeams, week):
	"""
	Builds all of the data for each of the matchups for the week.
	Argument: dictionary of fantasyTeam objects 'fantasyTeams', week to build int 'week'
	Return: list of matchups 'matchups' (0vs1, 2vs3, etc), list of matchups with nicknames, list of 
	lists of team points 'teamsPoints'(teamPoints correspond to matchups list; 0qb, 1wr, 2rb, 3te, 4flx, 5def, 6k)
	"""
	# this parsing will get messed up if a team doesn't have a full bench.
	matchups = []
	matchupsNicknames = []
	for team in fantasyTeams:
		if team not in matchups:
			matchups.append(team)
			matchupsNicknames.append(fantasyTeams[team].nickname)
			matchups.append(fantasyTeams[team].matchup[week])
			matchupsNicknames.append(fantasyTeams[fantasyTeams[team].matchup[week]].nickname)
	teamsPoints = []
	for team in matchups:
		teamPoints = []
		teamRoster = fantasyTeams[team].roster[week]
		#print(team, len(teamRoster))
		teamPoints.append(teamRoster[0].points[week]) # qb
		teamPoints.append(teamRoster[1].points[week] + teamRoster[2].points[week] + teamRoster[3].points[week]) # wrs
		teamPoints.append(teamRoster[4].points[week] + teamRoster[5].points[week]) # rbs
		teamPoints.append(teamRoster[6].points[week]) # te
		teamPoints.append(teamRoster[7].points[week]) # flx
		if teamRoster[len(teamRoster)-1].position == 'DEF':
			teamPoints.append(teamRoster[len(teamRoster)-2].points[week]) # k
			teamPoints.append(teamRoster[len(teamRoster)-1].points[week]) # def
		else: # if there's an IR spot
			teamPoints.append(teamRoster[len(teamRoster)-3].points[week]) # k
			teamPoints.append(teamRoster[len(teamRoster)-2].points[week]) # def
		teamsPoints.append(teamPoints)
	for i in range(len(teamsPoints)):
		for j in range(len(teamsPoints[0])):
			if teamsPoints[i][j]<-20:
				teamsPoints[i][j]=-20
	return matchups, matchupsNicknames, teamsPoints



def plotMatchups(fantasyTeams, week, show, save):
	"""
	Plots the weekly projections for each team in the league.
	Argument: dictionary of fantasyTeam objects 'fantasyTeams', week to plot int 'week',
	boolean 'show', boolean 'save'
	Return:
	"""
	pos = ['qb','wr','rb','te','flx','k','def']
	matchups, matchupsNicknames, teamsPoints = makeMatchupData(fantasyTeams, week)
	#print(matchups, teamsPoints)
	for i in range(0,len(matchups),2):
		points1 = teamsPoints[i]
		points2 = teamsPoints[i+1]
		pos.append('')
		points1.append(points1[0]) # to make line connect to beginning
		points2.append(points2[0])
		#print(points1, points2)
		ax = plt.subplot(polar=True)
		angles = [(2*pi)*(n/7) for n in range(8)] # size of angle slices
		plt.xticks(angles, pos)
		ax.set_theta_offset(pi/2) # puts the first index on top
		ax.set_theta_direction(-1) # set radial direction
		ax.set_rlabel_position(0)
		plt.yticks([-20,0,20,40,60,80,100], ["-20","0","20","40","60","80","100"], color="grey", size=10)
		plt.ylim(-20,100)

		ax.plot(angles,points1,'b',linewidth=.75,label=str(matchupsNicknames[i])+': '
					+str(fantasyTeams[matchups[i]].points[week])+' pts')
		ax.fill(angles,points1,'b',alpha=.25)
		ax.plot(angles,points2,'r',linewidth=.75,label=str(matchupsNicknames[i+1])+': '
					+str(fantasyTeams[matchups[i+1]].points[week])+' pts')
		ax.fill(angles,points2,'r',alpha=.25)
		ax.legend(loc=(-0.15,0.9))
		ax.set_title(matchupsNicknames[i]+' VS '+matchupsNicknames[i+1], fontsize=20, fontweight='bold', position=(.5,1))

		if fantasyTeams[matchups[i]].points[week]>fantasyTeams[matchups[i+1]].points[week]:
			player = fantasyTeams[matchups[i]].roster[week][fantasyTeams[matchups[i]].mvp[week]]
		else:
			player = fantasyTeams[matchups[i+1]].roster[week][fantasyTeams[matchups[i+1]].mvp[week]]
		statsString = ''
		for stat in player.statsFormatted[week]:
			statsString += str(stat['statValue'])+' '+stat['stat']+': '+str(round(stat['statPoints'],2))+' pts\n'
		text = 'MVP: '+player.name+', '+player.position+'\n'+statsString+'TOTAL: '+str(round(player.points[week],2))+' pts'
		#print(text)
		plt.text(1.3*pi,220,text,bbox={'facecolor': 'yellow', 'alpha': 0.5, 'pad': 5}) # for polar chart x=angle y=radius 

		if save:
			plt.savefig('C:/Users/NeilS/Desktop/FantasyBoyzUSA/plots/plotMatchups/plotMatchupsWeek'+str(week)+'_'+str(int(i/2+1))+'.png')
		if show:
			plt.show()
		plt.close()



def plotTeamsProjectedWeeklyScoring(fantasyTeams, weekStart, weekEnd, show, save):
	"""
	Plots the weekly projections for each team in the league.
	Argument: dictionary of fantasyTeam objects 'fantasyTeams', weeks to plot from int 'weekStart' to int 'weekEnd',
	boolean 'show', boolean 'save'
	Return:
	"""
	teamNames = []
	seasonProjections = []
	weeks = [n for n in range(weekStart, weekEnd+1)]
	for team in fantasyTeams:
		teamNames.append(fantasyTeams[team].nickname)
		projections = []
		for week in range(weekStart, weekEnd+1):
			projections.append(fantasyTeams[team].projectedPoints[week])
		seasonProjections.append(projections)

	for i in range(len(seasonProjections)):
		plt.plot(weeks, seasonProjections[i], '.')
	plt.legend(teamNames,loc='lower left', fontsize='x-small')
	plt.ylabel('Projected Points')
	plt.xlabel('week')
	plt.xticks(weeks)
	plt.title('Projected Scoring', fontweight='bold')

	if save:
		plt.savefig('C:/Users/NeilS/Desktop/FantasyBoyzUSA/plots/plotLeague/plotTeamsProjectedWeeklyScoring.png')
	if show:
		plt.show()
	plt.close()



def plotTeamsPoints(fantasyTeams, weekStart, weekEnd, show, save):
	"""
	Makes a plot of the total projected points for, projected points against, actual points for, and 
	actual points against for each team for each week of the season.
	Argument: dictionary of fantasyTeam objects 'fantasyTeams', weeks to plot from int 'weekStart' to int 'weekEnd',
	 , boolean 'show', boolean 'save'
	Return:
	"""
	"""
	projectedWins = makeProjectedWins(fantasyTeams, weekStart, weekEnd)
	ranksList = []
	rank = 1
	while len(ranksList) < len(fantasyTeams):
		maxWins = -1
		for team in projectedWins:
			if projectedWins[team] > maxWins and team not in ranksList:
				maxWins = projectedWins[team]
				teamToRank = team
		ranksList.append(teamToRank)
	"""
	weeks = [n for n in range(weekStart, weekEnd+1)]
	weeksShift = [n+.25 for n in weeks]
	fig, axs = plt.subplots(len(fantasyTeams), 1, sharex=False, sharey=True) # figure with numTeams subplots, same x and y axes for all.
	fig.suptitle('Projected and Actual Scoring', fontweight='bold')
	fig.subplots_adjust(hspace = 1) # set horizontal space between axes
	fig.set_size_inches(5,10) # set size of figure
	yticks = [50,150]
	plt.yticks(yticks) # set labels for y axis
	plt.xlabel('week')
	plt.ylabel('Projected points for(blue) and against(yellow). Actual points for (green) and against(red)',position=(0,8))
	plotNum = 0
	for team in fantasyTeams:
		projectedPointsList = []
		projectedPointsAgainstList = []
		pointsList = []
		pointsAgainstList = []
		for i in range(weekStart, weekEnd+1):
			projectedPointsList.append(fantasyTeams[team].projectedPoints[i])
			projectedPointsAgainstList.append(fantasyTeams[team].projectedPointsAgainst[i])
			pointsList.append(fantasyTeams[team].points[i])
			pointsAgainstList.append(fantasyTeams[team].pointsAgainst[i])
		axs[plotNum].plot(weeks, projectedPointsAgainstList, 'y*')
		axs[plotNum].plot(weeks, projectedPointsList, 'b*')
		axs[plotNum].plot(weeksShift, pointsAgainstList, 'r.')
		axs[plotNum].plot(weeksShift, pointsList, 'g.')
		axs[plotNum].set_xticks(weeks)
		"""
		spacer1 = ' '*(30-len(team))
		axisTitle = team+spacer1+'Projected Wins: '+str(projectedWins[team])
		spacer2 = ' '*(50-len(axisTitle))
		axisTitle = fantasyTeams[team].teamName
		"""
		axs[plotNum].set_title(fantasyTeams[team].nickname)
		plotNum += 1

	if save:
		plt.savefig('C:/Users/NeilS/Desktop/FantasyBoyzUSA/plots/plotLeague/plotTeamsPoints.png')
	if show:
		plt.show()
	plt.close()



def plotWinsDistribution(fantasyTeams, weekStart, weekEnd, show, save):
	"""
	Makes a plot of the discrete probability distribution of total wins for each team.
	Argument: dictionary of fantasyTeam objects 'fantasyTeams', weeks to plot from int 'weekStart' to int 'weekEnd',
	 , boolean 'show', boolean 'save'
	Return:
	"""
	fig, axs = plt.subplots(len(fantasyTeams), 1, sharex=False, sharey=True) # figure with numTeams subplots, same x and y axes for all.
	fig.subplots_adjust(hspace = 1) # set horizontal space between axes
	fig.set_size_inches(5,10) # set size of figure
	fig.suptitle('Wins Distribution', fontweight='bold')
	yticks = [0,30]
	plt.ylim(0,30)
	plt.yticks(yticks) # set labels for y axis
	plt.xlabel('wins')
	plt.ylabel('Probability (%)',position=(0,8))

	wins = [i for i in range(weekEnd+1)] # a team can win between 0 and 13 games
	plotNum = 0
	for team in fantasyTeams:
		probList = []
		for i in range(weekStart,weekEnd+1):
			probList.append(fantasyTeams[team].winProbability[i])
		probDistList = probDist(probList)
		scaledProbDistList = [i*100 for i in probDistList]
		#print(team,probList,probDistList)
		maxIx = -1
		maxProb = -1
		for i in range(len(probDistList)):
			if probDistList[i]>maxProb:
				maxIx = i
				maxProb = probDistList[i]
		axs[plotNum].plot(wins, scaledProbDistList, 'bo')
		axs[plotNum].set_title(fantasyTeams[team].nickname)
		axs[plotNum].set_xticks(wins)
		axs[plotNum].annotate('', xy=(maxIx, 0), xycoords='data', xytext=(-15, 25), 
								textcoords='offset points', arrowprops=dict(arrowstyle = '->'),
					            horizontalalignment='right', verticalalignment='top')
		plotNum += 1

	if save:
		plt.savefig('C:/Users/NeilS/Desktop/FantasyBoyzUSA/plots/plotLeague/plotWinsDistribution.png')
	if show:
		plt.show()
	plt.close()



def plotStandings(fantasyTeams, weekStart, weekEnd, show, save):
	"""
	Plots the points for, points against, and bullshit score per week for each team in order of 
	their rank in the league.
	Argument: dictionary of fantasyTeam objects 'fantasyTeams', weeks to plot from int 'weekStart' to int 'weekEnd',
	 , boolean 'show', boolean 'save'
	Return:
	"""
	ranksList = []
	ranksListNicknames = []
	for i in range(1, len(fantasyTeams)+1):
		for team in fantasyTeams:
			if int(fantasyTeams[team].standingsRank) == i:
				ranksList.append(team)
				ranksListNicknames.append(fantasyTeams[team].nickname+'\n'+str(fantasyTeams[team].wins)+
										'-'+str(fantasyTeams[team].losses)+'-'+str(fantasyTeams[team].ties))
				break
	pointsForBigList = []
	pointsAgainstBigList = []
	for i in range(weekStart,weekEnd+1): 
		pointsForSmallList = []
		pointsAgainstSmallList = []
		for team in ranksList:
			pointsForSmallList.append(fantasyTeams[team].points[i])
			pointsAgainstSmallList.append(fantasyTeams[team].pointsAgainst[i])
		pointsForBigList.append(pointsForSmallList)
		pointsAgainstBigList.append(pointsAgainstSmallList)
	fig, axs = plt.subplots(2)
	fig.set_size_inches(10,7.5)
	fig.subplots_adjust(hspace = .5)
	plots = [0]*(weekEnd-weekStart+1) # array of plots, needed for legend
	plots[0] = axs[0].bar(ranksListNicknames, pointsForBigList[0])
	axs[1].bar(ranksListNicknames, pointsAgainstBigList[0])
	for j in range(len(pointsForBigList[0])): # begin annotate points for  
			text = str(pointsForBigList[0][j])
			axs[0].annotate(text,xy=(j,20),ha='center')
	for j in range(len(pointsAgainstBigList[0])): # begin annotate points against
			text = str(pointsAgainstBigList[0][j])
			axs[1].annotate(text,xy=(j,20),ha='center')
	bottomForList = [] # keeps track of the bottom to graph on
	bottomAgainstList = []
	for j in range(len(fantasyTeams)):
		bottomForList.append(pointsForBigList[0][j]) 
		bottomAgainstList.append(pointsAgainstBigList[0][j])	
	for i in range(weekStart, weekEnd):
		plots[i] = axs[0].bar(ranksListNicknames, pointsForBigList[i], bottom=bottomForList)
		axs[1].bar(ranksListNicknames, pointsAgainstBigList[i], bottom=bottomAgainstList)
		text = 'week'+str(i)
		for j in range(len(pointsForBigList[i])): # annotate points for
			text = str(pointsForBigList[i][j])
			if text!='0.0':
				height = 0
				for k in range(i):
					height += pointsForBigList[k][j]
				axs[0].annotate(text,xy=(j,height+20),ha='center')
		for j in range(len(pointsAgainstBigList[i])): # annotate points against
			text = str(pointsAgainstBigList[i][j])
			if text!='0.0':
				height = 0
				for k in range(i):
					height += pointsAgainstBigList[k][j]
				axs[1].annotate(text,xy=(j,height+20),ha='center')
		
		for j in range(len(fantasyTeams)):
			bottomForList[j] += pointsForBigList[i][j]
			bottomAgainstList[j] += pointsAgainstBigList[i][j]

		#print(bottomForList, bottomAgainstList)
	maxTotalFor = 0
	maxTotalAgainst = 0
	for i in range(len(fantasyTeams)): # annotate total scoring
		totalFor = 0
		totalAgainst = 0
		for j in range(weekEnd):
			totalFor += pointsForBigList[j][i]
			totalAgainst += pointsAgainstBigList[j][i]
		if totalFor>maxTotalFor: maxTotalFor = totalFor
		if totalAgainst>maxTotalAgainst: maxTotalAgainst = totalAgainst
		axs[0].annotate(str(round(totalFor,2)), xy=(i,totalFor+5), ha='center', fontweight='bold')
		axs[1].annotate(str(round(totalAgainst,2)), xy=(i,totalAgainst+5), ha='center', fontweight='bold')

	#print(maxTotalFor,maxTotalAgainst)
	axs[0].set_title('Points For')
	axs[1].set_title('Points Against')
	axs[0].set_ylim(0,maxTotalFor+70) # make space for annotations
	axs[1].set_ylim(0,maxTotalAgainst+70) 
	titles = []
	for i in range(len(plots)):
		titles.append('week'+str(i+1))
	fig.legend(plots,titles,ncol=len(plots),fontsize='x-small',handlelength=.5,loc='lower center')
	fig.suptitle('Standings', fontweight='bold')

	if save:
		plt.savefig('C:/Users/NeilS/Desktop/FantasyBoyzUSA/plots/plotLeague/plotStandings.png')
	if show:
		plt.show()
	plt.close()



def plotTotalBull(fantasyTeams, show, save):
	"""
	Plots the total bull score for each team in the league.
	Argument: dictionary of fantasyTeam objects 'fantasyTeams', boolean 'show', boolean 'save'
	Return:
	"""
	totalBullScore = []
	weekBull = []
	teamList = []
	for team in fantasyTeams:
		totalBullScore.append(fantasyTeams[team].totalBullshitScore)
		teamList.append(fantasyTeams[team].nickname)

	fig, ax = plt.subplots()	
	ax.bar(teamList, totalBullScore, color='red')
	fig.set_size_inches(7.5,5) # set size of figure

	maxBull = 0
	minBull = 0
	for i in range(len(fantasyTeams)): # annotate bars
		if totalBullScore[i]>=0: heightAdjust = 1
		else: heightAdjust = -3
		ax.annotate(str(round(totalBullScore[i],2)), xy=(i,totalBullScore[i]+heightAdjust), ha='center', fontweight='bold')
		if totalBullScore[i]>maxBull: maxBull = totalBullScore[i]
		if totalBullScore[i]<minBull: minBull = totalBullScore[i]
	ax.set_ylim(minBull-10,maxBull+10)
	
	ax.set_title('Total Bull Score', fontweight='bold')
	ax.axhline(0, color='black')
	if save:
		plt.savefig('C:/Users/NeilS/Desktop/FantasyBoyzUSA/plots/plotLeague/plotTotalBull.png')
	if show:
		plt.show()
	plt.close()



def plotWeeklyBull(fantasyTeams, weekStart, weekEnd, show, save):
	"""
	Plots the bull score for each team for each week of the season.
	Argument: dictionary of fantasyTeam objects 'fantasyTeams', weeks to plot from int 'weekStart' to int 'weekEnd',
	 , boolean 'show', boolean 'save'
	Return:
	"""
	teamList = []
	weeklyBull = []
	weeks = [n for n in range(weekStart,weekEnd+1)]
	for team in fantasyTeams:
		teamList.append(fantasyTeams[team].nickname)
		weekBull = []
		for i in range(weekStart, weekEnd+1):
			weekBull.append(fantasyTeams[team].bullshitScore[i])
		weeklyBull.append(weekBull)

	fig, axs = plt.subplots(len(fantasyTeams), sharex=False, sharey=True)
	fig.subplots_adjust(hspace = 1)
	fig.set_size_inches(5,10) # set size of figure
	fig.suptitle('Weekly Bull Score', fontweight='bold')

	maxBull = 0
	minBull = 0
	for i in range(len(fantasyTeams)):
		axs[i].bar(weeks, weeklyBull[i], color='red')
		axs[i].set_title(teamList[i])
		axs[i].axhline(0, color='black')
		axs[i].set_xticks(weeks)
		maxi = max(weeklyBull[i])
		mini = min(weeklyBull[i])
		if maxi>maxBull: maxBull=maxi
		if mini<minBull: minBull=mini
	if abs(maxBull)>abs(minBull): limit = abs(maxBull)
	else: limit = abs(minBull)
	limit = (int(int(limit+10)/10))*10
	plt.ylim((-1)*limit,limit)
	plt.xlabel('week')

	if save:
		plt.savefig('C:/Users/NeilS/Desktop/FantasyBoyzUSA/plots/plotLeague/plotWeeklyBull.png')
	if show:
		plt.show()
	plt.close()



def plotRosterPerformance(fantasyTeams, weekStart, weekEnd, show, save):
	"""
	Makes a plot of each teams pointsFor for each week of the season where roster data is available,
	split by roster position.
	Argument: dictionary of fantasyTeam objects 'fantasyTeams', weeks to plot from int 'weekStart' to int 'weekEnd',
	 , boolean 'show', boolean 'save'
	Return:
	"""

	for team in fantasyTeams:
		qbPoints = [0]*(weekEnd-weekStart+1)
		wrPoints = [0]*(weekEnd-weekStart+1)
		rbPoints = [0]*(weekEnd-weekStart+1)
		tePoints = [0]*(weekEnd-weekStart+1)
		flxPoints = [0]*(weekEnd-weekStart+1)
		kPoints = [0]*(weekEnd-weekStart+1)
		defPoints = [0]*(weekEnd-weekStart+1)
		weeks = [n for n in range(weekStart,weekEnd+1)]

		for i in range(weekEnd-weekStart+1):
			teamsFile = 'C:/Users/NeilS/Desktop/FantasyBoyzUSA/fantasyTeamsData/weekly/fantasyTeamsData_Week'+str(i+1)+'.pickle'
			with open(teamsFile, 'rb') as file:
				fantasyTeamsNew = pickle.load(file)
			for nflPlayer in fantasyTeamsNew[team].roster[i+1]:
				#print(nflPlayer.name)
				pass
			qbPoints[i] = fantasyTeamsNew[team].roster[i+1][0].points[i+1]
			wrPoints[i] = fantasyTeamsNew[team].roster[i+1][1].points[i+1] + fantasyTeamsNew[team].roster[i+1][2].points[i+1] + fantasyTeamsNew[team].roster[i+1][3].points[i+1]
			rbPoints[i] = fantasyTeamsNew[team].roster[i+1][4].points[i+1] + fantasyTeamsNew[team].roster[i+1][5].points[i+1]
			tePoints[i] = fantasyTeamsNew[team].roster[i+1][6].points[i+1]
			flxPoints[i] = fantasyTeamsNew[team].roster[i+1][7].points[i+1]
			try:
				kPoints[i] = fantasyTeamsNew[team].roster[i+1][12].points[i+1]
				defPoints[i] = fantasyTeamsNew[team].roster[i+1][13].points[i+1]
			except: # if a teams bench isn't full
				kPoints[i] = fantasyTeamsNew[team].roster[i+1][11].points[i+1]
				defPoints[i] = fantasyTeamsNew[team].roster[i+1][12].points[i+1]
			#print(team,i,qbPoints,wrPoints,rbPoints,tePoints,flxPoints,kPoints,defPoints)
		print
		
		fig = plt.subplot()
		labels = ['QB','WRs','RBs','TE','FLX','K','DEF']
		plt.stackplot(weeks,qbPoints,wrPoints,rbPoints,tePoints,flxPoints,kPoints,defPoints, labels=labels)
		plt.title(fantasyTeams[team].nickname+'\nRoster Performance', fontsize=18, fontweight='bold')
		plt.xlabel('Week')
		plt.ylabel('Fantasy Points')
		plt.ylim(0,250)
		plt.xticks(weeks)
		plt.legend(loc=(.95,.65))
		
		if save:
			plt.savefig('C:/Users/NeilS/Desktop/FantasyBoyzUSA/plots/plotRosterPerformance/plotRosterPerformance'+team+'.png')
		if show:
			plt.show()
		plt.close()



def makeLegacyData():
	"""
	Gets the legacy data and formats it for plotting.
	Arguement:
	Return: list of all legacy stats 'legacyStats'. The first entry of legacyStats is the team list, then 
	every entry is a stat. Each entry of a stat is a year. Each entry of a year is the stat value for each
	team in order of the teamList.
	"""
	with open('C:/Users/NeilS/Desktop/FantasyBoyzUSA/info/newLegacy.json','r') as file:
		legacy = json.load(file)

	regWinsBig = []
	leaderBig = []
	bigGamesBig = []
	regPointsBig = []
	postWinsBig = []
	champsBig = []
	standingBig = []
	teamList = []
	for team in legacy: teamList.append(team)
	year = 0 # corresponds to 2013 season
	while(year<8): # 7 seasons plus total
		regWinsSmall = []
		leaderSmall = []
		bigGamesSmall = []
		regPointsSmall = []
		postWinsSmall = []
		champsSmall = []
		standingSmall = []
		for team in legacy:
			regWinsSmall.append(legacy[team]['RegSesWins'][year])
			leaderSmall.append(legacy[team]['GamesLeader'][year])
			bigGamesSmall.append(legacy[team]['BigGames'][year])
			regPointsSmall.append(legacy[team]['RegSesPts'][year])
			postWinsSmall.append(legacy[team]['PlayoffWins'][year])
			champsSmall.append(legacy[team]['Championship'][year])
			standingSmall.append(legacy[team]['FinalStanding'][year])
		regWinsBig.append(regWinsSmall)
		leaderBig.append(leaderSmall)
		bigGamesBig.append(bigGamesSmall)
		regPointsBig.append(regPointsSmall)
		postWinsBig.append(postWinsSmall)
		champsBig.append(champsSmall)
		standingBig.append(standingSmall)
		year += 1

	for i in range(len(regWinsBig)): # turn all values into floats
		for j in range(len(regWinsBig[0])):
			if regWinsBig[i][j]=='-': regWinsBig[i][j] = 0
			if leaderBig[i][j]=='-': leaderBig[i][j] = 0
			if bigGamesBig[i][j]=='-': bigGamesBig[i][j] = 0
			if regPointsBig[i][j]=='-': regPointsBig[i][j] = 0
			if postWinsBig[i][j]=='-': postWinsBig[i][j] = 0
			if champsBig[i][j]=='-': champsBig[i][j] = 0
			if standingBig[i][j]=='-': standingBig[i][j] = 0
			regWinsBig[i][j] = float(regWinsBig[i][j])
			leaderBig[i][j] = float(leaderBig[i][j])
			bigGamesBig[i][j] = float(bigGamesBig[i][j])
			regPointsBig[i][j] = float(regPointsBig[i][j])
			postWinsBig[i][j] = float(postWinsBig[i][j])
			champsBig[i][j] = float(champsBig[i][j])
			standingBig[i][j] = float(standingBig[i][j])
	legacyStats = [teamList, regWinsBig, leaderBig, bigGamesBig, regPointsBig, postWinsBig, champsBig, standingBig]
	return legacyStats



def plotLegacy(show, save):
	"""
	Creates charts for all of the legacy data
	Argument: boolean 'show', boolean 'save'
	Return:
	"""
	legacyStats = makeLegacyData()
	plots = ['Regular Season Wins','Week Top Score','Big Games',
				'Regular Season Points','Postseason Wins','Championships','Final Standing']
	for k in range(1,len(plots)+1):
		fig, ax = plt.subplots()
		year = 2013
		ax.bar(legacyStats[0], legacyStats[k][0], label=str(year)) # plot first year
		bottomList = legacyStats[k][0] # track bottom to plot on top of
		if k != 6: # don't annotate championships
			for j in range(len(legacyStats[k][0])): # annotate first year
				if legacyStats[k][0][j] != 0:
					ax.annotate(str(int(legacyStats[k][0][j])), xy=(j,0.25), ha='center')
		for i in range(1,7): # plot next 6 years
			year += 1
			ax.bar(legacyStats[0], legacyStats[k][i], label=str(year), bottom=bottomList)
			if k != 6: # don't annotate championships
				for j in range(len(legacyStats[k][i])): # annotate bars
					if legacyStats[k][i][j] != 0:
						ax.annotate(str(int(legacyStats[k][i][j])), xy=(j,bottomList[j]+0.25), ha='center')
			for j in range(len(bottomList)): # update bottom list
				bottomList[j] += legacyStats[k][i][j]
		maxHeight = 0
		for i in range(len(legacyStats[0])):
			if bottomList[i] > maxHeight: maxHeight = bottomList[i]
			if k==7: text = str(legacyStats[k][7][i]) # annotate average for standings
			else: text = str(int(bottomList[i]))
			ax.annotate(text, xy=(i,bottomList[i]+maxHeight/30), ha='center', fontweight='bold')
		ax.set_ylim(0,maxHeight+maxHeight/10)
		if k==6: ax.set_yticks((1,2,3)) # set y axis for championships
		ax.legend()
		ax.set_title(plots[k-1], fontsize=18, fontweight='bold')
		fig.set_size_inches(10,7.5)
		if save:
			plt.savefig('C:/Users/NeilS/Desktop/FantasyBoyzUSA/plots/plotLegacy/plotLegacy'+plots[k-1]+'.png')
		if show:
			plt.show()
		plt.close()



def stackedBarTest():
	try: plt.close()
	except: pass
	x = [1,2,3,4,5]
	y = [[5]*5, [4]*5, [3]*5, [2]*5, [1]*5]
	ax = plt.plot()
	plt.bar(x,y[0], label='y0')
	for i in range(1,5):
		plt.bar(x,y[i], label='y'+str(i), bottom=y[i-1])
	plt.legend()
	plt.show()
	plt.close()

def liveChartTest():
	style.use('fivethirtyeight')
	fig = plt.figure()
	ax1 = fig.add_subplot(1,1,1)
	ani = animation.FuncAnimation(fig, animate, interval=1000)
	plt.show()

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
	ax1.plot(xs, ys)

def generateChaos():
	with open('C:/Users/NeilS/Desktop/FantasyBoyzUSA/plots/chaosData.txt','w+') as file:
		x = 0
		for i in range(1000):
			file.write(str(i)+','+str(x)+'\n')
			x = x**2 - 1.5
