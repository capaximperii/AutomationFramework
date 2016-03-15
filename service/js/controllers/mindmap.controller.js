var app = angular.module('AF');

app.controller('mindCtrl', function ($scope, ip, tests, close) {
    $scope.ip = ip;
    $scope.close = close;
    $scope.tests = tests;
});
