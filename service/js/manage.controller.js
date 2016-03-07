var app = angular.module('AF');

app.controller('manageCtrl', function ($scope, ManageResource, $location, $http) {
	$scope.backup = function() {
		ManageResource.get(function(response){
			$scope.downurl = $location.protocol() + "://"+ $location.host() + ":" + $location.port() + response.url;
			$scope.message = response.message;
		});
	}

	$scope.restore = function() {
		var f = document.getElementById('file').files[0];
		var formData = new FormData();
		formData.append('file', f);
		$http({method: 'POST', url: '/api/manage',
			data: formData,
			headers: {'Content-Type': undefined },
			transformRequest: angular.identity})
		.success(function(response, status, headers, config) {
			$scope.upurl = $location.protocol() + "://"+ $location.host() + ":" + $location.port() + response.url;
			$scope.message = response.message;
		});
	}
});