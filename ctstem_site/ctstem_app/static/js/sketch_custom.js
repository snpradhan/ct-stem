$(function(){
  $("canvas.assignment_sketch").each(function(){
    var id = $(this).attr("id");
    $.each(['#000', '#f00', '#ff0', '#0f0', '#0ff', '#00f', '#f0f', '#fff'], function() {
      $('#'+id+'_tools').append("<a href='#"+id+"' class='color button-color' data-color='" + this + "' data-tool='marker' style='width: 30px; background: " + this + ";'></a> ");
    });
    $.each([3, 5, 10, 15], function() {
      $('#'+id+'_tools').append("<a href='#"+id+"' class='size button-size' data-size='" + this + "' data-tool='marker' style='background: #ccc'>" + this + "</a> ");
    });
    $('#'+id+'_tools').append("<a href='#"+id+"' class='eraser button-tool' data-tool='eraser'>Eraser</a> ");
    $('#'+id+'_tools').append("<a href='#"+id+"' class='line button-tool' data-tool='line'>Line</a> ");
    $('#'+id+'_tools').append("<a href='#"+id+"' class='rect button-tool' data-tool='rect'>Rectangle</a> ");
    $('#'+id+'_tools').append("<a href='#"+id+"' class='text button-tool' data-tool='text'>Text</a> ");
    $('#'+id+'').sketch();
  });

  $('a.button-tool').click(function(e) {
    e.preventDefault()
    $('a.button-tool').removeClass('activeTool');
    $(this).addClass('activeTool');
  });

  $('a.button-size').click(function(e) {
    e.preventDefault()
    $('a.button-size').removeClass('activeSize');
    $('a.button-tool').removeClass('activeTool');
    $(this).addClass('activeSize');
  });

  $('a.button-color').click(function(e) {
    e.preventDefault()
    $('a.button-color').removeClass('popout').removeClass('activecolor');
    $('a.button-tool').removeClass('activeTool');
    $(this).addClass('popout').addClass('activecolor');
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

saveTextFromArea = function (y, x, fontsize, canvasId, color){
   //get the value of the textarea then destroy it and the save button
   var text = $('textarea#textareaTest').val();
   $('textarea#textareaTest').remove();
   $('#saveText').remove();
   $('#textAreaPopUp').remove();
   $("#" + canvasId).sketch().addText(color, fontsize, x, y, text);
   $("#" + canvasId).sketch().redraw();
}

textArea =  function (action, canvasId) {
   if ($('#textAreaPopUp').length > 0) {
      $('textarea#textareaTest').remove();
      $('#saveText').remove();
      $('#textAreaPopUp').remove();
   }
   var mouseX =action.events[0].x;
   var mouseY =action.events[0].y;
   var textAreaX = window.event.pageX;
   var textAreaY = window.event.pageY;

   var color = action.color;
   var fontsize = action.size * 2;
   //append a text area box to the canvas where the user clicked to enter in a comment
   var textArea = "<div id='textAreaPopUp' style='position:absolute;top:"+textAreaY+"px;left:"+textAreaX+"px;z-index:30;'><textarea id='textareaTest' style='width:200px;height:50px;'></textarea>";
   var saveButton = "<input type='button' value='save' id='saveText' onclick='saveTextFromArea("+mouseY+","+mouseX+","+fontsize+",\""+canvasId+"\",\""+color+"\");'></div>";
   var appendString = textArea + saveButton;
   $("#" + canvasId).parent().append(appendString);
}
