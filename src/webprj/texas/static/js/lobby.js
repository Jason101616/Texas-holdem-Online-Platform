$(document).ready(function () {

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
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
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $('#newplay').on('click', function(event) {
            event.preventDefault(); // Prevent form from being submitted
            var room_id = prompt("Please enter a desk name:", ""); 
            if (room_id){
                $.ajax({
                    type: 'post',
                    url: 'newplay/' + room_id,
                    data: '',
                    success: function (data) {
                        alert("Successfully created room: " + room_id);

                        button = "<span><a class = 'smallbtn' id = 'desk-" + room_id + "' href = 'playroom/" + room_id + "'>" + room_id + "</a></span>";
                        $("#newplay").before(button);
                    }
                })
            }
        });
});