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
    console.log(entity);
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

miridanApp.controller('InputController', function ($scope) {
  $scope.targets = [];
  $scope.possibleActions = [{'name': 'explode'}, {'name': 'hug'}];
  $scope.selectedAction = $scope.possibleActions[0];

  $scope.$on('selectTarget', function(event, newtarget) {
    console.log(newtarget);
    $scope.targets.push(newtarget);
  });

  $scope.doaction = function() {
  	console.log("Going to try taking an action! " + $scope.selectedAction.name + ":" + $scope.targets);
  };
});

miridanApp.controller('LogController', function ($scope) {
  $scope.logs = [];
  for(var i = 0; i < 100; ++i) {
  	$scope.logs.push({'text': "Blargh " + i})
  }
});