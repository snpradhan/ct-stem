function reset_password(username, csrf_token){
  data = {}
  data['csrfmiddlewaretoken'] = csrf_token;
  data['username_or_email'] = username;
  var data = $.param(data);
  $.ajax({
    type: "POST",
    url: '/password_reset/recover/',
    data: data,
    success: function(data){
      $("ul.messages li").remove();
      $("ul.messages").html('<li class="success">Password reset email sent to user</li>');
      $('ul.messages').show();
      $('ul.messages').delay(30000).fadeOut('slow');
    },
    error: function(xhr, ajaxOptions, thrownError){
      $("ul.messages li").remove();
      $("ul.messages").html('<li class="error">Password reset email could not be sent to user</li>');
      $('ul.messages').show();
      $('ul.messages').delay(30000).fadeOut('slow');
    },
  });
  return false;
}

$(function (){
  //login modal
  $('#navLogin').click(function(){
    $('div#login').show();
  });

  $('#closeLogin').click(function(){
    $('div#login').hide();
  });

  $('.modal').on('hidden.bs.modal', function(){
    $(this).find('form')[0].reset();
    $(this).find('.msg').html('');
    $(this).find('.results').hide();
    $(this).find('.results tbody').html('');
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
  $('table.table.dt thead tr#filterrow th:not(.no-sort)').each( function () {
        var title = $(this).text();
        $(this).html( '<input type="text" placeholder="Search '+title+'" />' );
    } );

  var table = $('table.table.dt').DataTable({
    order: [],
    orderCellsTop: true,
    lengthMenu: [[100, -1], [100, "All"]],
    columnDefs: [
      { targets: 'no-sort', orderable: false }
    ]
  });

  // Apply the filter
  $("table.table.dt thead tr#filterrow input").on( 'keyup change', function () {
      table
          .column( $(this).parent().index()+':visible' )
          .search( this.value )
          .draw();
  });

  $('#select-all').click(function(event) {
    var $that = $(this);
    // Iterate each checkbox
    $('.action-select:checkbox').each(function() {
        this.checked = $that.is(':checked');
    });
  });

  //csv upload
  $("#formUpload").submit(function(e) {
    e.preventDefault();
    //var data = $(this).serialize();
    var data = new FormData($('form#formUpload').get(0));
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
      beforeSend: function(){
        $('#formUpload #spinner').show();
      },
      complete: function(){
        $('#formUpload #spinner').hide();
      },
      success: function(data){
        if(data['result'] == 'Success'){
          if(window.location.href.indexOf('/group/') != -1){

            for(var student in  data['new_students']){
              if($('tr#'+student).length == 0){
                var group = data['new_students'][student]['group'];
                var user_id = data['new_students'][student]['user_id'];
                var membership_id = data['new_students'][student]['membership_id']
                //add student detail to the table
                $('table.table#members tbody').append('<tr id='+student+'>\
                  <td><input id="student_'+student+'" type="checkbox" class="action-select" value="'+student+'" name="student_'+student+'">\
                  <td>'+data['new_students'][student]['username']+'\
                    <div class="controls">\
                      <a type="button" class="btn btn-success edit" aria-label="Edit User" title="Edit User" href="/user/'+user_id+'">\
                        <span class="glyphicon glyphicon-pencil" aria-hidden="true"></span>\
                      </a>\
                      <a type="button" class="btn btn-warning removeUser" aria-label="Remove Student" title="Remove Student" href="/student/remove/'+group+'/'+student+'" data-id="'+student+'">\
                        <span class="glyphicon glyphicon-trash" aria-hidden="true"></span>\
                      </a>\
                    </div>\
                  </td>\
                  <td>'+data['new_students'][student]['full_name']+'</td>\
                  <td>'+data['new_students'][student]['email']+'</td>\
                  <td>'+data['new_students'][student]['status']+'</td>\
                  <td>'+data['new_students'][student]['student_consent']+'</td>\
                  <td>'+data['new_students'][student]['parental_consent']+'</td>\
                  <td>'+data['new_students'][student]['member_since']+'</td>\
                  <td>'+data['new_students'][student]['last_login']+'</td></tr>');

                //add student membership hidden input
                $('table.table#members').before('<input id="id_group-members_'+student+'" name="group-members" type="hidden" value="'+student+'">');

              }
            }
            $("#upload").modal('toggle');
            bind_user_removal();
            display_messages(data['messages'])
          }
          else {
            //location is users or groups page
            window.location.reload();
          }
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


  bind_user_removal();


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
    //expand/collapse the standards ul
    $(this).closest('li').next('ul').toggle();
    $(this).children().each(function(){
      $(this).toggle();
    });

    //expand/collapse the unit lessons
    $(this).closest('.row').next('.row').toggle();

  });
  //add form-control class to ORDER fields
  $('input[id$=ORDER]').addClass('form-control');

  $('ul.messages').delay(30000).fadeOut('slow');

  $("a.preview").click(function(e){
    e.preventDefault();
    var url = $(this).data("form");
    $(".modal#curriculum").load(url, function() {
      $(this).modal('show');
    });
    return false;
  });
  $("a.profile").click(function(e){
    e.preventDefault();
    var url = $(this).data("form");
    $(".modal#profile").load(url, function() {
      $(this).modal('show');
    });
    return false;
  });

  $('body').on("click", "a.assign", function(e){
    e.preventDefault();
    var url = $(this).data("form");
    $("#assignmentModal").load(url, function() {
      $(this).modal('show');
    });
    return false;
  });
  //disable a field if it is inside a div with class disabled
  $('div#userProfile div.disabled select').prop('disabled', true);

  //on click of students tab load the spinner
  $('li a.students').on('click', function() {
    $('div#spinner').show();
  });

  $('.content').on("click", 'a.util-button.fa-files-o', function(e) {
    $('div#spinner').show();
  });

  $('form#curriculumForm input#submit').on('click', function() {
    $('div#spinner').show();
  });

  $('form#curriculumForm input#preview').on('click', function() {
    $('div#spinner').show();
  });
});



function bind_user_removal(){
  $('a.removeUser').unbind('click');
  $('a.removeUser').click(function(e){
    e.preventDefault();
    var remove = confirm('Are you sure you want to remove the student from the group?');
    var tr = $(this).closest('tr');
    var hd_input = $('input:hidden#id_group-members_'+$(this).data('id'));
    if(remove){
      var url = $(this).attr('href');
      data = {}
      data['csrfmiddlewaretoken'] = $('#userGroupForm').find('input:hidden').eq(0).val();
      var data = $.param(data);
      $.ajax({
        type: "POST",
        url: url,
        data: data,
        dataType: 'json',
        success: function(data){
          if(data['result'] == 'Success'){
            $(tr).remove();
            $(hd_input).remove();
          }
          else{
            $("ul.messages li").remove();
            $("ul.messages").html('<li class="error">User could not be removed from the group</li>');
            $('ul.messages').show();
            $('ul.messages').delay(30000).fadeOut('slow');
          }
        },
        error: function(xhr, ajaxOptions, thrownError){
          $("ul.messages li").remove();
          $("ul.messages").html('<li class="error">User could not be removed from the group</li>');
          $('ul.messages').show();
          $('ul.messages').delay(30000).fadeOut('slow');
        },
      });
    }
  });
}

function display_messages(messages){
  $("ul.messages li").remove();
  var html = '';
  for(var index in messages['error']){
    html = html + '<li class="error">'+messages['error'][index]+'</li>';
  }
  for(var index in messages['success']){
    html = html + '<li class="success">'+messages['success'][index]+'</li>';
  }
  $("ul.messages").html(html);
  $('ul.messages').show();
  $('ul.messages').delay(30000).fadeOut('slow');
}


function add_student_to_data_table(value, csrf){
  //add student detail to the table
  $('table.table#members tbody').append('<tr id='+value['student_id']+'>\
    <td width="3%"><input id="student_'+value['student_id']+'" type="checkbox" class="action-select" value="'+value['student_id']+'" name="student_'+value['student_id']+'" /></td>\
    <td>'+value['username']+'\
      <div class="controls">\
        <a type="button" class="btn btn-success edit" aria-label="Edit User" title="Edit User" href="/user/'+value['user_id']+'">\
          <span class="glyphicon glyphicon-pencil" aria-hidden="true"></span>\
        </a>\
        <a type="button" class="btn btn-warning removeUser" aria-label="Remove Student" title="Remove Student" href="/student/remove/'+value['group']+'/'+value['student_id']+'" data-id="'+value['student_id']+'">\
          <span class="glyphicon glyphicon-trash" aria-hidden="true"></span>\
        </a>\
        <button type="button" class="btn btn-info reset" aria-label="Reset User Password" title="Reset User Password" onclick="return reset_password(&apos;'+value['username']+'&apos;,&apos;'+csrf+'&apos;)">\
          <span class="glyphicon glyphicon-refresh" aria-hidden="true"></span>\
        </button>\
      </div>\
    </td>\
    <td>'+value['name']+'</td>\
    <td>'+value['email']+'</td>\
    <td>'+value['status']+'</td>\
    <td>'+value['student_consent']+'</td>\
    <td>'+value['parental_consent']+'</td>\
    <td>'+value['member_since']+'</td>\
    <td>'+value['last_login']+'</td></tr>');

  //add student membership hidden input
  $('table.table#members').before('<input id="id_group-members_'+value['student_id']+'" name="group-members" type="hidden" value="'+value['student_id']+'">');
}

function update_subaction( action, csrftoken ) {

  var action_id = 0;
  if ('parental_consent_selected' == action) {
    action_id = 1;
  }
  else if ('school_selected' == action) {
    action_id = 2;
  }

  if (action_id == 1) {
    $("select#subaction").empty();
    $("select#subaction").append('<option value="A">Agree</option');
    $("select#subaction").append('<option value="D">Disagree</option');
    $("select#subaction").show();
  }
  else if (action_id == 2) {
    var data = {csrfmiddlewaretoken: csrftoken};
    $.ajax({
        url: "/subaction/"+action_id+"/",
        type: "POST",
        data: data,
        success: function(data) {
            console.log(data);
            $("select#subaction").empty();
            $("#subaction").append($.parseJSON(data)
                .map(function(x){return "<option value=\""+x.id+"\">"+x.name+"</option>";})
                .reduce(function(a,b) { return a + b; } ));

            $("#subaction").show();


        },
        error: function(xhr, status, error) {
            alert("Error updating");
            if ( !$("#subaction").attr("disabled") ) { $("#subaction").attr("disabled", true); } },
        complete: function() { }
    });
  }
  else {
    if ( ! $("select#subaction").is(":disabled") ) {
      $("#subaction").hide();
      $("select#subaction").empty();
      $("select#subaction").append("<option value=\"\">---------</option>");
      $("input#duedate").hide();
    }
  }
}

function confirmAction(){
  var actionElement = window.document.getElementById("action");
  var action = actionElement.options[actionElement.selectedIndex].value;
  if(action == "delete_selected"){
    var sure = confirm("Do you want to mass delete selected users?");
    if(sure == true){
        return true;
    }
    else{
        return false;
    }
  }
  else if(action == ""){
    return false;
  }
  return true;
}
