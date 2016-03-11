var app = angular.module('AF');

app.controller('dashboardCtrl', function ($scope, ClientsResource, StatsResource, ModalService) {
	$scope.clients = [];
	$scope.selectedClient = null;

	$scope.loadAllClients = function() {
		$scope.message = "Loading ...";
		ClientsResource.query(function(clients){
			$scope.clients = clients;
			$scope.message = "Loaded";
		});
	}

	$scope.findOne = function(ipAddress) {
		ClientsResource.get(ipAddress, function(client){
			$scope.selectedClient = client;
		});
	}

	$scope.displayProgressRank = function(client) {
		var progress;
		if (client.current == 0)
			progress = 'Not started';
		else if (client.current == 10000)
			progress = 'Finished';
		else if (client.current == -10000)
			progress = 'Not checked in'
		else
			progress = 'Now running ' + client.current;
		return progress;
	}

	var showConfigurePopup = function(client) {
		ModalService.showModal({
			templateUrl: '/html/configure.html',
			inputs: {
			    client: client,
			},
			controller: 'configureCtrl',
			}).then(function(modal) {
			  modal.element.modal();
		});
     }
	
	var showStatsPopup = function(client) {
		ModalService.showModal({
			templateUrl: '/html/stats.html',
			inputs: {
			    client: client,
			},
			controller: 'statsCtrl',
			}).then(function(modal) {
			  modal.element.modal();
		});
     }

	$scope.configure = function(client) {
		ClientsResource.get({ip: client.ip}, function(client){
			$scope.selectedClient = client;
			$scope.message = "Configuring client " + client.ip;
			showConfigurePopup(client);
		});
	}
	
	$scope.showStats = function(client) {
		showStatsPopup(client);
	}

	$scope.launch = function(client) {
		client = {'ip': client.ip, 'history':0, 'current':0 ,'progress':0 };
		ClientsResource.update(client , function(message) {
			$scope.message = "Remote installer initiated for " + client.ip;
		});	
	}
	
	$scope.addClient = function(newclient) {
		client = response = {'ip': newclient.ip, 'history':0, 'current':0 ,'progress':0 };
		ClientsResource.save(client , function(c) {
			if(c.ip != null) {
				$scope.clients.push(c);
				$scope.message = "Client added, click on settings to configure test cases.";
			}
			else {
				newclient.ip = "";
				$scope.message = "The client you added, already exists.";
			}
		});
	}

	$scope.showHistoryPopup = function(client) {
		ModalService.showModal({
			templateUrl: '/html/history.html',
			inputs: {
			    client: client,
			},
			controller: function($scope, client, close) { 
	            $scope.client = client;
	            $scope.close = close;

	            $scope.getPercent = function(n, total) {
	            	if (total <= 0) return 0;
	            	return n/total * 100;
	            }
	          }
			}).then(function(modal) {
			  modal.element.modal();
		});
     }


	$scope.loadAllClients();
});