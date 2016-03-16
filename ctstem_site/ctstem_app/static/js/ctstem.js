/* clone questions in assessment steps */
function cloneSomeMore(selector, outerType, innerType) {
  var parent = $(selector).closest('.form-group');
  var newElement = $(selector).clone(true);
  var total_forms = $(parent).find("input[id*='-TOTAL_FORMS']");
  var total = total_forms.val();
  if(total == ''){
    total = 1;
  }
  var pattern = new RegExp(innerType+'-[0-9]+-');

  newElement.find(':input').each(function() {
    if ($(this).attr('type') !== 'button' &&
      $(this).attr('name').indexOf(outerType) !== -1 &&
      $(this).attr('name').indexOf(innerType) !== -1){
      var name = $(this).attr('name').replace(pattern, innerType + '-' + total + '-');
      var id = 'id_' + name;

      if ($(this).attr('type') !== 'hidden') {
          $(this).val('');
      }
      $(this).attr('name', name);
      $(this).attr('id', id);
      //$(this).attr({'name': name, 'id': id}).removeAttr('checked').removeAttr('readonly');
    }
  });
  total++;
  total_forms.val(total);
  $(selector).after(newElement);
}

/* this function clones an assessment step */
function cloneMore(selector, type) {
    var newElement = $(selector).clone(true);
    var total = $('#id_' + type + '-TOTAL_FORMS').val();
    newElement.find(':input').each(function() {
      var name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
      var id = "id_" + name;
      $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
      if($(this).attr('data-id') !== undefined){
        var data_id = $(this).attr('data-id').replace('-' + (total-1) + '-','-' + total + '-');
        $(this).attr({'data-id': data_id});
      }
      //$(this).val('').removeAttr('checked');
    });
    newElement.find('a').each(function() {
      $(this).attr('href', $(this).attr('href').replace('-' + (total-1) + '-','-' + total + '-'));
        //$(this).val('').removeAttr('checked');
    });
    newElement.find('label').each(function() {
      var newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
      $(this).attr('for', newFor);
    });
    newElement.find('input[id^=id_'+type+'][id$=id]').each(function(){
        $(this).removeAttr('value');
    });
    newElement.find('div').each(function(){
      if($(this).attr('data-field-id') !== undefined){
        var data_field_id = $(this).attr('data-field-id').replace('-' + (total-1) + '-','-' + total + '-');
        $(this).attr({'data-field-id': data_field_id});
      }
      $(this).find("div[id*='cke']").each(function(){
        $(this).remove();
      })
    });

    total++;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    $(newElement).find("input[id*='-TOTAL_FORMS']").val(1);
    $(newElement).find("input[id*='-INITIAL_FORMS']").val(0);
    $(newElement).find("input[id*='-MIN_NUM_FORMS']").val(0);
    $(newElement).find("input[id*='-MAX_NUM_FORMS']").val(1000);

    $(newElement).find('div.question_table table.question tbody tr:not(:last)').remove();
    $(newElement).find('div.question_table table.question tbody input').each(function(){
      var name = $(this).attr('name').replace(/-[0-9]+-id/, '-0-id');
      name = name.replace(/-[0-9]+-question/, '-0-question');
      name = name.replace(/-[0-9]+-ORDER/, '-0-ORDER');
      name = name.replace(/-[0-9]+-DELETE/, '-0-DELETE');
      var id = "id_" + name;
      $(this).attr({'name': name, 'id': id});
    });
    $(selector).after(newElement);
}

$(function (){
  //login modal
  $('#navLogin').click(function(){
    $('div#login').show();
  });

  $('#closeLogin').click(function(){
    $('div#login').hide();
  });

  $('#login').on('show.bs.modal', function () {
    $(".modal-content #loginMsg").html('');
    $(".modal-content #username").val('');
    $(".modal-content #password").val('');
  });

  //user code generation
  $("#generate_code").click(function(){
    var url = "/generate_code";
    var obj = $(this);
    $.ajax({
      type: 'GET',
      url: url,
      dataType: 'json',
      success: function(data){
        $(obj).closest('.input-group').find("input[id^='id'][id$='code']").val(data['code']);
      },
      error: function(){
        alert("Please try generating the user code again.")
      }

    });
  });


  //datatables configuration
  $('table.table.dt thead tr#filterrow th').each( function () {
        var title = $(this).text();
        $(this).html( '<input type="text" placeholder="Search '+title+'" />' );
    } );

  var table = $('table.table.dt').DataTable({
    orderCellsTop: true
  });

  // Apply the filter
  $("table.table.dt thead input").on( 'keyup change', function () {
      table
          .column( $(this).parent().index()+':visible' )
          .search( this.value )
          .draw();
  } );

  //csv upload
  $("#formUpload").submit(function(e) {
    e.preventDefault();
    //var data = $(this).serialize();
    var data = new FormData($('form').get(0));
    var url = "/upload/users";
    $.ajax({
      type: "POST",
      url: url,
      data: data,
      dataType: 'json',
      enctype: 'multipart/form-data',
      cache: false,
      processData: false,
      contentType: false,
      success: function(data){
        if(data['result'] == 'Success'){
          window.location.reload();
        }
        else{
          $('#uploadMsg').html(data['message']);
        }
      },
      error: function(xhr, ajaxOptions, thrownError){
        $('#uploadMsg').html("Something went wrong.  Try again later!");
      },
    });
  });

  $(".expand_collapse").click(function(){
    $(this).closest('.table').children('.collapsible_content').toggle();
    $(this).children().each(function(){
      $(this).toggle();
    })
  });
  $(".expand_collapse_other").click(function(){
    $(this).next().toggle();
    $(this).children().each(function(){
      $(this).toggle();
    })
  });

  $(".ec").click(function(){
    $(this).closest('li').next('ul').toggle();
    $(this).children().each(function(){
      $(this).toggle();
    });
  });

  //add form-control class to ORDER fields
  $('input[id$=ORDER]').addClass('form-control');

  $('ul.messages').delay(10000).fadeOut('slow');

});

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
