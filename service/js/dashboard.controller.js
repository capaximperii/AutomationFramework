var app = angular.module('AF');

app.controller('dashboardCtrl', function ($scope, ClientsResource, ModalService) {
	$scope.clients = [];
	$scope.selectedClient = null;

	$scope.loadAllClients = function() {
		ClientsResource.query(function(clients){
			$scope.clients = clients;
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

	var showPopup = function(client) {
              ModalService.showModal({
                templateUrl: '/html/configure.html',
                inputs: {
				    client: client,
				},
                controller: 'configureCtrl',
                }).then(function(modal) {
                  modal.element.modal();
              });
            };      

	$scope.configure = function(client) {
		ClientsResource.get({ip: client.ip}, function(client){
			$scope.selectedClient = client;
			showPopup(client);
		});
	}

	$scope.addClient = function(newclient) {
		client = response = {'ip': newclient.ip, 'history':0, 'current':0 ,'progress':0 };
		ClientsResource.save(client , function(c) {
			if(c.ip != null)
				$scope.clients.push(c);
			else
				newclient.ip = "Already exists?"
		});
	}

	$scope.loadAllClients();
});