var phonecatApp = angular.module('AF', []);

phonecatApp.controller('statsCtrl', function ($scope) {
  $scope.clients = [
    {'ip': 'Nexus S',
     'log': 'Fast just got faster with Nexus S.'},
    {'ip': 'Motorola XOOM™ with Wi-Fi',
     'log': 'The Next, Next Generation tablet.'}
  ];
});