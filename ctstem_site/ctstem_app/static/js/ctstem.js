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

    newElement.find('span[role="application"]').each(function(){
      $(this).remove();
    });
    newElement.find('script').each(function(){
      $(this).remove();
    });

    /*var newHTML = newElement[0].outerHTML;
    var regex = new RegExp('id_'+type+'-'+(total-1), 'g');
    newHTML = newHTML.replace(regex, 'id_'+type+'-'+(total));
    newElement = $.parseHTML(newHTML);*/

    total++;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    $(newElement).find("input[id*='-TOTAL_FORMS']").val(1);
    $(newElement).find("input[id*='-INITIAL_FORMS']").val(0);
    $(newElement).find("input[id*='-MIN_NUM_FORMS']").val(0);
    $(newElement).find("input[id*='-MAX_NUM_FORMS']").val(1000);
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
    $.ajax({
      type: 'GET',
      url: url,
      dataType: 'json',
      success: function(data){
        $("#id_user_code").val(data['user_code']);
      },
      error: function(){
        alert("Please try generating the user code again.")
      }

    });
  });


  //datatables configuration
  $('table.table.dt tfoot th').each( function () {
        var title = $(this).text();
        $(this).html( '<input type="text" placeholder="Search '+title+'" />' );
    } );

  var table = $('table.table.dt').DataTable();

  // Apply the search
  table.columns().every( function () {
    var that = this;

    $( 'input', this.footer() ).on( 'keyup change', function () {
      if ( that.search() !== this.value ) {
        that
          .search( this.value )
          .draw();
      }
    });
  });

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

});
