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
/*
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
*/
//<!-- -------------------------- author : @avialxee --------------------------- -->
            
                $(document).ready(function () {

                    $(function () {
                        $('[data-toggle="popover"]').popover()
                    });
                    
                    $(function (){
                        signal_check()
                    });
                    var activc = '';
                    var xhr

                    $("form").submit(function (event) {
                        //ajaxd();

                        $('#query-btn').hide()
                        $('#loading').show()

                        document.getElementById("skv-output-otext").innerHTML = "";
                        document.getElementById("skv-output-status").innerHTML = "";
                        document.getElementById("skv-output-img").innerHTML = "";

                        $('#skv-output-status').removeClass(activc);
                        $('#skv-output-otext').removeClass('alert alert-info');


                        document.getElementById("connection-status").innerHTML =
                            "Please wait!<br> Loading....";
                        $('#connection-status').removeClass('badge badge-success');

                        var statusloc = "";
                        var form_data = $('form').serialize();
                        signal_check().done(query(form_data, statusloc));
                        event.preventDefault();
                    });

                    
                    var query = function (form_data, statusloc) {
                        $.ajax({
                            url: $URL + '/api',
                            //async: false,
                            method: 'POST',
                            data: form_data,
                            success: function query(response) {
                                //console.log(response);
                                if (response['Location']) {
                                    statusloc = response['Location'];
                                    document.getElementById("connection-status").innerHTML =
                                        "Working...";
                                    $('#connection-status').removeClass('badge badge-success');
                                } else {
                                    //console.log('no status information');
                                    document.getElementById("connection-status").innerHTML = "";

                                }
                                url = $URL + String(statusloc);

                                xhr2 = $.ajax({

                                    url: url,
                                    method: 'GET',
                                    statusCode: {
                                        202: function (response) {
                                            //if (response['Location']){
                                            //statusloc=response['Location'];}
                                            console.log('req')
                                            setTimeout( function(){
                                              query('response');
                                            }, 5000
                                              );

                                        },
                                        200: function (response) {
                                            if (response['info'] == 'info' ||
                                                response['info'] == 'success' ||
                                                response['info'] == 'warning') {
                                                stats = 'alert alert-' + response[
                                                    'info'];
                                                activc = stats;
                                                $('#query-btn').show()
                                                $('#loading').hide()

                                                $('#skv-output-status').show()
                                                $('#skv-output-otext').show()
                                                $('#skv-output-status').addClass(
                                                    stats);
                                                if (response['info'] == 'success') {
                                                    $('#skv-output-otext').addClass(
                                                        'alert alert-info');
                                                }
                                                document.getElementById(
                                                        "connection-status")
                                                    .innerHTML = "";
                                                $('#skv-output-status').fadeIn()
                                                    .html('<strong >' + response[
                                                            'info'] +
                                                        '! </strong> ' + response[
                                                            'message']);
                                                for (var uri in response['url']){
                                                  //var ur_val = Object.values(response['url'][uri]);
                                                  
                                                  document.getElementById('skv-output-img').innerHTML +=                                                  
                                                    '<img class="img-fluid" src="' +
                                                    Object.values(response['url'][uri]) + '"/>';
                                                    
                                                }
                                                
                                                var brief = response['brieftext'];
                                                //document.getElementById(
                                                //            "skv-output-otext")
                                                //        .innerHTML += '<strong>Contour Values</strong>:<br>';
                                                for (var key in brief) {
                                                    var value = Object.values(brief[
                                                        key]);
                                                    document.getElementById(
                                                            "skv-output-otext")
                                                        .innerHTML += '<strong>' +
                                                        Object.keys(brief[key]) +
                                                        "</strong> :" + value +
                                                        ' <br>';
                                                    
                                                }
                                                    
                                                ////console.log(response['info']);
                                                ////console.log('completed');
                                            } else if (response['info'] ==
                                                'processing') {
                                                //statusloc=response['Location'];
                                                query('processing');
                                            } else {
                                                //statusloc=response['Location'];
                                                query('response')
                                                //console.log("..failed..finding..any..info");
                                            }
                                        },
                                        404: function (response) {
                                            $('#query-btn').show()
                                            $('#loading').hide()
                                        },
                                        401: function (response) {
                                            $('#query-btn').show()
                                            $('#loading').hide()
                                        },
                                        500: function (response) {
                                            $('#query-btn').show()
                                            $('#loading').hide()
                                        }
                                    }
                                })

                            }
                        })
                    };





                    var signal_check = function () {

                        document.getElementById("connection-status").innerHTML =
                            "Please wait!<br> Loading....";
                        $('#connection-status').removeClass('badge badge-success');

                        return $.ajax({
                            type: "GET",
                            url: $URL + "/static/media/logo.png",
                            //async: false,
                            success: function () {
                                $('#connection-status').removeClass('badge badge-warning');
                                document.getElementById("connection-status").innerHTML =
                                    "Connected";
                                $('#connection-status').addClass('badge badge-success');

                                ////console.log("");

                            },
                            error: function () {
                                document.getElementById("connection-status").innerHTML =
                                    "Something Wrong! Please try back later";
                                $('#connection-status').addClass('badge badge-warning');
                            }
                        });
                    };

                });