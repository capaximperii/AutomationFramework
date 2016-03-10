(function() {

  'use strict';

  var module = angular.module('angularModalService', []);

  module.factory('ModalService', ['$document', '$compile', '$controller', '$http', '$rootScope', '$q', '$timeout', '$templateCache',
    function($document, $compile, $controller, $http, $rootScope, $q, $timeout, $templateCache) {

    var body = $document.find('body');
    
    function ModalService() {

      var self = this;
      var getTemplate = function(template, templateUrl) {
        var deferred = $q.defer();
        if(template) {
          deferred.resolve(template);
        } else if(templateUrl) {
          var cachedTemplate = $templateCache.get(templateUrl);
          if(cachedTemplate !== undefined) {
            deferred.resolve(cachedTemplate);
          }
          else {
            $http({method: 'GET', url: templateUrl, cache: true})
              .then(function(result) {
                $templateCache.put(templateUrl, result.data);
                deferred.resolve(result.data);
              })
              .catch(function(error) {
                deferred.reject(error);
              });
          }
        } else {
          deferred.reject("No template or templateUrl has been specified.");
        }
        return deferred.promise;
      };

      self.showModal = function(options) {
        
        var deferred = $q.defer();
        var controller = options.controller;
        if(!controller) {
          deferred.reject("No controller has been specified.");
          return deferred.promise;
        }

        getTemplate(options.template, options.templateUrl)
          .then(function(template) {
            var modalScope = (options.scope || $rootScope).$new();
            var closeDeferred = $q.defer();
            var inputs = {
              $scope: modalScope,
              close: function(result, delay) {
                if(delay === undefined || delay === null) delay = 0;
                $timeout(function () {
                  closeDeferred.resolve(result);
                }, delay);
              }
            };
            if(options.inputs) {
              for(var inputName in options.inputs) {
                inputs[inputName] = options.inputs[inputName];
              }
            }
            var modalElementTemplate = angular.element(template);
            var linkFn = $compile(modalElementTemplate);
            var modalElement = linkFn(modalScope);
            inputs.$element = modalElement;
            var modalController = $controller(controller, inputs);
            if (options.appendElement) {
              options.appendElement.append(modalElement);
            } else {
              body.append(modalElement);
            }
            var modal = {
              controller: modalController,
              scope: modalScope,
              element: modalElement,
              close: closeDeferred.promise
            };

            modal.close.then(function(result) {
              modalScope.$destroy();
              modalElement.remove();
            });

            deferred.resolve(modal);

          })
          .catch(function(error) {
            deferred.reject(error);
          });

        return deferred.promise;
      };

    }

    return new ModalService();
  }]);

}());