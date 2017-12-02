
function updateChanges() {
    $.get("update_button").done(function(data) {
        $('#button_list').html("");
        if (data['desks']) {
            for (i = 0; i < data['desks'].length; i++) {
                button_id = 'room-' + data['desks'][i]['name'];
                if ($('#' + button_id).length == 0) {
                    newButton = "<span class = 'font20'><a class = 'smallbtn' id = 'room-" + data['desks'][i]['name'] + "' href = 'playroom/" + data['desks'][i]['name'] + "'>" + data['desks'][i]['name'] + "</a></span>";
                    $('#button_list').append(newButton);
                }
            }
        }
    })
}

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
                //debugger;
                console.log($('#newplay_form').html());
                return $('#newplay_form').html();
            }
        });
    });

    window.setInterval(updateChanges, 5000);
});