from yahoo_oauth import OAuth2
from yahoo_fantasy_api import league, game, team
import os
import json
import pickle 
from datetime import datetime
from pprint import PrettyPrinter

"""
from fantasyBoyzUsaPlots import (plotTeamsProjectedWeeklyScoring, plotPowerRankings,
								makeProjectedWins)
"""


class fantasyLeague:
	"""
	Holds the basic info for the fantasy league.
	"""
	def __init__(self):
		self.leagueKey = ''
		self.leagueId = ''
		self.name = ''
		self.url = ''
		self.numTeams = 0
		self.currentWeek = 0
		self.startWeek = 0
		self.startDate = ''
		self.endWeek = 0
		self.endDate = ''
		self.gameKey = ''
		self.statSettings = {}
		self.medianPoints = [0]*18 # median league score for each week


class fantasyTeam:
	"""
	Holds info for each fantasy team.
	"""
	def __init__(self):
		self.projectedPoints = [0]*18 # for each week of season
		self.totalProjectedPoints = 0
		self.projectedPointsAgainst = [0]*18
		self.totalProjectedPointsAgainst = [0]*18
		self.winProbability = [0]*18 # for each week of season
		self.totalWinProbability = 0
		self.points = [0]*18 # for each week of season
		self.totalPoints = 0
		self.pointsAgainst = [0]*18
		self.totalPointsAgainst = 0
		self.mvp = [0]*18 # for each week of season, entry is index of roster at that week
		self.matchup = ['']*18 # for each week of season
		self.teamKey = ''
		self.teamId = ''
		self.teamName = ''
		self.nickname = ''
		self.teamUrl = ''
		self.logoUrl = ''
		self.waiverPriority = 0
		self.numberOfMoves = 0
		self.numberOfTrades = 0
		self.draftGrade = ''
		self.draftRecapUrl = ''
		self.managerId = ''
		self.managerName = ''
		self.managerLoggedIn = 0
		self.isComissioner = 0
		self.managerEmail = ''
		self.imageUrl = ''
		self.standingsRank = ''
		self.weekRank = [0]*18 # pointsFor rank for each week
		self.bullshitScore = [0]*18
		self.totalBullshitScore = 0
		self.wins = 0
		self.losses = 0
		self.ties = 0
		self.winPercentage = ''
		self.bigGames = 0
		self.roster = ['']*18 # a list of weeks, each with a list of player objects



class nflPlayer:
	"""
	Holds info for all players currently or formerly rostered
	"""
	def __init__(self):
		self.name = ''
		self.position = ''
		self.photoUrl = ''
		self.team = ''
		self.status = ''
		self.notes = ''
		self.playerKey = ''
		self.statsRaw = ['notUpdated',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] # entry 0 is a flag, then a list of weeks each a dictionary of stats, in raw form from the api
		self.statsFormatted = [0]*18 # a list for each week of the season, each week a list of stats, each stat a dictionary
		self.points = [0]*18 # points for each week of season




def makeOauth():
	"""
	Makes the oauth2 authorization object based on unique key and secret.
	Argument:
	Return: oauth object 'oauth'
	"""
	myKey = 'dj0yJmk9R0pxc0dOeVZYQVJMJmQ9WVdrOU5qWjBRMGx5TXpBbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTFi'
	mySecret = 'a207ce01c63ca298d40f0010ddf06a7ed9f8ba75'
	if not os.path.exists('oauth2.json'):
	    creds = {'consumer_key': myKey, 'consumer_secret': mySecret}
	    with open('oauth2.json', "w") as f:
	        f.write(json.dumps(creds))
	oauth = OAuth2(None, None, from_file='oauth2.json')
	if not oauth.token_is_valid():
   		oauth.refresh_access_token()
	
	return oauth




def getLeagueId(oauth):
	"""
	gets the league id
	Argument: oauth object 'oauth'
	Return: string 'leagueID'
	"""
	myGame = game.Game(oauth,'nfl') # return NFL fantasy game object
	prettyPrint(vars(myGame))
	try:
		leagueId = myGame.league_ids(2019)[0] # returns 1 element list, 0th element is leagueID string
	except Exception as e:
		print(e)
		print('>> couldn''t get leagueId')
		leagueId = 0

	return leagueId




def prettyPrint(obj):
	"""
	Prints the dictionary real nice like.
	Argument: dictionary 'obj'
	"""
	pp = PrettyPrinter(indent=1)
	pp.pprint(obj)




def buildDictMap(dictionary, file, indent):
	"""
	Outputs to txt file a map of the dictionary while flagging lists.
	Argument: dictionary 'dictionary', string 'file', string 'indent'
	Return:
	"""
	for key in dictionary:
		file.write(indent+str(key)+'\n')
		#print(indent+str(key))
		if type(dictionary[key]) is list:
			indent = '     ' + indent
			for value in dictionary[key]:
				toWrite = indent
				for i in range(30):
					toWrite += str(value)[i]
					if i == len(value): break 
				file.write(toWrite+'(...)\n')
				#print(toWrite+'(...)')					
				if type(value) is dict:
					indent = '     ' + indent
					buildDictMap(value,file,indent)
					indent = ' '*(len(indent)-5)
			indent = ' '*(len(indent)-5)
		if type(dictionary[key]) is dict:
			indent = '     ' + indent
			buildDictMap(dictionary[key],file,indent)
			indent = ' '*(len(indent)-5)




def makeNewLeague(scoreboard):
	"""
	Builds a new fantasyLeague object and updates its data according to the scoreboard dictionary.
	Argument: dictionary 'scoreboard'
	Return: fantasyLeague object 'newFantasyLeague'
	"""
	newFantasyLeague = fantasyLeague()
	relevantData = scoreboard['fantasy_content']['league'][0]
	newFantasyLeague.leagueKey = relevantData['league_key']
	newFantasyLeague.leagueId = relevantData['league_id']
	newFantasyLeague.name = relevantData['name']
	newFantasyLeague.url = relevantData['url']
	newFantasyLeague.numTeams = relevantData['num_teams']
	newFantasyLeague.currentWeek = relevantData['current_week']
	newFantasyLeague.startWeek = relevantData['start_week']
	newFantasyLeague.startDate = relevantData['start_date']
	newFantasyLeague.endWeek = relevantData['end_week']
	newFantasyLeague.endDate = relevantData['end_date']
	newFantasyLeague.gameKey = newFantasyLeague.leagueKey[0] + newFantasyLeague.leagueKey[1] + newFantasyLeague.leagueKey[2]
	return newFantasyLeague




def buildTeams(scoreboard, league):
	"""
	Builds a list of all teams in the league and updates their data according to the scoreboard data. 
	Argument: dictionary 'scoreboard', fantasyLeague object 'league'
	Return: dictionary of fantasyTeam objects 'fantasyTeams'
	"""
	fantasyTeams = {}
	relevantData = scoreboard['fantasy_content']['league'][1]['scoreboard']['0']['matchups']
	for i in range(int(league.numTeams/2)): # nested loops to parse the matchups
		for j in range(2):
			newFantasyTeam = fantasyTeam()
			newFantasyTeam.teamKey = relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][0][0]['team_key']
			newFantasyTeam.teamId = relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][0][1]['team_id']
			newFantasyTeam.teamName = relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][0][2]['name']
			newFantasyTeam.teamUrl = relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][0][4]['url']
			newFantasyTeam.logoUrl = relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][0][5]['team_logos'][0]['team_logo']['url']
			newFantasyTeam.waiverPriority = relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][0][7]['waiver_priority']
			newFantasyTeam.numberOfMoves = relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][0][9]['number_of_moves']
			newFantasyTeam.numberOfTrades = relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][0][10]['number_of_trades']
			newFantasyTeam.draftGrade = relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][0][16]['draft_grade']
			newFantasyTeam.draftRecapUrl = relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][0][16]['draft_recap_url']
			newFantasyTeam.managerId = relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][0][19]['managers'][0]['manager']['manager_id']
			newFantasyTeam.managerName = relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][0][19]['managers'][0]['manager']['nickname']
			try: newFantasyTeam.isComissioner = relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][0][19]['managers'][0]['manager'][is_commissioner]
			except: pass
			newFantasyTeam.managerEmail = relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][0][19]['managers'][0]['manager']['email']
			newFantasyTeam.imageUrl = relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][0][19]['managers'][0]['manager']['image_url']
			newFantasyTeam.winProbability[1] = float(relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][1]['win_probability'])
			newFantasyTeam.points[1] = float(relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][1]['team_points']['total'])
			newFantasyTeam.projectedPoints[1] = float(relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][1]['team_projected_points']['total'])
			fantasyTeams.update({newFantasyTeam.teamName: newFantasyTeam})
	return fantasyTeams




def updateWeeklyTeamData(fantasyTeams, oauth, league):
	"""
	Updates the weekly data for each fantasy team.
	Argument: dictionary of fantasyTeam objects 'fantasyTeams', oauth object 'oauth',
	fantasyLeague object 'league'
	Return:
	"""
	for k in range(1,int(league.endWeek)+1):
		url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+str(league.leagueId)+'/scoreboard;week='+str(k)
		response = oauth.session.get(url, params={'format': 'json'})
		scoreboard = response.json()
		relevantData = scoreboard['fantasy_content']['league'][1]['scoreboard']['0']['matchups']
		if relevantData['count'] == 0: # if there is no data for this week
			break
		for i in range(int(league.numTeams/2)): 
			for j in range(2):
				winProbability = float(relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][1]['win_probability'])
				points = float(relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][1]['team_points']['total'])
				projectedPoints = float(relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][1]['team_projected_points']['total'])
				teamName = relevantData[str(i)]['matchup']['0']['teams'][str(j)]['team'][0][2]['name']
				if j==0: teamName1 = teamName # keep track of team names to assign matchups
				if j==1: teamName2 = teamName
				fantasyTeams[teamName].winProbability[k] = winProbability
				fantasyTeams[teamName].points[k] = points
				fantasyTeams[teamName].projectedPoints[k] = projectedPoints
			fantasyTeams[teamName1].matchup[k] = teamName2
			fantasyTeams[teamName1].pointsAgainst[k] = fantasyTeams[teamName2].points[k]
			fantasyTeams[teamName1].projectedPointsAgainst[k] = fantasyTeams[teamName2].projectedPoints[k]
			fantasyTeams[teamName2].matchup[k] = teamName1
			fantasyTeams[teamName2].pointsAgainst[k] = fantasyTeams[teamName1].points[k]
			fantasyTeams[teamName2].projectedPointsAgainst[k] = fantasyTeams[teamName1].projectedPoints[k] 




def updateTotalScoring(fantasyTeams):
	"""
	Sums the points, projected points, and win probability for each team. 
	Argument: dictionary of fantasyTeam objects 'fantasyTeams'
	Return:
	"""
	for team in fantasyTeams:
		for i in range(len(fantasyTeams[team].projectedPoints)):
			fantasyTeams[team].totalProjectedPoints += fantasyTeams[team].projectedPoints[i]
			fantasyTeams[team].totalPoints += fantasyTeams[team].points[i]
			fantasyTeams[team].totalWinProbability += fantasyTeams[team].winProbability[i]
			fantasyTeams[team].totalBullshitScore += fantasyTeams[team].bullshitScore[i]




def updateStandings(fantasyTeams, oauth, league):
	"""
	Updates the standingsRank, wins, losses, and ties for each team in the league. 
	Argument: dictionary of fantasyTeam objects 'fantasyTeams', oauth object 'oauth',
	fantasyLeague object 'league'
	Return:
	"""
	url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+str(league.leagueId)+'/standings'
	response = oauth.session.get(url, params={'format': 'json'})
	standings = response.json() 
	relevantData = standings['fantasy_content']['league'][1]['standings'][0]['teams']
	with open('C:/Users/NeilS/Desktop/FantasyBoyzUSA/info/dictMaps/standingsDictMap.txt','w+') as file:
		buildDictMap(standings,file,'')
	for i in range(len(fantasyTeams)):
		teamName = relevantData[str(i)]['team'][0][2]['name']
		try:
			managerLoggedIn = relevantData[str(i)]['team'][0][3]['is_owned_by_current_login']
			fantasyTeams[teamName].managerLoggedIn = managerLoggedIn
		except: pass
		fantasyTeams[teamName].standingsRank = relevantData[str(i)]['team'][2]['team_standings']['rank']
		fantasyTeams[teamName].wins = relevantData[str(i)]['team'][2]['team_standings']['outcome_totals']['wins']
		fantasyTeams[teamName].losses = relevantData[str(i)]['team'][2]['team_standings']['outcome_totals']['losses']
		fantasyTeams[teamName].ties = relevantData[str(i)]['team'][2]['team_standings']['outcome_totals']['ties']
		fantasyTeams[teamName].winPercentage = relevantData[str(i)]['team'][2]['team_standings']['outcome_totals']['percentage']




def updateRosters(fantasyTeams, oauth, league,weekStart,weekEnd):
	"""
	Updates rosters for every team in the league for given weeks. 
	Argument: dictionary of fantasyTeam objects 'fantasyTeams', oauth object 'oauth',
	fantasyLeague object 'league', int 'weekStart', int 'weekEnd'
	Return:
	"""
	noMoreRosters = False # if the roster data isn't available
	for i in range(1,len(fantasyTeams)+1):
		for j in range(weekStart,weekEnd+1): # int(league.endWeek)+1):
			url = 'https://fantasysports.yahooapis.com/fantasy/v2/team/'+str(league.leagueId)+'.t.'+str(i)+'/roster;week='+str(j)
			response = oauth.session.get(url, params={'format': 'json'})
			roster = response.json()
			relevantData = roster['fantasy_content']['team'][1]['roster']['0']['players']
			try: 
				teamName = roster['fantasy_content']['team'][0][2]['name']
			except Exception as e:
				print('>> updateRosters exception at week',j,':',e)
				noMoreRosters = True
				break
			weekRoster = []
			#print(teamName,'week',j)
			for k in range(len(relevantData)-1):
				playerInfoPointer = 0 # some players have additional injury information which pushes back the indices			
				newPlayer = nflPlayer()
				newPlayer.name = relevantData[str(k)]['player'][0][2]['name']['full']
				newPlayer.playerKey = relevantData[str(k)]['player'][0][1]['player_id']
				try: 
					newPlayer.team = relevantData[str(k)]['player'][0][6]['editorial_team_abbr'] 
				except: # if a player has an injury status
					try:
						newPlayer.team = relevantData[str(k)]['player'][0][7]['editorial_team_abbr'] 
						playerInfoPointer = 1 
					except: # if a player has injury notes
						newPlayer.team = relevantData[str(k)]['player'][0][8]['editorial_team_abbr']
						playerInfoPointer = 2
				#print(relevantData[str(k)]['player'][0])
				if playerInfoPointer==1:
					try:
						newPlayer.status = relevantData[str(k)]['player'][0][3]['status']
					except: # sometimes there's a note without a status
						newPlayer.notes = relevantData[str(k)]['player'][0][3]['injury_note']
				if playerInfoPointer==2:
					newPlayer.status = relevantData[str(k)]['player'][0][3]['status']
					newPlayer.notes = relevantData[str(k)]['player'][0][4]['injury_note'] 
				newPlayer.position = relevantData[str(k)]['player'][0][9+playerInfoPointer]['display_position']
				newPlayer.photoUrl = relevantData[str(k)]['player'][0][10+playerInfoPointer]['image_url']
				weekRoster.append(newPlayer)
				fantasyTeams[teamName].roster[j] = weekRoster
			for player in fantasyTeams[teamName].roster[1]:
				#print('   ',player.name,player.playerKey)
				pass
			print('>>    team',i,'roster week',j,'updated ',end='\r')
		if noMoreRosters:
			break
	with open('C:/Users/NeilS/Desktop/FantasyBoyzUSA/info/dictMaps/rosterDictMap'+str(j)+'.txt','w+') as file:
				buildDictMap(roster,file,'')




def updateNflPlayerStats(oauth, league, fantasyTeams, weekStart, weekEnd):
	"""
	Updates the stats for each rostered player from weekStart to weekEnd.
	Argument: oauth object 'oauth', fantasyLeague object 'league', dictionary of fantasyTeam objects 'fantasyTeams',
	int 'weekStart', int 'weekEnd'
	Return:
	"""
	#urlFile = open('C:/Users/NeilS/Desktop/FantasyBoyzUSA/info/testing/playerStatsUrls5.txt','w')
	for team in fantasyTeams: # each fantasy team
		for i in range(len(fantasyTeams[team].roster)): # each week in roster
			for j in range(len(fantasyTeams[team].roster[i])): # each player in week
				nflPlayer = fantasyTeams[team].roster[i][j]
				if nflPlayer.statsRaw[0]=='notUpdated': # if updating multiple weeks, don't update a players stats twice
					for k in range(weekStart, weekEnd+1):
						print('   ',team,k,nflPlayer.name,'          ',end='\r')
						url = 'https://fantasysports.yahooapis.com/fantasy/v2/player/'+league.gameKey+'.p.'+nflPlayer.playerKey+'/stats;type=week;week='+str(k)
						#urlFile.write(league.gameKey+'   '+nflPlayer.name+'   '+nflPlayer.playerKey+'   '+url+'\n'+team+' '+str(i)+' '+str(j)+' '+str(k)+'\n\n')
						try:
							response = oauth.session.get(url, params={'format': 'json'})
						except Exception as e:
							print('>> oauth.session.get exception:  ',e)
						try:
							nflPlayerStats = response.json()
						except Exception as e:
							print('>> response.json() exception:  ',e,'\n',team,i,nflPlayer.name,k)
						nflPlayer.statsRaw[k] = nflPlayerStats['fantasy_content']['player'][1]['player_stats']['stats']
				nflPlayer.statsRaw[0]=='updated'
				if j==0:
					#print(nflPlayer.statsRaw)
					pass
	with open('C:/Users/NeilS/Desktop/FantasyBoyzUSA/info/dictMaps/nflPlayerStatsDictMap.txt','w+') as file:
		buildDictMap(nflPlayerStats,file,'')
		pass
	#urlFile.close()




def formatNflPlayerStats(teams, league, week):
	"""
	References the league stat dictionary to format the stats for each player and update the players total points for the week.
	Argument: fantasyLeague object 'league', dictionary of fantasyTeam objects 'teams', int 'week' which week to format
	Return:
	"""
	for team in teams:
		#print(team,teams[team].points[week])
		for i in range(len(teams[team].roster[week])):
			nflPlayer = teams[team].roster[week][i]
			#print('   ',nflPlayer.name)
			totalPoints = 0
			statList = []
			for i in range(len(nflPlayer.statsRaw[week])):
				nflPlayerStatValue = int(nflPlayer.statsRaw[week][i]['stat']['value'])
				if nflPlayerStatValue > 0:
					statId = int(nflPlayer.statsRaw[week][i]['stat']['stat_id'])
					try:
						statAbbr = league.statSettings[statId]['statAbbr']
						statValue = float(league.statSettings[statId]['value'])
						validStat = True
					except:
						validStat = False
					if validStat:
						statPoints = nflPlayerStatValue*statValue
						totalPoints += statPoints
						statDict = {'stat':statAbbr,'statValue':nflPlayerStatValue,'statPoints':statPoints}
						statList.append(statDict)
						nflPlayer.points[week] = totalPoints
			nflPlayer.statsFormatted[week] = statList
			nflPlayer.points[week] = totalPoints
			#print('      ',statList)
			#print('      ',totalPoints)
		#print()




def makeStatSettings(oauth, league):
	"""
	Makes a dictionary of the statSettings that is referenced when player stats are formatted.
	Argument: oauth object 'oauth', fantasyLeague object 'league'
	Return: 
	"""
	statSettings = {}
	stat = {}
	url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+league.leagueId+'/settings'
	response = oauth.session.get(url, params={'format': 'json'})
	leagueSettings = response.json()
	#print(leagueSettings['fantasy_content']['league'][1]['settings'][0]['stat_modifiers']['stats'])
	statIdList = leagueSettings['fantasy_content']['league'][1]['settings'][0]['stat_categories']['stats']
	for i in range(len(statIdList)):
		statId = statIdList[i]['stat']['stat_id']
		statFullName = statIdList[i]['stat']['name']
		statShortName = statIdList[i]['stat']['display_name']
		stat = {'statName':statFullName,'statAbbr':statShortName}
		statSettings[statId] = stat
	statValues = leagueSettings['fantasy_content']['league'][1]['settings'][0]['stat_modifiers']['stats']
	for i in range(len(statValues)):
		statId = statValues[i]['stat']['stat_id']
		statValue = statValues[i]['stat']['value']
		statSettings[statId].update({'value':statValue})
	#prettyPrint(statSettings)
	with open('C:/Users/NeilS/Desktop/FantasyBoyzUSA/info/dictMaps/leagueSettingsDictMap.txt','w+') as file:
		buildDictMap(leagueSettings,file,'')
	league.statSettings = statSettings




def makeTeamsNicknames(fantasyTeams):
	"""
	Creates nicknames for the teamName of the fantasyTeams, which is the first word of the teamName.
	Argument: dictionary of fantasyTeam objects 'fantasyTeams'
	Return:
	"""
	for team in fantasyTeams:
		nickname = team[0]+team[1]+team[2]
		for i in range(3,len(team)):
			if team[i].islower() and team[i]!=' ':
				nickname += team[i]
			else:
				break
		if nickname[len(nickname)-1] == ' ':
			nickname = nickname[0]+nickname[1]
		fantasyTeams[team].nickname = nickname




def updateBullshit(teams, league):
	"""
	Updates the median points scored for each week, updates points scored ranks for each week,
	updates bullshit score for each week.
	Argument: dictionary of fantasyTeam objects 'teams', fantasyLeague object 'league'
	Return:
	"""
	for i in range(1, 14):
		teamsList = []
		pointsList = []
		for team in teams:
			teamsList.append(team)
			pointsList.append(teams[team].points[i])
		for j in range(len(pointsList)-1):
			for k in range(j+1,len(pointsList)):
				if pointsList[j]<pointsList[k]:
					temp1 = pointsList[j]
					temp2 = teamsList[j]
					pointsList[j] = pointsList[k]
					teamsList[j] = teamsList[k]
					pointsList[k] = temp1
					teamsList[k] = temp2
		league.medianPoints[i] = (pointsList[int(len(pointsList)/2)]+pointsList[int((len(pointsList)/2)-1)])/2
		for j in range(len(pointsList)):
			teams[teamsList[j]].weekRank[i] = j+1
		for team in teams:
			if teams[team].weekRank[i]<=len(teams)/2 and teams[team].points[i]<teams[team].pointsAgainst[i]:
				teams[team].bullshitScore[i] = league.medianPoints[i] - teams[team].points[i]
			elif teams[team].weekRank[i]>len(teams)/2 and teams[team].points[i]>teams[team].pointsAgainst[i]:
				teams[team].bullshitScore[i] = league.medianPoints[i] - teams[team].points[i]




def updateMvps(fantasyTeams):
	"""
	Looks at the rosters of each team for each week and finds the player with the most points.
	Argument: dictionary of fantasyTeam objects 'fantasyTeams'
	Return: 
	"""
	player = nflPlayer()
	validPositions = [0,1,2,3,4,5,6,7] # only starters can be mvp
	for team in fantasyTeams: # teams
		for i in range(len(fantasyTeams[team].roster)): # weeks
			maxPoints = 0
			for j in range(len(fantasyTeams[team].roster[i])): # players
				validPositions.append(len(fantasyTeams[team].roster[i])-1) # add def to valid positions
				validPositions.append(len(fantasyTeams[team].roster[i])-2) # add k to valid positions
				player = fantasyTeams[team].roster[i][j]
				if player.points[i]>maxPoints:
					if (player.position=='QB' and player.points[i]<40) or j not in validPositions:
						pass
					#print(player.name, player.points[i])
					else:
						maxPoints = player.points[i]
						fantasyTeams[team].mvp[i] = j
				validPositions.pop()
				validPositions.pop()

	"""
	for team in fantasyTeams:
		for i in range(1,len(fantasyTeams[team].mvp)):
			ix = fantasyTeams[team].mvp[i]
			try:
				print(team,i,fantasyTeams[team].roster[i][ix].name)
			except:
				pass
	"""




def saveOldLegacy():
	"""
	Creates a dictionary of old legacy data and saves it as 'oldLegacy.json'.
	Arguement: 
	Return: 
	"""
	with open ('C:/Users/NeilS/Desktop/FantasyBoyzUSA/info/oldLegacy.txt','r') as file:
		lines = file.readlines()
	legacy = {}
	lineix = 0
	for i in range(10):
		stats = {}
		player = lines[lineix].split()[0]
		for j in range(7):
			line = lines[lineix+2+j].split()
			stat = [line[1], line[2], line[3], line[4], line[5], line[6]]
			stats.update({line[0]:stat})
		legacy.update({player:stats})
		lineix += 10
	with open('C:/Users/NeilS/Desktop/FantasyBoyzUSA/info/legacy.json','w+') as file:
		json.dump(legacy,file)
	print(legacy)
	print('>> old legacy data saved')




def updateLegacy(fantasyTeams, weekStart, weekEnd):
	"""
	Updates Fantasy Boyz legacy data and saves it as 'newLegacy.json'
	Argument: dictionary of fantasyTeam objects 'fantasyTeams', bounds of weeks to look at int 'weekStart'
	and int 'weekEnd'
	Return:
	"""
	with open('C:/Users/NeilS/Desktop/FantasyBoyzUSA/info/legacy.json','r') as file:
		legacy = json.load(file)
	for team in legacy:
		found = False
		notUpdated = False
		for teamNow in fantasyTeams:
			if fantasyTeams[teamNow].nickname == team:
				found = True
				if len(legacy[team]['Championship'])<7:
					notUpdated = True
					thisTeam = fantasyTeams[teamNow].nickname
					thatTeam = teamNow
					break
		if found and notUpdated:
			legacy[thisTeam]['RegSesWins'].append(fantasyTeams[thatTeam].wins) # wins
			leader = 0
			for i in range(weekStart, weekEnd+1):
				if fantasyTeams[thatTeam].weekRank[i]==1:
					leader += 1
			legacy[thisTeam]['GamesLeader'].append(leader) # games leader
			legacy[thisTeam]['RegSesPts'].append(fantasyTeams[thatTeam].totalPoints) # season points
			legacy[thisTeam]['FinalStanding'].append(fantasyTeams[thatTeam].standingsRank) # standings rank
			legacy[thisTeam]['PlayoffWins'].append('-') # postseason wins
			legacy[thisTeam]['Championship'].append('-') # championships
			legacy[thisTeam]['BigGames'].append(fantasyTeams[thatTeam].bigGames) # big games
		if not found:
			#print('!!!')
			legacy[team]['RegSesWins'].append('-')
			legacy[team]['GamesLeader'].append('-')
			legacy[team]['BigGames'].append('-')
			legacy[team]['RegSesPts'].append('-')
			legacy[team]['PlayoffWins'].append('-')
			legacy[team]['Championship'].append('-') # postseason wins
			legacy[team]['FinalStanding'].append('-') # championships
	for team in legacy: # add sum to legacy stats
		statCount = 0 # the final stat (league standing) is totaled as an average
		for stat in legacy[team]:
			statTotal = 0
			validStats = 7
			for item in legacy[team][stat]:
				try: statTotal += float(item)
				except Exception as e: validStats -= 1
			if statCount==6: statTotal /= validStats
			legacy[team][stat].append(round(statTotal,2))
			statCount += 1
	with open('C:/Users/NeilS/Desktop/FantasyBoyzUSA/info/newLegacy.json','w+') as file:
		json.dump(legacy, file)
	"""
	for team in legacy:
		print(team)
		print(legacy[team])
		print()
	"""



def makeBigGames(fantasyTeams, weekStart):
	"""
	Finds the number of big games for each team for the current season. A big game is 25% more points than
	the league average for the season.
	Argument: dictionary of fantasyTeam objects 'fantasyTeams', int 'weekStart' is used to know how many
	weeks are included in totalPoints.
	Return: 
	"""
	totalPoints = 0
	for team in fantasyTeams:
		totalPoints += sum(fantasyTeams[team].points)
	leagueAvg = totalPoints/(len(fantasyTeams)*weekStart)
	for team in fantasyTeams:
		for item in fantasyTeams[team].points:
			if item>(1.25*leagueAvg):
				fantasyTeams[team].bigGames += 1
	#print(leagueAvg)
	for team in fantasyTeams:
		#print(team, fantasyTeams[team].bigGames)
		pass


def getDataTest(url):
	"""
	Attempts to grab data from the yahoo api; if successful, the data is printed. 
	Argument: string 'url'
	Return:
	"""
	oauth = makeOauth()
	response = oauth.session.get(url, params={'format': 'json'})
	try:
		received = response.json()
	except Exception as e:
		print('>> response.json() exception:',e)
	if received:
		prettyPrint(received)




def initializeLeague(weekStart, weekEnd, finalize):
	"""
	Runs all of the functions to initialize all of the league data. 
	Argument: int 'weekStart' and int 'weekEnd' for the bounds of updateRosters and updateNflPlayerStats,
	boolean 'finalize' if the week is over.
	Return: fantasyLeague object 'fantasyLeague', dictionary of fantasyTeam objects 'fantasyTeams' 
	"""
	oauth = makeOauth()
	print('>> oauth created')
	leagueId = getLeagueId(oauth)

	if leagueId:
		url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+leagueId+'/scoreboard;week=0'
		response = oauth.session.get(url, params={'format': 'json'})
		scoreboard = response.json() # makes a json/dictionary object
		with open('C:/Users/NeilS/Desktop/FantasyBoyzUSA/info/dictMaps/scoreboardDictMap.txt','w+') as file:
			buildDictMap(scoreboard,file,'')

		fantasyLeague = makeNewLeague(scoreboard)
		fantasyLeague.leagueId = leagueId
		print('>> league created')
		fantasyTeams = buildTeams(scoreboard, fantasyLeague)
		makeTeamsNicknames(fantasyTeams)
		print('>> teams created')
		makeStatSettings(oauth, fantasyLeague)
		print('>> league settings updated')
		updateWeeklyTeamData(fantasyTeams, oauth, fantasyLeague)
		print('>> weekly projections updated')
		updateBullshit(fantasyTeams, fantasyLeague)
		print('>> bullshit updated')
		updateTotalScoring(fantasyTeams)
		print('>> team scoring updated')
		updateStandings(fantasyTeams, oauth, fantasyLeague)
		print('>> league standings updated')
		makeBigGames(fantasyTeams, weekStart)
		print('>> big games updated')
		print('>> updating team rosters...')
		updateRosters(fantasyTeams, oauth, fantasyLeague,weekStart, weekEnd)
		print('>> team rosters updated               ')
		print('>> updating player stats...')
		updateNflPlayerStats(oauth,fantasyLeague,fantasyTeams,weekStart, weekEnd)
		print('>> player stats updated                       ') 
		formatNflPlayerStats(fantasyTeams,fantasyLeague,weekStart)
		print('>> player stats formatted')
		updateMvps(fantasyTeams)
		print('>> weekly mvps updated')
		updateLegacy(fantasyTeams,1,weekEnd)
		print('>> legacy updated')
		if finalize:
			teamsFile = 'C:/Users/NeilS/Desktop/FantasyBoyzUSA/fantasyTeamsData/weekly/fantasyTeamsData_Week'+str(weekStart)+'.pickle'
			leagueFile = 'C:/Users/NeilS/Desktop/FantasyBoyzUSA/fantasyLeagueData/weekly/fantasyLeagueData_Week'+str(weekStart)+'.pickle'
		else:
			time = datetime.now()
			newTime = time.strftime("%m-%d-%Y_%H-%M")
			teamsFile = 'C:/Users/NeilS/Desktop/FantasyBoyzUSA/data/fantasyTeamsData/live/fantasyTeamsData_'+newTime+'.pickle'
			leagueFile = 'C:/Users/NeilS/Desktop/FantasyBoyzUSA/data/fantasyLeagueData/live/fantasyLeagueData_'+newTime+'.pickle'
		with open(teamsFile,'wb+') as file: # wb for write byte
			pickle.dump(fantasyTeams,file)
		with open(leagueFile,'wb+') as file:
			pickle.dump(fantasyLeague,file)
		print('>> league and team data saved')
		print('>> Week',weekStart,'league initialization complete!')

		return fantasyLeague, fantasyTeams
	return 0,0




def main():
	"""
	Only update one week at a time because too many calls need to be made to the api otherwise. 
	"""
	#getDataTest(url = 'http://fantasysports.yahooapis.com/fantasy/v2/league/390.l.139892/players')
	#saveOldLegacy()

	fantasyLeague, fantasyTeams = initializeLeague(4,4,True)


if __name__ == '__main__':
	main()