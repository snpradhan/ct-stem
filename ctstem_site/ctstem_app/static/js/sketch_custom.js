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

/*
 * Load existing canvas data
 */
function loadCanvasData(){
  $('canvas.assignment_sketch').each(function(){
    var id = '#'+$(this).attr('id');
    var actions = $(id).next().val();
    if(actions){
      var actions_json = JSON.parse(actions);
      $.each(actions_json, function (i, val) {
        $(id).sketch().actions.push(val);
        $(id).sketch().redraw();
      });
    }
  });
}

/*
 * Set canvas data for save
 */
function setCanvasData(){
  $('canvas.assignment_sketch').each(function(){
    var actions = $(this).sketch().actions;
    $(this).next().val(JSON.stringify(actions));
  });
}
