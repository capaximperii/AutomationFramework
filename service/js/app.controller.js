var app = angular.module('AF', ['ngResource', 'angularModalService', 'ui.router']);

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
		})
		.state('serverevent', {
			parent: 'menubar-page',
			url: '/serverevent',
			views: {
				'content@': {
					templateUrl: '/html/serverevent.html',
					controller: 'serverEventsCtrl'
				}
			}
		})
		.state('manage', {
			parent: 'menubar-page',
			url: '/manage',
			views: {
				'content@': {
					templateUrl: '/html/manage.html',
					controller: 'manageCtrl'
				}
			}
		}).state('settings', {
			parent: 'menubar-page',
			url: '/settings',
			views: {
				'content@': {
					templateUrl: '/html/settings.html',
					controller: 'settingsCtrl'
				}
			}
		}).state('help', {
			parent: 'menubar-page',
			url: '/help',
			views: {
				'content@': {
					templateUrl: '/html/help.html',
				}
			}
		});


	});