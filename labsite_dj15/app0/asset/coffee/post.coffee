checkSpec = (s) ->
  try
    s = $.parseJSON s
  catch err
    console.log err
    return 0
  if not s.root or not s.problems
    return 0
  for prob in s.problems
    if prob.type not in ['code', 'text'] or not prob.name or not prob.points
      return 0
  1

$ -> (
  $('#id_duetime').datepicker()
  descInput = $('#id_description')
  descPreview = $('#desc-preview')
  titleInput = $('#id_title')
  convert = new Markdown.getSanitizingConverter().makeHtml
  updatePreview = ->
    text = '#' + titleInput.val() + '\n' + descInput.val()
    descPreview.html convert text
  # update preview for each key stroke
  descInput.keyup updatePreview
  titleInput.keyup updatePreview
  # update preview for the first time
  updatePreview()

  # spec widget
  specInput = $('#id_spec_str')
  specCheck = 0
  specInput.keyup ->
    if specCheck
      isValid = checkSpec specInput.val()
      if isValid
        specCheck.html 'Check: <span style="color: #3cb868">valid</span>'
      else
        specCheck.html 'Check: <span class="errorlist">invalid</span>'
    else
      specInput.prev().remove()
      $('<div id="spec-check"></div>').insertBefore specInput
      specCheck = $('#spec-check')
)
