function send_password_reset_email(username, csrf_token){
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
      $("ul.messages").html('<li class="success">Password reset email sent to user</li>');
      $('ul.messages').show();
      $('ul.messages').delay(30000).fadeOut('slow');
    },
  });
  return false;
}

function reset_password(user_full_name, user_id, csrf_token){
  var r = confirm("Are you sure you want to reset "+user_full_name+"'s password?");
  if (r == true) {
    data = {}
    data['csrfmiddlewaretoken'] = csrf_token;
    var data = $.param(data);
    $.ajax({
      type: "POST",
      url: '/user/reset_password/'+user_id+'/',
      data: data,
      success: function(data){
        console.log(data);
        if(data['result'] == 'Success'){
          $('div.modal#reset_password #id_name').html(data['full_name']);
          $('div.modal#reset_password #id_username').html(data['username']);
          $('div.modal#reset_password #id_password').html(data['password']);
          $('div.modal#reset_password').modal('show');
        }
        else{
          $("ul.messages li").remove();
          $("ul.messages").html('<li class="error">'+data['message']+'</li>');
          $('ul.messages').show();
          $('ul.messages').delay(30000).fadeOut('slow');
        }

      },
      error: function(xhr, ajaxOptions, thrownError){
        $("ul.messages li").remove();
        $("ul.messages").html('<li class="error">User password could not be reset</li>');
        $('ul.messages').show();
        $('ul.messages').delay(30000).fadeOut('slow');
      },
    });
  }
  return false;
}

$(function (){

  //user code generation
  $("#generate_code").click(function(){
    var url = "/generate_code/";
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

  //paginate sort table
  $('table.table.paginate_sort thead  th:not(.no-sort)').each( function () {
    var id = $(this).attr('id');
    var td_class = $(this).attr('class');
    var href = "?order_by=1&direction=2&ignorecase=3";
    var fa_class = '';
    sort_html = '';
    if(id) {
      id = id.trim()
      href = href.replace('1', id);
      if(order_by == id){
        if(direction == 'asc') {
          href = href.replace('2', 'desc');
          fa_class = 'fa fa-sort-asc';
        }
        else {
          href = href.replace('2', 'asc');
          fa_class = 'fa fa-sort-desc';
        }
      }
      else {
        href = href.replace('2', 'asc');
        fa_class = 'fa fa-sort'
      }
      if(td_class == 'ignorecase') {
        href = href.replace('3', 'true');
      }
      else{
        href = href.replace('3', 'false');
      }
      sort_html = '<a class="'+fa_class+'" href="'+href+'"></a>'
      $(this).append(sort_html);
    }
  });

  $('#select-all').click(function(event) {
    var $that = $(this);
    // Iterate each checkbox
    $('.action-select:checkbox').each(function() {
        this.checked = $that.is(':checked');
    });
  });

  //user upload modal submit
  $("#formUpload").submit(function(e) {
    e.preventDefault();
    //var data = $(this).serialize();
    //var data = new FormData($('form#formUpload').get(0));
    var emails = $('#formUpload textarea#id_emails').val();
    var file = $('#formUpload input#id_uploadFile').val();
    if(emails == '' && file == ''){
      $('#uploadMsg .errorlist .error').html("Please select a class and either a list of student emails or a student email csv to upload.")
    }
    else {

      //create options for ajax call
      var options = {
        type: "POST",
        url: "/upload/users/",
        beforeSend: function(){
          $('#formUpload #spinner').show();
        },
        complete: function(){
          $('#formUpload #spinner').hide();
        },
        success: function(data){
          if(data['success'] == true){
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
              $("#upload").modal('toggle');
              window.location.reload();
            }
          }
          else{
            $('#uploadMsg .errorlist .error').html(data['message']);
          }
        },
        error: function(xhr, ajaxOptions, thrownError){
          $('#uploadMsg .errorlist .error').html("Something went wrong.  Try again later!");
        },
      };

      if(file == '') {
        options['data'] = $(this).serialize();
      }
      else{
        options['data'] = new FormData($('form#formUpload').get(0));
        options['enctype'] = 'multipart/form-data';
        options['cache'] = false;
        options['processData'] = false;
        options['contentType'] = false;
      }

      $.ajax(options);
    }
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

  /* handler for search and assign curriculum modal trigger */
  $('a.assignment-modal').click(function(){
    $("div.modal#assignment select#id_group_class option:selected").prop('selected', false);
    $("div.modal#assignment select#id_group_class option[value='"+$(this).data('id')+"']").prop('selected', true);
    var title = 'to Class';
    if($(this).data('title') !== undefined){
      title = 'to '+$(this).data('title');
    }
    $("div.modal#assignment .modal-title span").html(title);

    if($(this).data('id') != null){
      $("div.modal#assignment select#id_group_class").closest('.form-group').hide();
      if($(this).data('subject') != null) {
        $("div.modal#assignment select#id_subject option:selected").prop('selected', false);
        $("div.modal#assignment select#id_subject option[value='"+$(this).data('subject')+"']").prop('selected', true);
        $("div.modal#assignment form").submit();
      }
    }
    else{
      $("div.modal#assignment select#id_group_class").closest('.form-group').show();
    }
  });

  /* handler for user upload modal trigger */
  $('a.upload-modal').click(function(){
    $("div.modal#upload select#id_group option:selected").prop('selected', false);
    $("div.modal#upload select#id_group option[value='"+$(this).data('id')+"']").prop('selected', true);

    var title = 'Class';
    if($(this).data('title') !== undefined){
      title = '<div>'+$(this).data('title')+'</div>';
    }
    $("div.modal#upload .modal-title span").html(title);

    if($(this).data('id') != null){
      $("div.modal#upload select#id_group").closest('.form-group').hide();
    }
    else{
      $("div.modal#upload select#id_group").closest('.form-group').show();
    }
  });

  $("button.search_users").click(function(e){
    e.preventDefault();
    var url = $(this).data("form");
    var modal = $(this).data("target");
    var group_id = $(this).data("id");
    $(modal).load(url, function() {
      $(this).find('input[name="group_id"]').val(group_id);
      $(this).modal('show');
    });
    return false;
  });

  //bind remove function
  $("button.remove").click(function(e){
    var id = $(this).closest('tr').attr('id');
    var form_group = $(this).closest('.form-group');
    $(form_group).find('select[id^="id"] option[value="'+id+'"]').prop('selected', false);
    //$('select[id^="id"][id$="shared_with"] option[value="'+id+'"]').prop('selected', false);
    var table = $(form_group).find('table.inner_table');
    $(table).find('tbody tr#'+id).remove();
    rowAddorRemove($(table));
  });

  //hide table header if no rows
  $('table.inner_table').each(function(){
    if(!$(this).parent().hasClass('results') && !$(this).parent().hasClass('dt_input')) {
      rowAddorRemove($(this));
    }
  });

  if($('div.button-group-fixed').length > 0) {
    var fix_button_top = $('div.button-group-fixed').offset().top;

    $(window).scroll(function() {
      var currentScroll = $(window).scrollTop() + 100;
      if (currentScroll >= fix_button_top) {
        // apply position: fixed if you
        $('div.button-group-fixed').css({
          position: 'fixed',
          top: '6em',
          right: '6.75em',
        });
      } else {
        $('div.button-group-fixed').css({
          position: 'static'
        });
      }
    });
  }

  $('a.emoji-modal').click(function(){
    $("div.modal#emojis input#emoji_feedback_area").val($(this).data('id'));
  });

  $('div.emoji span').click(function(){
    var id = $('input#emoji_feedback_area').val();
    var val = $('textarea#'+id).val();
    $('textarea#'+id).val(val + $(this).html());
  });

  $('input#clear[type="submit"]').click(function(e){
    e.preventDefault();
    $('form')[0].reset();
    $('form').submit();
  });

});

function rowAddorRemove(tbl){
  if($(tbl).find('tbody > tr:visible').length == 0){
    $(tbl).find('thead').css('display', 'none');
  }
  else{
    $(tbl).find('thead').css('display', 'table-header-group');
  }
}

function bind_user_removal(){
  $('a.removeUser').unbind('click');
  $('a.removeUser').click(function(e){
    e.preventDefault();
    var remove = confirm('Are you sure you want to remove the student from the group?');
    var tr = $(this).closest('tr');
    var table = $(this).closest('table');
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
            rowAddorRemove(table);
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

  rowAddorRemove($('table.table#members'));

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
