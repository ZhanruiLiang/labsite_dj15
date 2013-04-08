flip = (f) ->
    (a, b) -> f b, a

$(
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
                        $("#error-list").html "Server error, failed to delete."

    updateList = ->
        (flip Dajaxice.submission_list) { assID: assID }, (data) ->
            $("#submissions").html data.list

    $('#upload-form').ajaxForm
        beforeSubmit: ()->
            $('#upload-status').html "Uploading..."
        success: (data) ->
            if data.code == 0
                updateList()
                $('#error-list').html ''
                $('#upload-status').html "Uploaded."
            else if data.code > 0
                # upload error
                $('#error-list').html data.message
                $('#upload-status').html "Upload failed."

    updateList()
)
