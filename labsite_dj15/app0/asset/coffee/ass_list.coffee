$ ->
  $('.item-ass').each (i, elem) ->
    elem = $ elem
    elem.click ->
      window.location = elem.find('a').attr 'href'
