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
function dtmBuildHtmlTable(parentId, tableId, colInput, rowInput, editFlag) {

  console.log('building table');

  var selector = "#" + parentId + " > #"+tableId;
  var headSelector = selector +" > thead";
  var bodySelector = selector +" > tbody";

  //create the headers
  if (colInput){
    dtmAddAllColumnHeaders( headSelector, colInput, editFlag);
  }
  var rowLen;
  if ( rowInput != null && rowInput != ''){
    rowLen = rowInput.length
  } else{
    rowLen = 3;
  }
  for (var i = 0; i < rowLen; i++) {
    var row$ = $('<tr/>');
    for (var colIndex = 0; colIndex < colInput.length; colIndex++) {
      var cellValue = "";
      if ( rowInput != null && rowInput != ''){
        var cellValue = rowInput[i][colIndex];
      }
      if (cellValue == null ) cellValue = "";
      if (editFlag){
        row$.append($('<td><input type="text" value="'+cellValue+'"/> </td>'));
      }
      else{
        row$.append($('<td>'+cellValue+'</td>'));
      }
    }
    // last action cell
    if (editFlag) {
      var buttons$ = $('<td class="add_delete_buttons" />');
      buttons$.append($('<button type="button" class="btn btn-success" title="Add Row" onclick="dtmInsertRow(\''+ tableId +'\', this)">+</button>'));
      //do not allow the first row to be deleted
      if (i > 0) {
        buttons$.append($('<button type="button" class="btn btn-danger" title="Delete Row" onclick="dtmDeleteRow(\''+ tableId +'\', this)">-</button>'));
      }
      else{
        buttons$.append($('<button type="button" class="btn btn-danger" style="display:none;" title="Delete Row" onclick="dtmDeleteRow(\''+ tableId +'\', this)">-</button>'));
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

function dtmAddAllColumnHeaders(selector, colInput, editFlag) {
  var headerTr$ = $('<tr bgcolor=#ff9966 class="eachRow" />');
  for (var i = 0; i < colInput.length; i++) {
    var key= colInput[i];
    headerTr$.append($('<th class="eachHdr"/>').html(key));
  }
  if (editFlag){
    headerTr$.append($('<th class="eachHdr"/>'));
  }
  $(selector).append(headerTr$);
}
