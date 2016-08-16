function check_session(){
  var url = "/check_session/";
  $.ajax({
    type: "GET",
    url: url,
    async: true,
    success: function(data){
      if(data.session_expired){
        //set a counter on the dialog and show
        var sec = 30;
        $("div#session_expiry span.time").text(sec);
        $('div#session_expiry').modal({
                                backdrop: 'static',
                                keyboard: false
                              });
        $('div#session_expiry').modal('show');
        //logout in 30 seconds if the user does not respond
        var timeout = setTimeout(function(){
          $('div#session_expiry').modal('hide');
          window.location.href = "/logout";
        }, sec*1000);
        //update the counter every second
        var updated_sec = sec
        var timer = setInterval(function(){
          $("div#session_expiry span.time").text(--updated_sec);
          if (updated_sec == 0) {
            $("div#session_expiry span.time").text(sec);
            clearInterval(timer);
          }
        }, 1000);

        $('#formSession').submit(function(e){
          $(this).ajaxSubmit();
          clearTimeout(timeout);
          $('div#session_expiry').modal('hide');
          return false;
        });
      }
    },
    error: function(e){
      //alert('error', e);
    },
  });
}
