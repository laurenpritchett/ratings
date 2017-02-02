<script>

  console.log("READING javascript");

  function setLoginButton(user_id){
    console.log("ajax worked");
    if (user_id){
        var userHomePage = '<a href="/user/{}"'.format(user_id);
        $("#login-button").html(userHomePage);
    } else {
        $("#logout-button").hide();
    }
  };

  function checkLoginStatus(){
    console.log("called function");
    $.get('/check-status', setLoginButton);
  
  };

  checkLoginStatus();

  </script>