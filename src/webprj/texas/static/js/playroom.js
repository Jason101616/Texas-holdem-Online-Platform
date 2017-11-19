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

function click_hold() {
    var message = {
        'message': 'hold'
    };
    console.log(message);
    socket.send(JSON.stringify(message));

    clear_status();
}

function click_fold() {
    var message = {
        'message': 'fold'
    };
    console.log(message);
    socket.send(JSON.stringify(message));

    clear_status();
}

function click_raise(val) {
    var message = {
        'message': 'raise',
        'value': val
    };
    console.log(message);
    socket.send(JSON.stringify(message));

    clear_status();
}

function clear_status() {
    $('#game_hold')[0].disabled = true;
    $('#game_fold')[0].disabled = true;
    $('#game_raise100')[0].disabled = true;
    $('#game_raise200')[0].disabled = true;

    for (i = 0; i < 9; i++){
        $('#player-' + i).css("background", "rgba(255,255,255,0)");
    }
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
    $('#start_game')[0].disabled = true;
    $('#game_hold')[0].disabled = true;
    $('#game_fold')[0].disabled = true;
    $('#game_raise100')[0].disabled = true;
    $('#game_raise200')[0].disabled = true;

    for (i = 1; i < 9; i++) {
        $('#player-' + i)[0].style.visibility = 'hidden';
        //visibility = 'visible'
    }

    function poker_string(value) {
        var num = value % 13;
        var color = (value - num++) / 13;
        switch (color){
            case 0:
            value = '♥';
            break;
            case 1:
            value = '♣';
            break;
            case 2:
            value = '♦';
            break;
            case 3:
            value = '♠';
            break;
            default:
            break;
        }
        switch (num){
            case 11:
            value = 'J' + value;
            break;
            case 12:
            value = 'Q' + value;
            break;
            case 13:
            value = 'K' + value;
            default:
            value = num + value;
            break;
        }
        return value;
    }

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
        $('#leave_room')[0].disabled = true;
    });

    socket.onmessage = function (message) {

        console.log(message.data);

        var data = JSON.parse(message.data);

        if (data['can_start'] === 'yes') {
            $('#start_game')[0].disabled = false;
        }

        if (data['new_player']) {
            $.ajax({
                type: 'post',
                url: 'addplayer',
                data: data['new_player'],
                success: function(data) {
                    if (data.players){
                        for (i = 0; i < data.players.length; i++){
                            username = data.players[i]['username'];
                            position = data.players[i]['position'];
                            chips = data.players[i]['chips'];
                            $('#player-' + position)[0].children[0].children[0].children[0].children[1].innerHTML = username;
                            $('#player-' + position)[0].style.visibility = "visible";
                            $('#player-' + position)[0].children[0].children[2].children[0].children[0].innerHTML = "Total chips: " + chips;
                            $('#player-' + position)[0].children[0].children[2].children[0].children[1].innerHTML = "Betting: 0";
                        }
                    }
                }
            })
        }

        if (data['user_cards']) {
            values = data['user_cards'].split(" ");
            if (values.length === 2){
                for (i = 0; i < 2; i++){
                    $("#card-0-" + (i + 1)).html("<p>" + poker_string(values[i]) + "</p>");
                }
            }
            for (i = 1; i < 9; i++){
                $("#card-" + i + "-1").html("<p>*</p>");
                $("#card-" + i + "-2").html("<p>*</p>");
                $('#player-' + i)[0].children[0].children[0].children[0].children[0].innerHTML = "";
            }
            for (i = 0; i < 5; i++){
                $("#desk-" + i).html('*');
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

        if (data['cur_user_pos'] && data['cur_user_chips']) {
            chips = data['cur_user_chips'];
            $.ajax({
                type: 'post',
                url: 'get_position/' + data['cur_user_pos'],
                data: "",
                success: function(data) {
                    //update chip information
                    if (data['position'] == 0){
                        chip_ori = $('#player-0')[0].children[0].children[0].children[3].children[1].innerHTML;
                        chip_ori = parseInt(chip_ori.split(":")[1]);

                        total_ori = $('#player-0')[0].children[0].children[0].children[3].children[0].innerHTML;
                        total_ori = parseInt(total_ori.split(":")[1]);
                        total_new = total_ori - (chips - chip_ori);

                        $('#player-0')[0].children[0].children[0].children[3].children[0].innerHTML = "Total chips: " + total_new;
                        $('#player-0')[0].children[0].children[0].children[3].children[1].innerHTML = "Betting: " + chips;
                    }
                    else {
                        chip_ori =  $('#player-' + data['position'])[0].children[0].children[2].children[0].children[1].innerHTML;
                        chip_ori = parseInt(chip_ori.split(":")[1]);

                        total_ori = $('#player-' + data['position'])[0].children[0].children[2].children[0].children[0].innerHTML;
                        total_ori = parseInt(total_ori.split(":")[1]);
                        total_new = total_ori - (chips - chip_ori);

                        $('#player-' + data['position'])[0].children[0].children[2].children[0].children[0].innerHTML = "Total chips: " + total_new;
                        $('#player-' + data['position'])[0].children[0].children[2].children[0].children[1].innerHTML = "Betting: " + chips;
                    }
                }
            })
        }

        if (data['move']) {
            for (i = 0; i < 9; i++){
                $('#player-' + i).css("background", "rgba(255,255,255,0)");
            }
            pos = data['move'];
            $.ajax({
                type: 'post',
                url: 'get_position/' + pos,
                data: '',
                success: function(data) {
                    // debugger;
                    if (data['position'] == 0) {
                        $('#game_hold')[0].disabled = false;
                        $('#game_fold')[0].disabled = false;
                        $('#game_raise100')[0].disabled = false;
                        $('#game_raise200')[0].disabled = false;
                    }
                    $('#player-' + data['position']).css("background", "linear-gradient(0deg, rgba(255,255,255,1), rgba(255,255,255,0))");
                }
            })
        }

        if (data['desk_cards']) {
            for (i = 0; i < data['desk_cards'].length; i++){
                $('#desk-' + i)[0].innerHTML = poker_string(data['desk_cards'][i]);
            }
        }

        if (data['start_timer']) {
            timer_10sec();
        }
    };
});