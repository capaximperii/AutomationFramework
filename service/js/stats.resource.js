'use strict';

angular.module('AF')
    .factory('StatsResource', function ($resource, DateUtils) {
        return $resource('/api/clients/:id', {}, {
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