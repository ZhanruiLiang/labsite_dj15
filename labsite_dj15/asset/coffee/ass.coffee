flip = (f) ->
    (a, b) -> f b, a

$ -> (
    updateList = ->
        (flip Dajaxice.submission_list) { assID: assID }, (data) ->
            $("#submissions").html data.list
            buttons = $("#submissions button.delete")
            for button in buttons
                button = $ button
                sid = button.data "sid"
                do (sid) ->
                    button.click ->
                        (flip Dajaxice.delete_submission) { submissionID: sid }, (success) ->
                            if success
                                $("#submissions tr[data-sid="+sid+"]").remove()
                            else
                                updateError "Server error, failed to delete."

    updateError = (message) ->
        errorList = $('#error-list')
        errorList.css
            'background-color': '#ffaaaa'
            'color': '#1b533b'
        errorList.html message
        if message
            errorList.show()
        else
            errorList.hide()

    $('#upload-form').ajaxForm
        beforeSubmit: ()->
            $('#upload-status').html "Uploading..."
            $('#error-list').hide()
            $('#upload-button').hide()
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
            $('#upload-button').show()

    updateList()
    updateError ''
)
