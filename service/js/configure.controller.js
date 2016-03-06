var app = angular.module('AF');

app.controller('configureCtrl', function ($scope, close, client, TestsResource) {
	$scope.tests = [];
	$scope.selectedClient = client;
	$scope.selectedTests =[];
	$scope.close = close;

	$scope.loadAllTests = function() {
		TestssResource.query(function(tests){
			$scope.tests = tests;
		});
	}

	$scope.findOne = function(ipAddress) {
		TestssResource.query(ipAddress, function(tests){
			$scope.selectedTests = tests;
		});
	}

	$scope.addTest = function(newclient) {
	}
});