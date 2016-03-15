var app = angular.module('AF');

app.controller('statsCtrl', function ($scope, client, close, StatsResource, ClientsResource, ModalService) {
	$scope.client = client;
	$scope.stats = null;
	$scope.close = close;
	
	$scope.loadStatsForClient = function(c) {
		StatsResource.get({ip: c.ip}, function(stats){
			$scope.stats = stats;
		});
	}

	$scope.showConsolePopup = function (test) {

		ModalService.showModal({
			templateUrl: '/html/console.html',
			inputs: {
			    output: test.console,
			},
			controller: function($scope, output, close) { 
	            $scope.output = output;
	            $scope.close = close;
	          }
			}).then(function(modal) {
			  modal.element.modal();
		});
	}

	$scope.getPercent = function(type) {
		var count = 0;
		if ( $scope.stats == null ) return 0;
		var total = $scope.stats.testoutput.length;
		if ( total == 0 ) return 0;
		angular.forEach($scope.stats.testoutput, function(test)  {
			if (test.result == type) count ++; 		
		});

		return count / total * 100;
	}

	$scope.isRunning = function() {
		if ( $scope.stats == null ) return false;

		for(var i=0; i < $scope.stats.testoutput.length; i ++)  {
			var test = $scope.stats.testoutput[i];
			if (test.result == "Pending")  return true;	
		};
		return false;
	}

	$scope.abort = function() {
		client.abort = true;
		ClientsResource.delete({ip: client.ip});
	}

	$scope.loadStatsForClient(client);
});
