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
      if($(this).attr('href')){
        $(this).attr('href', $(this).attr('href').replace('-' + (total-1) + '-','-' + total + '-'));
      }
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
          if(window.location.href.indexOf('/groups/') != -1){
            window.location.reload();
          }
          else if(window.location.href.indexOf('/group/') != -1){

            for(var student in  data['new_students']){
              if($('tr#'+student).length == 0){
                var group = data['new_students'][student]['group'];
                var user_id = data['new_students'][student]['user_id'];
                var membership_id = data['new_students'][student]['membership_id']
                //add student detail to the table
                $('table.table#members tbody').append('<tr id='+student+'>\
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
                  <td>'+data['new_students'][student]['last_login']+'</td></tr>');

                //add student membership hidden input
                $('table.table#members').before('<input id="id_group-members_'+student+'" name="group-members" type="hidden" value="'+student+'">');

              }
            }
            $("#upload").modal('toggle');
            bind_user_removal();
            display_messages(data['messages'])
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
    $(this).closest('li').next('ul').toggle();
    $(this).children().each(function(){
      $(this).toggle();
    });
  });

  //add form-control class to ORDER fields
  $('input[id$=ORDER]').addClass('form-control');

  $('ul.messages').delay(10000).fadeOut('slow');

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
            $('ul.messages').delay(10000).fadeOut('slow');
          }
        },
        error: function(xhr, ajaxOptions, thrownError){
          $("ul.messages li").remove();
          $("ul.messages").html('<li class="error">User could not be removed from the group</li>');
          $('ul.messages').show();
          $('ul.messages').delay(10000).fadeOut('slow');
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
  $('ul.messages').delay(10000).fadeOut('slow');
}


function add_student_to_data_table(value){
  //add student detail to the table
  $('table.table#members tbody').append('<tr id='+value['student_id']+'>\
    <td>'+value['username']+'\
      <div class="controls">\
        <a type="button" class="btn btn-success edit" aria-label="Edit User" title="Edit User" href="/user/'+value['user_id']+'">\
          <span class="glyphicon glyphicon-pencil" aria-hidden="true"></span>\
        </a>\
        <a type="button" class="btn btn-warning removeUser" aria-label="Remove Student" title="Remove Student" href="/student/remove/'+value['group']+'/'+value['student_id']+'" data-id="'+value['student_id']+'">\
          <span class="glyphicon glyphicon-trash" aria-hidden="true"></span>\
        </a>\
      </div>\
    </td>\
    <td>'+value['name']+'</td>\
    <td>'+value['email']+'</td>\
    <td>'+value['status']+'</td>\
    <td>'+value['last_login']+'</td></tr>');

  //add student membership hidden input
  $('table.table#members').before('<input id="id_group-members_'+value['student_id']+'" name="group-members" type="hidden" value="'+value['student_id']+'">');
}
