/**
  function dtmInsertRow creates new row based on the input parameters:
  tableId - table id
  index - ID from input will add new row to this index
 **/

 function dtmInsertRow(tableId, elmt) {

  // clone first row
  var newRow = $("#"+tableId+ " tbody tr:first").clone(true);

  // clean all cells for new row
  $(newRow).find('input[type=text]').each(function(){
    $(this).val('');
  });

  $(newRow).insertAfter($(elmt).closest('tr'));
  $(newRow).find('button').each(function(){
    $(this).show();
  })

}

/**
  dtmDeleteRow function deletes specified row in provided tableId
  input params
    - tableId - id for the table in which we will delete row
    - i delete row number based on provided ID
**/
function dtmDeleteRow(tableId, elmt) {

  var dr= elmt.parentNode.rowIndex;
  var row = $(elmt.closest('tr'));
  var tbody = $(row).parent();
  var index = $(tbody).children().index($(row));
  if(confirm("Are you sure you want to delete row "+ (index+1) +" in this table?")) {
    $(elmt).closest('tr').remove();
  }
}


/**********************
  This function takes the input data from the given table
  and stores it in a hidden variable as a json string
  This function only needs to return the row data
      var rowInput = [["row0col0", "row0col1", ...], ["row1col0", "row1col1",...], ...]
**********************/

function dtmSaveTable(tableId) {

  var data = [];

  // traverse through row
  $("#"+tableId + " tbody tr").each(function(){
    var rowData = [];
    $(this).find('td:not(.add_delete_buttons)').each(function(){
      rowData.push($(this).children('input').first().val());
    });
    data.push(rowData);
  });
  if(data){
    var json_data = JSON.stringify(data)
    //find the hidden input whose value needs to be set
    var parent = $("#"+tableId).closest('div.dt_input');
    var hdn_input = $(parent).children('input[type=hidden]:first');
    $(hdn_input).val(json_data);
  }
}

/**
  dtmBuildHtmlTable is function that builds the HTML Table out of
  parentId, tableId as a separator
  rowInput contains the row data array as defined above, can be an empty array
**/
function dtmBuildHtmlTable(parentId, tableId, colHeaders, rowHeaders, rowInput, editFlag) {

  console.log('building table');

  var selector = "#" + parentId + " > #"+tableId;
  var headSelector = selector +" > thead";
  var bodySelector = selector +" > tbody";

  console.log(rowInput);
  //create the headers
  if (colHeaders.length > 0){
    dtmAddColumnAllHeaders( headSelector, colHeaders, rowHeaders, editFlag);
  }
  var rowLen;
  if (rowHeaders.length > 0) {
    rowLen = rowHeaders.length
  }
  else if ( rowInput != null && rowInput != ''){
    rowLen = rowInput.length
  } else{
    rowLen = 3;
  }
  for (var i = 0; i < rowLen; i++) {
    var row$ = $('<tr/>');
    if (rowHeaders && rowHeaders[i]) {
      row$.append($('<th>'+rowHeaders[i]+'</th>'));
    }
    for (var colIndex = 0; colIndex < colHeaders.length; colIndex++) {
      var cellValue = "";
      if ( rowInput != null && rowInput != ''){
        if (i in rowInput && colIndex in rowInput[i]){
          cellValue = rowInput[i][colIndex];
        }
      }
      if (cellValue == null ) {
        cellValue = "";
      }
      if (editFlag){
        row$.append($('<td><input type="text" value="'+cellValue+'"/> </td>'));
      }
      else{
        row$.append($('<td>'+cellValue+'</td>'));
      }
    }
    // last action cell
    if (editFlag && rowHeaders.length == 0) {
      var buttons$ = $('<td class="add_delete_buttons" />');
      buttons$.append($('<button type="button" class="btn blue" title="Add Row" onclick="dtmInsertRow(\''+ tableId +'\', this)">+</button>'));
      //do not allow the first row to be deleted
      if (i > 0) {
        buttons$.append($('<button type="button" class="btn red" title="Delete Row" onclick="dtmDeleteRow(\''+ tableId +'\', this)">-</button>'));
      }
      else{
        buttons$.append($('<button type="button" class="btn red" style="display:none;" title="Delete Row" onclick="dtmDeleteRow(\''+ tableId +'\', this)">-</button>'));
      }
      row$.append(buttons$);
    }
    $(bodySelector).append(row$);
  }
}

/**********************
  dtmAddAllColumnHeaders(selector, colInput)
  colInput contains the header array
**********************/

function dtmAddColumnAllHeaders(selector, colHeaders, rowHeaders, editFlag) {
  var headerTr$ = $('<tr bgcolor=#ff9966 class="eachRow" />');
  if(rowHeaders.length > 0){
    headerTr$.append($('<th class="eachHdr"/>'));
  }
  for (var i = 0; i < colHeaders.length; i++) {
    var key= colHeaders[i];
    headerTr$.append($('<th class="eachHdr"/>').html(key));
  }
  if (editFlag && rowHeaders.length == 0){
    headerTr$.append($('<th class="eachHdr"/>'));
  }
  $(selector).append(headerTr$);
}

/*
 * Load existing data in the data table
 */
function loadDataTable(assignmentStatus){
  $('div.dt_input').each(function(){
    var status = assignmentStatus;
    if($(this).hasClass('closed')){
      status = false;
    }
    var divId = $(this).attr('id');
    var tableId = $(this).children('table:first').attr('id');
    //get row data
    var rowInput = $(this).children('input[type=hidden]:first').val();
    if (rowInput) {
      rowInput = JSON.parse(rowInput);
    }
    else {
      rowInput = '';
    }
    var headers = $(this).children('input[type=hidden]:nth-of-type(2)').val().split('\n');
    var colHeaders = [], rowHeaders = [];
    for (var i=0; i< headers.length; i++){
      header = headers[i].split('|');
      if(header.length == 2){
        if(header[0] != ""){
          colHeaders.push(header[0]);
        }
        if(header[1] != ""){
          rowHeaders.push(header[1]);
        }
      }
      else if (header.length == 1){
        if(header[0] != "&nbsp;"){
          colHeaders.push(header[0]);
        }
        else{
          colHeaders.push("");
        }
      }
    }
    dtmBuildHtmlTable(divId, tableId, colHeaders, rowHeaders, rowInput, status);
  });
}

/*
 * Set the data in the data tables for save
 */
function setDataTable(){
  $('div.dt_input').each(function(){
    var tableId = $(this).children('table:first').attr('id');
    dtmSaveTable(tableId);
  });
}

/*
 * Adjust side nav and main content top position based on blue nav bar height
 */
function page_numbers_position(){

  var top_pos = $('header div#page_numbers').offset();
  var height = $('header div#page_numbers').height();
  var nav_bar_pos = top_pos['top'] + height;
  var messages_pos = nav_bar_pos + 5;
  var main_content_pos = nav_bar_pos + 50;

  $('ul.messages').css('top', messages_pos+'px');
  $('header nav#side-nav').css('top', nav_bar_pos+'px');
  $('.page').css('margin-top', main_content_pos+'px');

}
