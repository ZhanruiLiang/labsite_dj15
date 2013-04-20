$(
    csrftoken = $.cookies.get 'csrftoken'
    csrfSafeMethod = (method) ->
        # these HTTP methods do not require CSRF protection
        /^(GET|HEAD|OPTIONS|TRACE)$/.test method
    $.ajaxSetup {
        crossDomain: false
        beforeSend: (xhr, settings) ->
            if not csrfSafeMethod settings.type
                xhr.setRequestHeader "X-CSRFToken", csrftoken
    }
)
