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

    $(function () {
        $('#newplay').popover({
            html: true,
            title: function () {
                //return $(this).parent().find('.head').html();
                return "create a new desk";
            },
            content: function () {
                debugger;
                return $('#newplay_form').html();
            }
        });
    });

    /*$('#newplay').on('click', function(event) {
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
    });*/
});