/**
 * Created by Nausicaasnow on 2017/10/27.
 */

$(document).ready(function() {
    // using jQuery
  // https://docs.djangoproject.com/en/1.10/ref/csrf/
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length +
            1));
          break;
        }
      }
    }
    return cookieValue;
  }

  var csrftoken = getCookie('csrftoken');

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });

  console.log('hello world!');
  // Create a new WebSocket
    ws = new WebSocket("ws://" + window.location.host + "/test/");
    // Make it show an alert when a message is received
    ws.onmessage = function(message) {
        console.log(message);
        console.log(message.data + ' hi!');
    }
    // Send a new message when the WebSocket opens
    ws.onopen = function() {
        ws.send('Hello, world');
    }
    if (ws.readyState == WebSocket.OPEN) ws.onopen();
    console.log('ws finished!');

    $('#get_card').on('click', function(event) {
        event.preventDefault(); // Prevent form from being submitted
        console.log("click!");
        ws.send("click");

  });

});

