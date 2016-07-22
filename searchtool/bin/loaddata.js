// Copyright IBM Corp. 2015,2016. All Rights Reserved.
// Node module: loopback-example-database
// This file is licensed under the MIT License.
// License text available at https://opensource.org/licenses/MIT


var path = require('path');



var app = require(path.resolve(__dirname, '../server/server'));


var ds = app.datasources.searchtoolapi;
var tables = ["user", "accessToken", "userCredential", "userIdentity", "ACL", "RoleMapping", "Role"];


ds.automigrate(tables, function (err) {
    if (err) throw err;

    var users = [
        {
            email: 'john.doe@ibm.com',
            username: 'John',
            createdAt: new Date(),
            lastModifiedAt: new Date(),
            password: 'pwd',
        },
        {
            email: 'jane.doe@ibm.com',
            username: 'Jane',
            createdAt: new Date(),
            lastModifiedAt: new Date(),
            password: 'pwd',
        },
        {
            email: 'bob@projects.com',
            username: 'Bob',
            createdAt: new Date(),
            lastModifiedAt: new Date(),
            password: 'bob',
        },
    ];
    var count = users.length;
    users.forEach(function (user) {
        app.models.user.create(user, function (err, model) {
            if (err) throw err;

            console.log('Created:', model);

            if (count === 0) {
                ds.disconnect();
            }
        });
    });
});
