var miridanApp = angular.module('miridanApp', ['ui.bootstrap']);

miridanApp.controller('EntityListController', function ($scope, $rootScope) {
  $scope.entities = [
    {'name': 'Evil Chest',
     'description': 'It is a spooky evil chest!',
 	 'imageurl': 'placeholder0.png'},
    {'name': 'Evil Eyeball Collection',
     'description': 'A spooky collection of evil eyeballs!',
     'imageurl': 'placeholder1.png'},
    {'name': 'Radish',
     'description': 'A regular radish.',
     'imageurl': 'placeholder2.png'}
  ];

  $scope.selectEntity = function(entity) {
    $rootScope.$broadcast('selectTarget', entity);
  };
});

miridanApp.controller('InventoryListController', function ($scope, $rootScope) {
  $scope.entities = [
    {'name': 'Evil Chest',
     'description': 'It is a spooky evil chest!',
 	 'imageurl': 'placeholder0.png'},
    {'name': 'Evil Eyeball Collection',
     'description': 'A spooky collection of evil eyeballs!',
     'imageurl': 'placeholder1.png'},
    {'name': 'Radish',
     'description': 'A regular radish.',
     'imageurl': 'placeholder2.png'}
  ];
});

miridanApp.controller('InputController', function ($scope, $rootScope) {
  $scope.targets = [];
  $scope.possibleActions = [{'name': 'explode'}, {'name': 'hug'}];
  $scope.selectedAction = $scope.possibleActions[0];

  $scope.$on('selectTarget', function(event, newtarget) {
    $scope.targets.push(newtarget);
  });

  $scope.doaction = function() {
    var actionstr = $scope.selectedAction.name;
    for(var i = 0; i < $scope.targets.length; ++i) {
      actionstr += (" [" + $scope.targets[i].name + "]");
    }
    $rootScope.$broadcast('addLogs', [{'text': actionstr}]);
  };
});

miridanApp.controller('LogController', function ($scope) {
  $scope.logs = [{'text': 'WELCOM TO MIRIDAN!!!'}];

  $scope.$on('addLogs', function(event, newlogs) {
    for(var i = 0; i < newlogs.length; ++i) {
      $scope.logs.push(newlogs[i]);
    }
  });
});