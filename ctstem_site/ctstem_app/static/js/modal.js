$(function (){

  $('.modal').on('hidden.bs.modal', function(){
    if($(this).find('form').length > 0) {
      $(this).find('form')[0].reset();
    }
    $(this).find('.msg .errorlist .error').html('');
    $(this).find('.results').hide();
    $(this).find('.results tbody').html('');
  });


  $("a.modal-open").click(function(e){
    e.preventDefault();
    var url = $(this).data('href');
    var target = $(this).data('target');
    $(target).load(url, function() {
      $(this).modal('show');
    });
  });
});
