var app = angular.module('AF');

app.controller('statsCtrl', function ($scope, client, StatsResource, ModalService) {
	$scope.client = client;
	$scope.stats = null;
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

	$scope.loadStatsForClient(client);
});