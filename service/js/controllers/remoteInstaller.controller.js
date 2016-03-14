var app = angular.module('AF');

app.controller('remoteInstallerCtrl', function ($scope, RemoteInstallerResource) {
	$scope.clients = null;
	$scope.loadRemoteInstaller = function() {
		RemoteInstallerResource.get(function(response){
			$scope.clients = response.clients;
			$scope.schedules = response.schedules;
			for (var i =0; i < response.schedules.length; i ++ ) {
				var schedule = response.schedules[i];
				schedule.date = new Date(0, 0, 0, schedule.hour, schedule.minute, 0, 0);
			}
		});
	}

	$scope.addSchedule = function() {
		var hour = $scope.schedule.time.getHours();
		var minute = $scope.schedule.time.getMinutes();
		var data = {'ip': $scope.schedule.ip, 'hour': hour, 'minute': minute };

		var timestamp=Date.parse($scope.schedule.time);
		if (isNaN(timestamp)==true || $scope.schedule.ip.length < 7) {
			$scope.schedule.time = new Date();
			return;
		}


		RemoteInstallerResource.save(data, function(response){
			$scope.clients = response.clients;
			$scope.schedules = response.schedules;
			for (var i =0; i < response.schedules.length; i ++ ) {
				var schedule = response.schedules[i];
				schedule.date = new Date(0, 0, 0, schedule.hour, schedule.minute, 0, 0);
			}
		});
	}

	$scope.removeSchedule = function (schedule) {
		RemoteInstallerResource.delete(schedule, function(response){
			$scope.clients = response.clients;
			$scope.schedules = response.schedules;
			for (var i =0; i < response.schedules.length; i ++ ) {
				var schedule = response.schedules[i];
				schedule.date = new Date(0, 0, 0, schedule.hour, schedule.minute, 0, 0);
			}
		});
	}

	$scope.loadRemoteInstaller();
});
