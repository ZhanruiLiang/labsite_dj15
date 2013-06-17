start_check = () ->
  $.ajax
    type: 'post'
    url: '/m/startsimcheck/'+gAssID+'/'
    success: (data)=>
      console.log data
      if data.code == 0
        show_check_started()
      else
        alert "request failed"
    error: ->
        alert "request failed"

show_check_started = () ->
  $('#start-button').html('checking...').attr('disabled', 'disabled')

new_diff_view = (diffResultPath) ->
  view = $('<div/>').addClass('diff')
  button = $('<button/>').addClass('dismiss').html('dismiss')
  button.click (event)->
    view.remove()
  view.append button
  $.ajax
    type: 'get'
    url: diffResultPath
    success: (data)->
      view.append $(data)
      view.prettyTextDiff()
  $('#diffviews').append view

$ ->
  $('#start-button').click start_check
  $('table.dataTable').dataTable
    iDisplayLength: 100
    bLengthChange: true
  $('table#diff-results button.view-diff').each (i, e)->
    button = $(e)
    diffID = button.data 'diffid'
    button.click (event)->
      new_diff_view '/m/diff/'+diffID+'/'
