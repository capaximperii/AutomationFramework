var app = angular.module('AF');

app.controller('settingsCtrl', function ($scope, $state, SettingsResource) {
	$scope.settings = null;
	
	$scope.loadAllSettings = function() {
		SettingsResource.get(function(settings){
			$scope.settings = settings;
		});
	}

	$scope.saveSettings = function() {
		SettingsResource.update($scope.settings, function(result) {
			$scope.message = "Settings have been saved."
		});
	}
	$scope.loadAllSettings();
});
