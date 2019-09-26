import pickle 
from pprint import PrettyPrinter

from fantasyBoyzUsa import (fantasyLeague, fantasyTeam, nflPlayer) # must be included so unpickling works
from fantasyBoyzUsaPlots import (plotTeamsProjectedWeeklyScoring, plotTeamsPoints, plotMatchups,
								plotRosterPerformance, plotWinsDistribution, plotStandings, liveChartTest,
								stackedBarTest, plotTotalBull, plotWeeklyBull, plotLegacy)




def prettyPrint(obj):
	"""
	Prints the dictionary real nice like.
	Argument: dictionary 'obj'
	"""
	pp = PrettyPrinter(indent=1)
	pp.pprint(obj)





def main():
	week = 3
	leagueFile = 'C:/Users/NeilS/Desktop/FantasyBoyzUSA/fantasyLeagueData/weekly/fantasyLeagueData_Week'+str(week)+'.pickle'
	teamsFile = 'C:/Users/NeilS/Desktop/FantasyBoyzUSA/fantasyTeamsData/weekly/fantasyTeamsData_Week'+str(week)+'.pickle'
	with open(leagueFile, 'rb') as file:
		fantasyLeague = pickle.load(file)
	with open(teamsFile, 'rb') as file:
		fantasyTeams = pickle.load(file)

	#prettyPrint(plotLegacy(fantasyTeams, True, False))
	#plotWeeklyBull(fantasyTeams, 1, 13, True, True)
	#plotTotalBull(fantasyTeams, True, True)
	#plotStandings(fantasyTeams, 1, 13, True, True)
	#plotWinsDistribution(fantasyTeams, 1, 13, True, True)
	#plotTeamsProjectedWeeklyScoring(fantasyTeams, 1, 13, True, True)
	#plotTeamsPoints(fantasyTeams, 1, 13, True, True)

	#plotLegacy(True, True)


	#plotRosterPerformance(fantasyTeams, 1, 3, True, True)	
	#plotMatchups(fantasyTeams,week,True,True)




	#stackedBarTest()
	
	#liveChartTest()




if __name__ == '__main__':
	main()