var config = require('../../server/config.json'),
    path = require('path');

module.exports = function( user ) {
  console.log('> ************REG ********');
  //send verification email after registration

  /* user.afterRemote('create', function(context, user, next) {
    console.log('> user.afterRemote triggered');

    var options = {
      type: 'email',
      to: user.email,
      from: 'noreply@c-iq.com',
      subject: 'Thanks for registering.',
      template: path.resolve(__dirname, '../../server/views/verify.ejs'),
      redirect: '/verified',
      user: user
    };

    user.verify(options, function(err, response, next) {

      if (err) return next(err);

      console.log('> verification email sent:', response);

      context.res.render('response', {
        title: 'Signed up successfully',
        content: 'Please check your email and click on the verification link ' +
            'before logging in.',
        redirectTo: '/',
        redirectToLinkText: 'Log in'
      });
    });
  }); */

  //send password reset link when requested
  user.on('resetPasswordRequest', function(info) {
    var url = 'http://' + config.host + ':' + config.port + '/reset-password';
    var html = 'Greetings -<br><br>We understand you lost your TFSPets password. Click <a href="' + url + '?access_token=' +
        info.accessToken.id + '">here</a> to reset your password <br><br>Thanks <br><br>This email was sent by:<br>The Filling Station Pet Supplies<br>10115 SW Nimbus Avenue<br>Tigard, OR 97223<br>503-352-4269<br>';

    user.app.models.Email.send({
      to: info.email,
      from: info.email,
      subject: 'TFSPets Password Reset',
      html: html
    }, function(err) {
      if (err) return console.log('> error sending password reset email');
      console.log('> sending password reset email to:', info.email);
    });
  });
};
