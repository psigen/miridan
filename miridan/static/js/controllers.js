var miridanApp = angular.module('miridanApp', ['ui.bootstrap']);

miridanApp.controller('EntityListController', function ($scope, $rootScope, $http) {
  $scope.entities = [];
  $scope.url = '../world';
  //$scope.url = 'test/testworld';

  $scope.getUpdate = function() {
    $http.get($scope.url).success(function(data) {
      $scope.entities = data.entities;
    });
  }

  $scope.getUpdate();

  $scope.selectEntity = function(entity) {
    $rootScope.$broadcast('selectTarget', entity);
  };

  $scope.$on('refreshData', function(event) {
    $scope.getUpdate();
  });
});

miridanApp.controller('InventoryListController', function ($scope, $rootScope) {
  $scope.entities = [];
});

miridanApp.controller('InputController', function ($scope, $rootScope, $http) {
  $scope.targets = [];
  $scope.possibleActions = [{'name': 'explode', 'args': ['target', 'explosive']}, 
                            {'name': 'hug', 'args': ['target_player']}];
  $scope.selectedAction = $scope.possibleActions[0];
  $scope.url = '../action';
  //$scope.url = 'test/testaction';
  $scope.posturl = '../action/';

  $http.get($scope.url).success(function(data) {
    $scope.possibleActions = [];
    var curaction;
    for(var k in data.actions) {
      curaction = data.actions[k];
      curaction.name = k;
      $scope.possibleActions.push(curaction);
    }
    $scope.selectedAction = $scope.possibleActions[0];
  });

  $scope.$on('selectTarget', function(event, newtarget) {
    $scope.targets.push(newtarget);
  });

  $scope.formatActionName = function(action) {
    return action.name + ":[" + action.args.join("][") + "]";
  }

  $scope.doaction = function() {
    var theaction = $scope.selectedAction;
    var actionstr = $scope.selectedAction.name;
    var aargs = $scope.selectedAction.args;
    for(var i = 0; i < $scope.targets.length; ++i) {
      actionstr += (" [" + (aargs[i] || "?") + ":" + $scope.targets[i].name + "]");
    }
    $rootScope.$broadcast('addLogs', [{'message': actionstr}]);

    var purl = $scope.posturl + theaction.name + "?";
    var arglist = [];
    for(var j = 0; j < theaction.args.length && j < $scope.targets.length; ++j) {
      arglist.push(theaction.args[j] + "=" + $scope.targets[j].name);
    }
    purl += arglist.join("&");
    console.log("PURL: " + purl);

    $http.put(purl).success(function(data) {
      console.log("Action succeeded?");
      $rootScope.$broadcast('refreshData', 12);
    }).error(function(data, status) {
      console.log("Action failed: ");
      console.log(data);
      console.log(status);
      $rootScope.$broadcast('refreshData', 12);
    });
  };
});

miridanApp.controller('LogController', function ($scope, $http) {
  $scope.logs = [{'message': 'WELCOM TO MIRIDAN!!!'}];
  $scope.url = '../log';
  //$scope.url = 'test/testlog';

  $scope.getUpdate = function() {
    $http.get($scope.url).success(function(data) {
      $scope.logs = data.logs;
    });
  }

  $scope.getUpdate();

  $scope.$on('addLogs', function(event, newlogs) {
    for(var i = 0; i < newlogs.length; ++i) {
      $scope.logs.push(newlogs[i]);
    }
  });

  $scope.$on('refreshData', function(event) {
    $scope.getUpdate();
  });
});