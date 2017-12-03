var COUNT_DOWN = 30;
var timer = COUNT_DOWN;
var timeout;

var COUNT_DOWN_win = 5;
var timer_win = COUNT_DOWN_win;
var timeout_win;

function start_timer() {
    if (timer >= 0) {
        time_str = '0' + timer;
        timer--;
        time_str = time_str.substring(time_str.length - 2, time_str.length);
        $('#message').html('00:' + time_str);
        timeout = setTimeout(start_timer, 1000);
    }
    else {
        timer = COUNT_DOWN;
        var message = {'message' : 'timeout'};
        socket.send(JSON.stringify(message));
        $('#message').html('Timeout: automatically fold!');
    } 
}

function start_timer_win() {
    if (timer_win >= 0) {
        timer_win--;
        timeout_win = setTimeout(start_timer_win, 1000);
    }
    else {
        timer_win = COUNT_DOWN_win;
        var message = {'message' : 'timeout_win'};
        socket.send(JSON.stringify(message));
    } 
}

function stop_timer() {
    clearTimeout(timeout);
    $('#message').html('<br>');
    timer = COUNT_DOWN;
}

function click_hold() {
    stop_timer();
    console.log('click hold');
    var message = {
        'message': 'hold'
    };
    console.log(message);
    socket.send(JSON.stringify(message));
    clear_status();
}

function click_fold() {
    stop_timer();
    var message = {
        'message': 'fold'
    };
    console.log(message);
    socket.send(JSON.stringify(message));
    clear_status();
}

function click_allin() {
    stop_timer();
    var message = {
        'message': 'all_in'
    }
    console.log(message);
    socket.send(JSON.stringify(message));
    clear_status();
}

function click_raise() {
    stop_timer();
    val = $('#raise_value')[0].value;
    var message = {
        'message': 'raise',
        'value': val
    };
    console.log(message);
    socket.send(JSON.stringify(message));
    clear_status();
}

function change_raise_value() {
    var value = $('#raise_value')[0].value;
    $('#raise_calue_disp').html(value);
}

function clear_status() {
    $('#game_hold')[0].disabled = true;
    $('#game_fold')[0].disabled = true;
    $('#game_allin')[0].disabled = false;
    $('#game_raise')[0].disabled = false;

    for (i = 0; i < 9; i++) {
        $('#player-' + i).css('background', 'rgba(255,255,255,0)');
    }
}

$(document).ready(function () {
    console.log(window.location.pathname);
    console.log(window.location.host);
    socket =
    new WebSocket('ws://' + window.location.host + window.location.pathname);

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
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            }
        }
    });

    // initialize the page
    $('#start_game')[0].disabled = true;
    $('#game_hold')[0].disabled = true;
    $('#game_fold')[0].disabled = true;
    $('#game_raise')[0].disabled = true;
    $('#game_allin')[0].disabled = false;

    for (i = 1; i < 9; i++) {
        $('#player-' + i)[0].style.display = 'none';
        // visibility = 'visible'
    }

    function poker_string(value) {
        var num = value % 13;
        var color = (value - num++) / 13;
        switch (color) {
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
        switch (num) {
            case 1:
            value = 'A' + value;
            break;
            case 11:
            value = 'J' + value;
            break;
            case 12:
            value = 'Q' + value;
            break;
            case 13:
            value = 'K' + value;
            break;
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
    });

    socket.onmessage = function (message) {

        console.log(message.data);

        var data = JSON.parse(message.data);

        if (data['start_game']) {
            $('#start_game')[0].disabled = true;
            $('#message').html('Game started!');

            $('#player-0')[0].children[0].children[0].children[0].children[0].innerHTML = '';
            $('#player-0')[0].children[0].children[0].children[0].children[1].innerHTML = '';
            for (i = 1; i < 9; i++) {
                $('#player-' + i)[0].children[0].children[0].children[0].children[0].children[0].innerHTML = '';
                $('#player-' + i)[0].children[0].children[0].children[0].children[0].children[1].innerHTML = '';
            }

            $.ajax({
                type: 'post',
                url: 'addplayer',
                data: '',
                success: function (data) {
                    if (data.players) {
                        for (i = 0; i < data.players.length; i++) {
                            position = data.players[i]['position'];
                            chips = data.players[i]['chips'];

                            if (position == 0) {
                                $('#player-0')[0].children[0].children[0].children[3].children[0].innerHTML =
                                'Total chips: ' + chips;
                                $('#player-0')[0].children[0].children[0].children[3].children[1].innerHTML =
                                'Betting: 0';
                            } else {
                                $('#player-' + position)[0].children[1].children[0].innerHTML =
                                'Total chips: ' + chips;
                                $('#player-' + position)[0].children[1].children[1].innerHTML =
                                'Betting: 0';
                            }
                        }
                    }
                }
            })
        }

        if (data['new_player']) {
            $.ajax({
                type: 'post',
                url: 'addplayer',
                data: data['new_player'],
                success: function (data) {
                    if (data.players) {
                        for (i = 0; i < data.players.length; i++) {
                            username = data.players[i]['username'];
                            position = data.players[i]['position'];
                            if (position == 0) continue;

                            chips = data.players[i]['chips'];
                            $('#player-' + position)[0].children[0].children[0].children[0].children[0].children[2].innerHTML =
                            username;
                            //$('#player-' + position)[0].style.visibility = 'visible';
                            $('#player-' + position)[0].style.display = '';
                            $('#player-' + position)[0].children[1].children[0].innerHTML =
                            'Total chips: ' + chips;
                            $('#player-' + position)[0].children[1].children[1].innerHTML =
                            'Betting: 0';
                        }
                    }
                }
            })
        }

        if (data['user_cards']) {
            values = data['user_cards'].split(' ');
            if (values.length === 2) {
                for (i = 0; i < 2; i++) {
                    $('#card-0-' + (i + 1))
                    .html('<p>' + poker_string(values[i]) + '</p>');
                }
            }
            for (i = 1; i < 9; i++) {
                $('#card-' + i + '-1').html('<p class = \'small\'>*</p>');
                $('#card-' + i + '-2').html('<p class = \'small\'>*</p>');
                $('#player-' + i)[0].children[0].children[0].children[0].children[0].children[0].innerHTML = '';
                $('#player-' + i)[0].children[0].children[0].children[0].children[0].children[1].innerHTML = '';
            }
            for (i = 0; i < 5; i++) {
                $('#desk-' + i).html('*');
            }
        }

        if (data['big_blind'] && data['small_blind'] && data['dealer']) {
            $.ajax({
                type: 'post',
                url: 'getjob/' + data['big_blind'][1] + '/' + data['small_blind'][1] +
                '/' + data['dealer'][1],
                data: '',
                success: function (data) {
                    pos1 = data['big_blind'];
                    if (pos1 == 0) {
                        $('#player-' + pos1)[0].children[0].children[0].children[0].children[1].innerHTML +=
                        '[big blind]<br>\n';
                    }
                    else {
                        $('#player-' + pos1)[0].children[0].children[0].children[0].children[0].children[1].innerHTML +=
                        '[big blind]<br>\n';
                    }

                    pos2 = data['small_blind'];
                    if (pos2 == 0) {
                        $('#player-' + pos2)[0].children[0].children[0].children[0].children[1].innerHTML +=
                        '[small blind]<br>\n';
                    }
                    else {
                        $('#player-' + pos2)[0].children[0].children[0].children[0].children[0].children[1].innerHTML += '[small blind]<br>\n';
                    }

                    pos3 = data['dealer']
                    if (pos3 == 0) {
                        $('#player-' + pos3)[0].children[0].children[0].children[0].children[1].innerHTML +=
                        '[dealer]<br>\n';
                    }
                    else {
                        $('#player-' + pos3)[0].children[0].children[0].children[0].children[0].children[1].innerHTML += '[dealer]<br>\n';
                    }
                }
            })
        }

        if (data['cur_user_pos']) {
            stop_timer();

            $('#chips')
            .html('Chips in the pool: ' + data['total_chips_current_game']);

            total_new = data['cur_user_chips'];
            chip_new = data['cur_user_chips_this_game'];
            current_user_target_pos = data['cur_user_pos'];
            current_user_act = data['act'];

            $.ajax({
                type: 'post',
                url: 'get_position',
                data: '',
                success: function (data) {

                    $('#message').html(current_user_act);

                    login_user_pos = data['position'];
                    user_pos = parseInt(current_user_target_pos) - 1 - parseInt(login_user_pos);
                    if (user_pos < 0) user_pos += 9;

                    // update chip information
                    if (user_pos == 0) {

                        $('#player-0')[0].children[0].children[0].children[3].children[0].innerHTML =
                        'Total chips: ' + total_new;
                        $('#player-0')[0].children[0].children[0].children[3].children[1].innerHTML =
                        'Betting: ' + chip_new;

                        $('#player-0')[0].children[0].children[0].children[0].children[0].innerHTML = '~ ' + current_user_act + ' ~';

                    } else {
                        $('#player-' + user_pos)[0].children[1].children[0].innerHTML =
                        'Total chips: ' + total_new;
                        $('#player-' + user_pos)[0].children[1].children[1].innerHTML =
                        'Betting: ' + chip_new;

                        $('#player-' + user_pos)[0].children[0].children[0].children[0].children[0].children[0].innerHTML = '~ ' + current_user_act + ' ~';
                    }
                }
            })
        }

        if (data['move']) {
            stop_timer();

            for (i = 0; i < 9; i++) {
                $('#player-' + i).css('background', 'rgba(255,255,255,0)');
            }
            target_pos = data['move'];

            permission = {'check': data['check'], 'raise': data['raise']};

            $.ajax({
                type: 'post',
                url: 'get_position',
                data: '',
                success: function (data) {
                    login_user_pos = data['position'];
                    user_pos = parseInt(target_pos) - 1 - parseInt(login_user_pos);
                    if (user_pos < 0) user_pos += 9;

                    if (user_pos == 0) {
                        $('#game_fold')[0].disabled = false;
                        $('#game_allin')[0].disabled = false;
                        
                        if (permission['check']) {
                            $('#game_hold')[0].disabled = false;
                        }
                        if (permission['raise'][0]) {
                            $('#game_raise')[0].disabled = false;
                            $('#raise_value')[0].min = permission['raise'][1][0];
                            $('#raise_value')[0].max = permission['raise'][1][1];
                            $('#raise_value')[0].value = $('#raise_value')[0].min;
                            $('#raise_calue_disp').html($('#raise_value')[0].value);
                        }
                        start_timer();
                    }
                    $('#player-' + user_pos)
                    .css(
                        'background',
                        'linear-gradient(0deg, rgba(255,255,255,1), rgba(255,255,255,0))');
                }
            })
        }

        if (data['desk_cards']) {
            for (i = 0; i < data['desk_cards'].length; i++) {
                $('#desk-' + i)[0].innerHTML = poker_string(data['desk_cards'][i]);
            }
        }

        if (data['winner']) {
            user_cards = data['cards'];
            winner_pos = data['winner_pos'];
            $('#start_game')[0].disabled = false;
            $('#message').html('Winner is ' + data['winner'] + '!');

            clear_status();

            $.ajax({
                type: 'post',
                url: 'get_position',
                data: '',
                success: function (data) {
                    login_user_pos = data['position'];
                    // display all user cards
                    for (i = 0; i < 9; i++) {
                        if (user_cards[i.toString()]) {
                            pos = i - parseInt(login_user_pos);
                            if (pos < 0) pos += 9;

                            if (pos != 0) {
                                pokers = user_cards[i.toString()].split(' ');
                                pokers[0] = poker_string(parseInt(pokers[0]));
                                pokers[1] = poker_string(parseInt(pokers[1]));
                                $('#player-' + pos)[0].children[0].children[0].children[1].children[0].children[0].children[0].innerHTML = pokers[0];
                                $('#player-' + pos)[0].children[0].children[0].children[1].children[1].children[0].children[0].innerHTML = pokers[1];
                            }
                        }
                    }

                    winner_pos = parseInt(winner_pos) - parseInt(login_user_pos);
                    if (winner_pos == 0) {
                        start_timer_win();
                    }
                    if (winner_pos < 0) winner_pos += 9;
                    $('#player-' + winner_pos)
                    .css(
                        'background',
                        'linear-gradient(0deg, rgba(254,238,117,0.5), rgba(254,238,117,0))');
                }
            })
        }

        if (data['active_players']) {
            player_list = data['active_players'];
            $.ajax({
                type: 'post',
                url: 'get_position',
                data: '',
                success: function (data) {
                    login_user_pos = data['position'];
                    for (i = 0; i < 9; i++) {
                        //$('#player-' + i)[0].style.visibility = 'hidden';
                        $('#player-' + i)[0].style.display = 'none';
                    }
                    for (i = 0; i < player_list.length; i++) {
                        pos = player_list[i] - login_user_pos;
                        if (pos < 0) {
                            pos += 9;
                        }
                        //$('#player-' + pos)[0].style.visibility = 'visible';
                        $('#player-' + pos)[0].style.display = '';
                    }
                }
            })

        }

        if (data['owner']) {
            owner_position = data['owner'];
            if (data['can_start'] == 'yes') {
                $.ajax({
                    type: 'post',
                    url: 'get_position',
                    data: '',
                    success: function (data) {
                        login_user_pos = data['position'];
                        if (owner_position - 1 == login_user_pos) {
                            $('#message').html('Ready to start: please start the game');
                            $('#start_game')[0].disabled = false;
                        }
                        else {
                            $('#message').html('Waiting for the owner to start the game');
                            $('#start_game')[0].disabled = true;
                        }
                    }
                })
            }
            else {
                $('#message').html('Waiting for more players');
                $('#start_game')[0].disabled = true;
            }
        }

        if (data['restart']) {
            $('#start_game')[0].disabled = true;
            for (i = 1; i < 9; i++) {
                $('#player-' + i)[0].style.display = 'none'
            }
            for (i = 0; i < 5; i++) {
                $('#desk-' + i).html('');
            }
            for (i = 1; i < 3; i++) {
                $('#card-0-' + i).html('');
            }
            $('#player-0')[0].children[0].children[0].children[3].children[0].innerHTML =
            'Total chips: ' + data['cur_user_chips'];
            $('#player-0')[0].children[0].children[0].children[3].children[1].innerHTML =
            'Betting: 0';
            $('#player-0')[0].children[0].children[0].children[0].children[1].innerHTML = '';
            $('#player-0')[0].children[0].children[0].children[0].children[0].innerHTML = '';
            $('#player-0').css('background', 'rgba(255,255,255,0)');
            $('#message').html('Waiting for more players');
            $('#chips').html('<br>');
        }

        if (data['get_out']) {
            window.location.replace('lobby');
        }
    };
});