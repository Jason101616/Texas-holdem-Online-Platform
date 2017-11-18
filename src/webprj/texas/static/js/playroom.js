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
function start_game() {

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
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    //initialize the page
    start_game = document.getElementById("get_card");
    //start_game.disabled = true;


    for (i = 1; i < 9; i++) {
        document.getElementById("player-" + i).style.visibility = 'hidden';
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

        if (data['is_full'] == 'yes') {
            start_game = document.getElementById("get_card"); 
            start_game.disabled = true;
        }

        if (data['new_player']) {
            debugger;
            $.ajax({
                type: 'post',
                url: 'addplayer',
                data: data['new_player'],
                success: function(data) {
                    debugger;
                    if (data.players){
                        for (i = 0; i < data.players.length; i++){
                            username = data.players[0]['username'];
                            position = data.players[0]['position'];
                            $('#player-' + position)[0].children[0].children[0].children[0].innerHTML = username;
                            $('#player-' + position)[0].style.visibility = "visible";
                        }
                    }
                }
            })
        }

        if (data.card) {
            for (var i = 0; i < 9; i++) {
                if (!data.card[i]) {
                    continue;
                }
                var name = data.card[i][0];
                debugger;
                switch (data.card[i][1]) {
                    case 0:
                    name += '♥';
                    break;
                    case 1:
                    name += '♣';
                    break;
                    case 2:
                    name += '♦';
                    break;
                    case 3:
                    name += '♠';
                    break;
                    default:
                    break;
                }
                data.card[i] = name;
            }
        }

        if (data.status === "start") {
            var i = 1;
            for (; i <= 5; i++) {
                $('#desk-' + i).html("X");
            }
            for (; i <= 7; i++) {
                $('#robot-' + (i - 5)).html("X");
            }
            for (; i <= 9; i++) {
                $('#me-' + (i - 7)).html(data.card[i - 1]);
            }
            $('#message').html("");
        } 
        else if (data.status === 'hold') {
            switch (data.hold_click_cnt) {
                case 1:
                var i = 1;
                for (; i <= 3; i++) {
                    $('#desk-' + i).html(data.card[i - 1]);
                }
                break;

                case 2:
                $('#desk-' + 4).html(data.card[3]);
                break;

                case 3:
                $('#desk-' + 5).html(data.card[4]);
                break;

                default:
                var i = 6;
                for (; i <= 7; i++) {
                    $('#robot-' + (i - 5)).html(data.card[i - 1]);
                }
                $('#message').html(data.result);
                break;
            }
        } 
        else if (data.status === 'fold') {
            $('#message').html(data.result);
            var i = 1;
            for (; i <= 5; i++) {
                $('#desk-' + i).html(data.card[i - 1]);
            }
            for (; i <= 7; i++) {
                $('#robot-' + (i - 5)).html(data.card[i - 1]);
            }
            for (; i <= 9; i++) {
                $('#me-' + (i - 7)).html(data.card[i - 1]);
            }
        }
    };
});