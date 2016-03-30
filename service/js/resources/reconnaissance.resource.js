'use strict';

angular.module('AF')
    .factory('ReconnaissanceResource', function ($resource) {
        return $resource('/api/patterns/:id', {}, {
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