var app = angular.module('AF');

app.controller('reconnaissanceCtrl', function ($scope, $state, ReconnaissanceResource) {

	$scope.splitView = null;

	$scope.loadAllData = function() {
		ReconnaissanceResource.get(function(data) {
			var consolidated = [];
			var split = [];

			for (k in data) {
				var ip = k;
				var tests = data[ip];
				for(test in tests) {
					var label = test
					var value = 0;

					/*SPLIT*/
					if (tests[label].Pass != null) {
						var found = false;
						var index = -1; 
						for (var i=0; i < split.length; i ++ ) {
							if (split[i].key == ip ) {
								index = i; 
								found = true; 
							}
						}
						if (found == false) {
							split.push({key: ip, values: [ parseInt(tests[label].Pass), parseInt(tests[label].Fail)]});
						} else {
							var tmp = split[index].values;
							tmp[0] += parseInt(tests[label].Pass);
							tmp[1] += parseInt(tests[label].Fail);
						}

						/* CONSOLIDATED */
						var found = false;
						var index = -1;
						var values = [parseInt(tests[label].Pass), parseInt(tests[label].Fail)];
						for (var i=0; i<consolidated.length; i++ ) {
							if (consolidated[i].key == label) {
								found = true;
								index = i;
							}
						}
						if (found == false) {
							consolidated.push({key: label, values: values});
						} else {
							var tmp = consolidated[index].values;
							tmp[0] += values[0];
							tmp[1] += values[1];
						}
					}
				}
				if ($scope.splitData == null && split.length > 0 && split[0].key != null)
					$scope.splitData = [{key: split[0].key, values: [split[0].values, [10,10]]}];
				if ($scope.consolidatedData == null && consolidated.length > 0 && consolidated[0].key != null)
					$scope.consolidatedData = [{key: consolidated[0].key, values: [consolidated[0].values, [10,10]]}];
				$scope.splitView = true;
			}
		});
	}
	$scope.loadAllData();
});
