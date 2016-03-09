var app = angular.module('AF');

app.controller('remoteInstallerCtrl', function ($scope, RemoteInstallerResource) {
	$scope.clients = null;
	$scope.loadRemoteInstaller = function() {
		RemoteInstallerResource.get(function(clients){
			$scope.clients = clients;
		});
	}
	$scope.loadRemoteInstaller();
});
