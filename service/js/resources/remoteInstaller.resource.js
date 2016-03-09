'use strict';

angular.module('AF')
    .factory('RemoteInstallerResource', function ($resource) {
        return $resource('/api/remoteInstaller/:id', {}, {
            'query': { method: 'GET', isArray: true},
            'get': {
                method: 'GET',
                transformResponse: function (data) {
                    data = angular.fromJson(data);
                    return data;
                }
            },
            'update': { method:'PUT' }
        });
    });