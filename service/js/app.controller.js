var app = angular.module('AF', ['ngResource', 'ui.router']);

app.controller('MainCtrl', function ($scope, $state) {
	$state.go('dashboard');
});

app.config(function ($stateProvider) {
	$stateProvider
		.state('menubar-page', {
	        'abstract': true,
	        views: {
	            'menubar@': {
	                templateUrl: '/html/leftmenu.html'
	                //controller: 'NavbarController'
	            }
	        }
	    })
		.state('dashboard', {
			parent: 'menubar-page',
			url: '/dashboard',
			views: {
				'content@': {
					templateUrl: '/html/dashboard.html',
					controller: 'dashboardCtrl'
				}
			}
		});
	});