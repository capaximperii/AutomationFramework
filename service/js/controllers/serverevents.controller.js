var app = angular.module('AF');

app.controller('serverEventsCtrl', function ($scope, ServerResource) {
	$scope.events = null;

	$scope.loadAllEvents = function() {
		ServerResource.query(function(events){
			$scope.events = events;
		});
	}
	$scope.loadAllEvents();
});