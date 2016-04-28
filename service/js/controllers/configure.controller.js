var app = angular.module('AF');

app.controller('configureCtrl', function ($scope, close, client, ModalService, TestsResource) {
	$scope.allTests = [];
	$scope.selectedTests =[];
	$scope.close = close;
	$scope.client = client;
	$scope.variables = [];
	$scope.currentTest = null;
	$scope.filterText = "";

	$scope.loadAllTests = function() {
		TestsResource.query(function(tests){
			angular.forEach(tests, function(t){
				var test = JSON.parse(t);
				$scope.allTests.push(test);
			});
		});
	}

	$scope.findOne = function(ipAddress) {
		TestsResource.query({ip: ipAddress}, function(tests){
			angular.forEach(tests, function(t){
				var test = JSON.parse(t);
				$scope.selectedTests.push(test);
			});
		});
	}

	$scope.addTest = function() {
		var rank = $scope.selectedTests.length + 1;
		var copy = angular.copy($scope.currentTest);
		for(var i =0; i < $scope.variables.length; i ++ ) {
			for(var j = 0; j < copy.commands.length; j ++ ) {
				if(copy.commands[j].lastIndexOf('${', 0) === 0 && copy.commands[j].lastIndexOf('Echo') > 1) {
					copy.commands[j] = copy.commands[j].replace(new RegExp(
							'Echo ' + $scope.variables[i].old, 'g'),'Echo ' + $scope.variables[i].value);
				}
			}
		}
		copy.name = copy.name + '-' + rank
		copy.rank = rank;
		$scope.selectedTests.push(copy);
		$scope.currentTest = null;
		$scope.variables = [];
	}

	$scope.removeTest = function(test) {
		for( var i= 0 ; i < $scope.selectedTests.length; i ++){
			if (test.name == $scope.selectedTests[i].name)
				$scope.selectedTests.splice(i,1);
		};
	}

	$scope.selectTest = function(test) {
		$scope.currentTest = angular.copy(test);
		$scope.updateVariablesForTest();
	}

	$scope.updateVariablesForTest = function() {
		$scope.variables = [];
		var commands = [];
		if($scope.currentTest) commands = $scope.currentTest.commands;
		for (var i =0 ; i < commands.length; i ++ ) {
			var c = commands[i];
			if(commands[i].lastIndexOf('${', 0) === 0 && commands[i].lastIndexOf('Echo') > 1) {
				var value = commands[i].split('Echo')[1].trim();
				var v = {name: commands[i].split('=')[0], value: value, old: value};
				$scope.variables.push(v);
			}
		}
	}

	$scope.save = function() {
		TestsResource.update({ip: client.ip, config: JSON.stringify($scope.selectedTests)},
		function(result){
			$scope.message = result.message;
		});
	}
    
	$scope.showMindmapPopup = function () {
		var mindmap = {name: $scope.client.ip};
		mindmap.children = [];
		angular.forEach($scope.selectedTests, function(t){
			var test = {name: t.name };
			test.children = [];
			angular.forEach(t.commands, function(command){
				test.children.push({name: command});
			});
			mindmap.children.push(test);
		});

		ModalService.showModal({
			templateUrl: '/html/mindmap.html',
			inputs: {
			    ip: $scope.client.ip,
			    tests: mindmap
			},
			controller: 'mindCtrl' 
			}).then(function(modal) {
			  modal.element.modal();
			});
		}

		$scope.filterTests = function(test) {
			if($scope.filterText.length == 0) return true;
			var regExp = new RegExp($scope.filterText, "i");
			return test.name.match(regExp);
		}

		function sortSelected () {
			$scope.selectedTests.sort(function(a, b){
			return a.rank - b.rank;
		});

		}

		$scope.moveDown = function(test) {
			for (var i = 0; i < $scope.selectedTests.length; i ++) {
				if (test.name == $scope.selectedTests[i].name) {
					if (i == $scope.selectedTests.length - 1) // we are the last
						return;
					var tmprank = $scope.selectedTests[i + 1].rank;
					$scope.selectedTests[i + 1].rank = test.rank;
					test.rank = tmprank;
					sortSelected();
					break;
				}
			}
		}

		$scope.moveUp = function(test) {
			for (var i = 0; i < $scope.selectedTests.length; i ++) {
				if (test.name == $scope.selectedTests[i].name) {
					if (i == 0) // we are the first
						return;
					var tmprank = $scope.selectedTests[i - 1].rank;
					$scope.selectedTests[i - 1].rank = test.rank;
					test.rank = tmprank;
					sortSelected();
					break;
				}
			}
		}

		$scope.loadAllTests();
		$scope.findOne(client.ip);
});
