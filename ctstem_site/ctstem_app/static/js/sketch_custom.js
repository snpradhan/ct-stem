$(function(){
  $("canvas.assignment_sketch").each(function(){
    var id = $(this).attr("id");
    $.each(['#000', '#f00', '#ff0', '#0f0', '#0ff', '#00f', '#f0f', '#fff'], function() {
      $('#'+id+'_tools').append("<a href='#"+id+"' class='color' data-color='" + this + "' data-tool='marker' style='width: 30px; background: " + this + ";'></a> ");
    });
    $.each([3, 5, 10, 15], function() {
      $('#'+id+'_tools').append("<a href='#"+id+"' class='size' data-size='" + this + "' data-tool='marker' style='background: #ccc'>" + this + "</a> ");
    });
    $('#'+id+'_tools').append("<a href='#"+id+"' class='eraser' data-tool='eraser'>Eraser</a> ");
    $('#'+id+'_tools').append("<a href='#"+id+"' class='line' data-tool='line'>Line</a> ");
    $('#'+id+'_tools').append("<a href='#"+id+"' class='rect' data-tool='rect'>Rectangle</a> ");
    $('#'+id+'').sketch();
  });
});
