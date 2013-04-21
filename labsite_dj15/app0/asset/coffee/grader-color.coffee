nameToColor = (name) ->
  [r, g, b] = [0, 1, 2].map (i)->
    if name.length > i
      100 + (name.charCodeAt i) % 100
    else 0
  'rgb('+r+','+g+','+b+')'

window.updateGrader = ->
  $('.grader-name').each (i, elem) -> $(elem).css
      color: nameToColor $(elem).html()

$ -> updateGrader()
