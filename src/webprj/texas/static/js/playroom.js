var timer = 10;

function timer_10sec() {
    if (timer >= 0) {
        var time_str = '0' + timer;
        timer--;
        time_str = time_str.substring(time_str.length - 2, time_str.length)
        $('#message').html('00:' + time_str);
        setTimeout(timer_10sec, 1000);
    } else {
        timer = 10;
        $('#message').html('timeout!');
        var message = {
            'message': 'timeout'
        };
        socket.send(JSON.stringify(message));
    }
}

//
function click_hold() {
    //timer_10sec();
    var message = {
        'message': 'hold'
    };
    socket.send(JSON.stringify(message));
}

function click_fold() {
    var message = {
        'message': 'fold'
    };
    socket.send(JSON.stringify(message));
}

function click_raise(val) {
    var message = {
        'message': 'raise',
        'value': val
    };
    socket.send(JSON.stringify(message));
}

$(document).ready(function () {
    console.log(window.location.pathname);
    console.log(window.location.host);
    socket = new WebSocket("ws://" + window.location.host + "/chat/");

    // socket.onopen = function() {
    //     socket.send("have opened");
    // };
    // Call onopen directly if socket is already open
    if (socket.readyState === WebSocket.OPEN) {
        socket.onopen();
    }

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

    //initialize the page
    document.getElementById("start_game").disabled = true;


    for (i = 1; i < 9; i++) {
        //document.getElementById("player-" + i).style.visibility = 'hidden';
        //visibility = 'visible'
    }

    $('#game_hold').on('click', function (event) {
        event.preventDefault(); // Prevent form from being submitted
        var message = {
            'message': 'hold'
        };
        socket.send(JSON.stringify(message));
    });

    $('#game_fold').on('click', function (event) {
        event.preventDefault(); // Prevent form from being submitted
        var message = {
            'message': 'fold'
        };
        socket.send(JSON.stringify(message));
    });

    $('#leave_room').on('click', function (event) {
        event.preventDefault(); // Prevent form from being submitted
        var message = {
            'command': 'leave'
        };
        socket.send(JSON.stringify(message));
        window.location.replace('lobby');
    });

    $('#start_game').on('click', function (event) {
        event.preventDefault(); // Prevent form from being submitted
        var message = {
            'start_game': 'yes'
        };
        socket.send(JSON.stringify(message));
    });

    socket.onmessage = function (message) {

        console.log(message.data);

        var data = JSON.parse(message.data);

        if (data['can_start'] === 'yes') {
            document.getElementById("start_game").disabled = false;
        }

        if (data['new_player']) {
            $.ajax({
                type: 'post',
                url: 'addplayer',
                data: data['new_player'],
                success: function(data) {
                    if (data.players){
                        for (i = 0; i < data.players.length; i++){
                            username = data.players[0]['username'];
                            position = data.players[0]['position'];
                            $('#player-' + position)[0].children[0].children[0].children[0].children[1].innerHTML = username;
                            $('#player-' + position)[0].style.visibility = "visible";
                        }
                    }
                }
            })
        }

        if (data['user_cards']) {
            values = data['user_cards'].split(" ");
            if (values.length === 2){
                for (i = 0; i < 2; i++){
                    num = values[i] % 13;
                    color = (values[i] - num++) / 13;
                    switch (color){
                        case 0:
                        values[i] = '♥';
                        break;
                        case 1:
                        values[i] = '♣';
                        break;
                        case 2:
                        values[i] = '♦';
                        break;
                        case 3:
                        values[i] = '♠';
                        break;
                        default:
                        break;
                    }
                    switch (num){
                        case 11:
                        values[i] = 'J' + values[i];
                        break;
                        case 12:
                        values[i] = 'Q' + values[i];
                        break;
                        case 13:
                        values[i] = 'K' + values[i];
                        default:
                        values[i] = num + values[i];
                        break;
                    }
                    $("#card-0-" + (i + 1)).html("<p>" + values[i] + "</p>");
                }
            }
            for (i = 1; i < 9; i++){
                $("#card-" + i + "-1").html("<p>*</p>");
                $("#card-" + i + "-2").html("<p>*</p>");
                $('#player-' + i)[0].children[0].children[0].children[0].children[0].innerHTML = "";
            }
        }

        if (data['big_blind'] && data['small_blind'] && data['dealer']) {
            $.ajax({
                type: 'post',
                url: 'getjob/' + data['big_blind'][1] + '/' + data['small_blind'][1] + '/' + data['dealer'][1],
                data: "",
                success: function(data) {
                 pos1 = data['big_blind'];
                 $('#player-' + pos1)[0].children[0].children[0].children[0].children[0].innerHTML += "[big blind]<br>\n";

                 pos2 = data['small_blind'];
                 $('#player-' + pos2)[0].children[0].children[0].children[0].children[0].innerHTML += "[small blind]<br>\n";

                 pos3 = data['dealer'];
                 $('#player-' + pos3)[0].children[0].children[0].children[0].children[0].innerHTML += "[dealer]<br>\n";
             }
         })
        }

        if (data['start_timer']) {
            timer_10sec();
        }
    };
});