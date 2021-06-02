function message(status, shake=false, id="") {
  if (shake) {
    $("#"+id).effect("shake", {direction: "right", times: 2, distance: 8}, 250);
  } 
  document.getElementById("feedback").innerHTML = status;
  $("#feedback").show().delay(2000).fadeOut();
}

function error(type) {
  $("."+type).css("border-color", "#E14448");
}

var login = function() {
  $.post({
    type: "POST",
    url: $LOGIN,
    data: {"username": $("#login-user").val(), 
           "password": $("#login-pass").val()},
    success(response){
      var status = JSON.parse(response)["status"];
      if (status === "Login successful") { location.reload(); }
      else { error("login-input"); }
    }
  });
};


$(document).ready(function() {
  
  $(document).on("click", "#login-button", login);
  $(document).keypress(function(e) {if(e.which === 13) {login();}});
  
  $(document).on("click", "#signup-button", function() {
    $.post({
      type: "POST",
      url: "/signup",
      data: {"username": $("#signup-user").val(), 
             "password": $("#signup-pass").val(), 
             "email": $("#signup-mail").val()},
      success(response) {
        var status = JSON.parse(response)["status"];
        if (status === "Signup successful") { location.reload(); }
        else { message(status, true, "signup-box"); }
      }
    });
  });

  $(document).on("click", "#save", function() {
    $.post({
      type: "POST",
      url: "/settings",
      data: {"username": $("#settings-user").val(), 
             "password": $("#settings-pass").val(), 
             "email": $("#settings-mail").val()},
      success(response){
        message(JSON.parse(response)["status"]);
      }
    });
  });
document.addEventListener('DOMContentLoaded', () => {
  (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
    const $notification = $delete.parentNode;

    $delete.addEventListener('click', () => {
      $notification.parentNode.removeChild($notification);
    });
  });
});



});

// Open or Close mobile & tablet menu
// https://github.com/jgthms/bulma/issues/856
$("#navbar-burger-id").click(function () {
  if($("#navbar-burger-id").hasClass("is-active")){
    $("#navbar-burger-id").removeClass("is-active");
    $("#navbar-menu-id").removeClass("is-active");
  }else {
    $("#navbar-burger-id").addClass("is-active");
    $("#navbar-menu-id").addClass("is-active");
  }
});

$(document).ready(function () {
  var xhr
  $("form").submit(function (event) {
    $('#query-btn').hide()
    $('#loading').show()
    var form_data = $('form').serialize();
    xhr =  $.ajax({
        url: '/query',
        method: 'POST',
        data: form_data,
        success: function (response) {
          stats = 'notification is-' + response[0]
          $('#query-btn').show()
          $('#loading').hide()
          $('#skv-output-status').show()
          $('#skv-output-otext').show()
          $('#skv-output-status').addClass(stats);
          $('#skv-output-img').fadeIn().html('<img src="' + response[2] + '"/>');
          $('#skv-output-status').fadeIn().html('<strong >' + response[0] + '! </strong> ' + response[1]);
          var brief = response[3];
          for(var key in brief)
          {
            var value = Object.values(brief[key]);
            document.getElementById("skv-output-otext").innerHTML +='<strong>'+Object.keys(brief[key]) + "</strong> :" + value + '<br>';
          }

          console.log(response[3][0]);
          console.log('completed');
        },
        error: function (error) {
          $('#query-btn').show()
          $('#loading').hide()
          console.log('something went wrong!');
          console.log(error);
        }
      })
    event.preventDefault();
  });


});