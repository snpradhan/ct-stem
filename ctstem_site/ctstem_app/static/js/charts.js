function render_pie_chart(element) {
  var id = $(element).attr('id');
  var status_str = $(element).attr('name').replace(/'/g, '"');
  var status = $.parseJSON(status_str);
  var complete = $(element).data('percent-complete');
  $("#"+id).highcharts({
    chart: {
      renderTo: 'container',
      type: 'pie',
      height: 120,
      width: 120,
      backgroundColor: 'rgba(0,0,0,0)',
    },
    title: {
      text: complete+"%",
      align: 'center',
      verticalAlign: 'middle',
      y: 12,
      style: {
        fontWeight: 'bold',
        color: 'black',
        fontSize: '16px'
      },
      filter: {
        property: 'name',
        operator: '===',
        value: 'New'
      },
    },
    tooltip: false,
    plotOptions: {
      pie: {
        dataLabels: {
          enabled: false,

        }
      }
    },
    credits: {
      enabled: false
    },
    series: [{
      name: 'Status',
      innerSize: '80%',
      data: status,
    }]
  });
}

function render_stacked_bar_chart(element) {
  var id = $(element).attr('id');
  var status_str = $(element).attr('name').replace(/'/g, '"');
  var status = $.parseJSON(status_str);
  var total = parseInt($(element).data('total'));
  $("#"+id).highcharts({
    chart: {
      renderTo: 'container',
      height: 80,
      type: 'bar',
      backgroundColor: 'rgba(0,0,0,0)',
    },
    credits: false,
    title: {
      text: ''
    },
    xAxis: {
      visible: false,
      categories: [''],
    },
    yAxis: {
      min: 0,
      max: total,
      endOnTick: false,
      title: {
        text: ''
      },
      reversedStacks: false,
      visible: false,
    },
    legend: false,
    plotOptions: {
      series: {
        stacking: 'normal',
        dataLabels: {
          enabled: false,
          inside: true,
          //format: '{point.y}/'+total,
          formatter: function() {
            return this.y > 0 ? this.y + '/'+total : null;
          }
        }
      }
    },
    series: status,
  });
}
function render_progress_chart(element) {
  var id = $(element).attr('id');
  var student_id = $(element).data('student-id');
  var assignment_id = $(element).data('assignment-id');
  var percent_complete = $(element).data('percent-complete');
  if(student_id && assignment_id) {
    $.ajax({
      type: 'GET',
      url: '/assignment_percent_complete/'+student_id+'/'+assignment_id+'/',
      success: function(data){
        if(data['success'] == true) {
          percent_complete = data['percent_complete'];
          render_progress_chart_with_percent_complete(id, percent_complete);
        }
        return false;
      },
      error: function(xhr, ajaxOptions, thrownError){
        alert(thrownError);
      },
    });
  }
  else {
    render_progress_chart_with_percent_complete(id, percent_complete);
  }
}
function render_progress_chart_with_percent_complete(id, percent_complete) {

  var text_color = 'black';
  if(parseInt(percent_complete) > 15 ){
    text_color = 'white';
  }

  $("#"+id).highcharts({
    chart: {
      renderTo: 'container',
      type: 'bar',
      height: 100,
      backgroundColor: 'rgba(0,0,0,0)',
    },
    credits: false,
    title: {
      text: ''
    },
    xAxis: {
      visible: false,
      categories: [''],
    },
    yAxis: {
      min: 0,
      max: 100,
      visible: false,
    },
    legend: false,

    series: [{
      data: [100],
      grouping: false,
      animation: false,
      enableMouseTracking: false,
      showInLegend: false,
      color: '#e5f7ff',
      pointWidth: 25,
      borderWidth: 0,
      dataLabels: {
        className: 'highlight',
        format: '',
        enabled: true,
        align: 'right',
        style: {
          color: 'white',
          textOutline: false,
        }
      }
    }, {
      enableMouseTracking: false,
      data: [percent_complete],
      color: '#00adff',
      borderWidth: 0,
      pointWidth: 25,
      dataLabels: {
        enabled: true,
        inside: true,
        align: 'center',
        format: '{point.y}%',
        style: {
          color: text_color,
          textOutline: false,
        }
      }
    }]
  });
}

