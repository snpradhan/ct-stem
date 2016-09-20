$(function(){
  $("canvas.assignment_sketch").each(function(){
    var id = $(this).attr("id");
    $.each(['#f00', '#ff0', '#0f0', '#0ff', '#00f', '#f0f', '#000', '#fff'], function() {
      $('#'+id+'_tools').append("<a href='#"+id+"' data-color='" + this + "' data-tool='marker' style='width: 30px; background: " + this + ";'></a> ");
    });
    $.each([3, 5, 10, 15], function() {
      $('#'+id+'_tools').append("<a href='#"+id+"' data-size='" + this + "' data-tool='marker' style='background: #ccc'>" + this + "</a> ");
    });
    $('#'+id+'_tools').append("<a href='#"+id+"' data-tool='eraser'>Eraser</a> ");

    $('#'+id+'').sketch();
  });
});
