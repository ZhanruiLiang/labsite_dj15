$ ->
  updateList = ->
    $('#submissions').html 'loading list...'
    $.ajax
      url: '/m/submission_list/' + g_assID + '/'
      type: 'get'
      success: (data) ->
        $("#submissions").html data.list
        $("#submissions button.delete").click (event)->
          sid = $(event.target).data "sid"
          $.ajax
            type: 'post'
            url: '/m/delete_submission/' + sid + '/'
            success: (success) ->
              if success
                updateError ''
                updateList()
              else
                updateError "Error, failed to delete."
        $("#submissions button.view").click (event)->
          sid = $(event.target).data "sid"
          window.location = '/m/subm/' + sid + '/'
        $('#submissions td.fail').click (e) ->
          tr = $(e.target).parent()
          sid = tr.data 'sid'
          message = tr.data 'message'
          updateError message

  updateError = (message) ->
    errorList = $('#error-list')
    errorList.css
      'background-color': '#ffaaaa'
      'color': '#1b533b'
    errorList.html message
    if message
      errorList.show()
      $.scrollTo(errorList)
    else
      errorList.hide()

  $('#upload-form').ajaxForm
    beforeSubmit: ()->
      $('#upload-status').html "Uploading..."
      $('#error-list').hide()
      $('#upload-button').hide()
    timeout: 120000
    error: (jqXHR, textStatus, errorThrown) ->
      $('#upload-status').html 'Uploaded failed: ' + textStatus + '/' + errorThrown
      $('#upload-button').show()
    success: (data) ->
      if data.code == 0
        updateList()
        updateError ''
        $('#upload-status').html 'Uploaded.'
      else if data.code > 0
        updateError data.message
        $('#upload-status').html 'Upload failed.'
        updateList()
      $('#upload-button').show()

  convert = new Markdown.getSanitizingConverter().makeHtml
  $('#desc').html convert $('#desc').html()

  updateList()
  updateError ''
