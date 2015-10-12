/* clone questions in assessment steps */
function cloneSomeMore(selector, outerType, innerType) {
  var parent = $(selector).parent();
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

    total++;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    $(newElement).find("input[id*='-TOTAL_FORMS']").val(1);
    $(newElement).find("input[id*='-INITIAL_FORMS']").val(0);
    $(newElement).find("input[id*='-MIN_NUM_FORMS']").val(0);
    $(newElement).find("input[id*='-MAX_NUM_FORMS']").val(1000);
    $(selector).after(newElement);
}

$(function (){
  $('#navLogin').click(function(){
    $('div#login').show();
  });

  $('#closeLogin').click(function(){
    $('div#login').hide();
  });
});
