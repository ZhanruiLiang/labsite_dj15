lookup = (a, key)->
  for [k, v] in a
    if k == key
      return v
  null

nameToColor = (name) ->
  [r, g, b] = [0, 1, 2].map (i)->
    if name.length > i
      100 + (name.charCodeAt i) % 100
    else 0
  'rgb('+r+','+g+','+b+')'

itervalues = (a)-> v for [k, v] in a

pre = (data) -> if data then $ '<pre>' + data + '</pre>' else ''

max = (a, b) -> if a > b then a else b
min = (a, b) -> if a < b then a else b

relhref = (name)-> $('head link[rel="'+name+'"]').attr 'href'

class ThemeSet
  @COOKIE_NAME: 'fav-theme'
  constructor: () ->
    @div = $ '#themes'
    @styles = []
    for link in $ '#themes link'
      style = {}
      link = style.csslink = link = $ link
      name = style.name = link.attr('id').slice(6)
      button = style.button = $ '<button>'+style.name+'</button>'
      button.addClass 'choice'
      do (name) => button.click => @set_theme name
      @styles.push [name, style]
      $('#themes .choices').append button

    @selected = lookup @styles, (($.cookies.get ThemeSet.COOKIE_NAME) or 'default')
    @set_theme @selected.name

  set_theme: (name) ->
    for style in itervalues @styles
      style.csslink.attr 'disabled', 'disabled'
      style.button.removeClass 'selected'
    @selected = style = lookup @styles, name
    style.button.addClass 'selected'
    style.csslink.removeAttr 'disabled'
    $.cookies.set ThemeSet.COOKIE_NAME, name,
      path: '/'
      expires: 365

class Problem
  constructor: (div) ->
    @name = div.data 'name'
    @points = div.data 'points'
    @con = div.find 'div.console div.console-inner'
    @form = div.find 'form'
    @runButton = div.find 'button.run'
    @running = false
    @comID = div.data 'comid'
    @scoreMeter = div.find '.score-meter'

    @form.ajaxForm
      timeout: 20000
      success: (data) =>
        @update_console data.message, data.code
        @scoreMeter.removeClass('notgraded score').addClass('score').html(
          'Graded ' + @form.find('input[type="radio"]:checked').val())

    @update_console 'This is the console for problem ' + @name

    @runButton.click =>
      if not @running
        @start_run()
      else
        @end_run()

    @runID = null

  update_console: (msg, code=0) ->
    if not msg or msg == '' then return
    item = $ '<div class="info-item"></div>'
    item.html msg
    item.addClass (if code == 0 then 'good' else 'bad')
    @con.append(item).scrollTo(item, 500)

  log_ajax_error: (jqXHR, textStatus, errorThrown)=>
        @update_console jqXHR, 1
        @update_console textStatus, 1
        @update_console errorThrown, 1

  start_run: ()->
    if @running then return
    @running = true
    @runButton.addClass('warn').html('Interrupt')

    console.log '/m/run/' +  @comID + '/'
    $.ajax
      type: 'post'
      url: '/m/run/' + @comID + '/'
      success: (data)=>
        if data.code == 0
          @runID = data.runID
          @interact ''
      error: @log_ajax_error

  interact: (data)->
    $.ajax
      type: 'post'
      url: '/m/interact/' + @runID + '/'
      data:
        input: data
      dataType: 'json'
      success: (data) =>
        code = data.code
        if code == 0
          @update_console (pre data.stdout), 0
          @update_console (pre data.stderr), 1
          if data.retcode != null
            @update_console (pre 'retcode: ' + data.retcode), 1
          if data.retcode or data.retcode == 0
            @run_end()
          else
            @prompt()
        else
          @update_console data.message, 1
          @run_end()
      error: @log_ajax_error

  run_end: ()->
    @running = false
    @runButton.removeClass('warn').html('Run')
    @update_console 'ended', 1

  end_run: ()->
    if not @running then return
    @run_end()
    $.ajax
      type: 'post'
      url: '/m/stop/' + @runID + '/'

  prompt: ()->
    placeholder = "waiting for input..."
    item = $ '<input type="text" placeholder="waiting for input..."/>'
    item.css 'font-family', 'monospace'
    item.addClass 'prompt'
    item.keypress (event)=>
      if event.keyCode == 13
        @interact item.val() + '\n'
      item.attr 'size', max(placeholder.length, item.val().length+1)

    @con.append(item).scrollTo(item, 500)
    item.focus()

$ ->(
  themes = new ThemeSet()
  problems = for div in $('#rows .row')
    new Problem($ div)
  $('#fin-next').click ->
    $.ajax
      type: 'post'
      url: '/m/finish/' + $('#fin-next').data('cur-sid') + '/'
      success: (data) ->
        if data.code == 0
          window.location = relhref 'next'
  $('#next').click ->
    window.location = relhref 'next'
  $('#back').click ->
    window.location = relhref 'back'
)
