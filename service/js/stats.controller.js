var app = angular.module('AF');

app.controller('statsCtrl', function ($scope, client, StatsResource) {
	$scope.client = client;
	$scope.loadStatsForClient = function(client) {
		StatsResource.get({ip: client.ip}, function(response){
			console.log(response);
		});
	}
});