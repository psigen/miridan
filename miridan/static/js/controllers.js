var miridanApp = angular.module('miridanApp', []);

miridanApp.controller('EntityListController', function ($scope) {
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

miridanApp.controller('InventoryListController', function ($scope) {
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
  $scope.whatever = 12;

  $scope.doaction = function() {
  	if($scope.text) {
  		console.log("Going to try taking an action! " + $scope.text);
  		$scope.text = "";
  	}
  };
});

miridanApp.controller('LogController', function ($scope) {
  $scope.logs = [];
  for(var i = 0; i < 100; ++i) {
  	$scope.logs.push({'text': "Blargh " + i})
  }
});