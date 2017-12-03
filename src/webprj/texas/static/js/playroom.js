var COUNT_DOWN = 30;
var timer = COUNT_DOWN;
var timeout;

var timer_fake = COUNT_DOWN;
var timeout_fake;

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
    }
}

function start_timer_fake() {
    if (timer_fake >= 0) {
        time_str = '0' + timer_fake;
        timer_fake--;
        time_str = time_str.substring(time_str.length - 2, time_str.length);
        $('#message').html('00:' + time_str);
        timeout_fake = setTimeout(start_timer_fake, 1000);
    }
    else {
        timer_fake = COUNT_DOWN;
    }
}

function stop_timer() {
    clearTimeout(timeout);
    $('#message').html('<br>');
    timer = COUNT_DOWN;
}

function stop_timer_fake() {
    clearTimeout(timeout_fake);
    $('#message').html('<br>');
    timer_fake = COUNT_DOWN;
}

function click_hold() {
    stop_timer();
    var message = {
        'message': 'hold'
    };
    socket.send(JSON.stringify(message));
    clear_status();
}

function click_fold() {
    stop_timer();
    var message = {
        'message': 'fold'
    };
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
    $('#game_allin')[0].disabled = true;
    $('#game_raise')[0].disabled = true;

    for (i = 0; i < 9; i++) {
        $('#player-' + i).css('background', 'rgba(255,255,255,0)');
    }
}

$(document).ready(function () {
    console.log(window.location.pathname);
    console.log(window.location.host);
    socket =
    new WebSocket('ws://' + window.location.host + window.location.pathname);

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
    $('#game_allin')[0].disabled = true;

    for (i = 1; i < 9; i++) {
        $('#player-' + i)[0].style.display = 'none';
        // visibility = 'visible'
    }

    function poker_string(value) {
        var num = value % 13;
        var color = (value - num++) / 13;
        var font;
        switch (num) {
            case 1:
            num = 'A';
            break;
            case 11:
            num = 'J';
            break;
            case 12:
            num = 'Q';
            break;
            case 13:
            num = 'K';
            break;
            default:
            num = num.toString();
            break;
        }
        switch (color) {
            case 0:
            color = '&clubs;';
            font = 'black';
            break;
            case 1:
            color = '&spades;';
            font = 'black';
            break;
            case 2:
            color = '&hearts;';
            font = 'red';
            break;
            case 3:
            color = '&diams;';
            font = 'red';
            break;
            default:
            break;
        }
        var card = {'color' : color, 'num' : num, 'font': font};
        return card;
    }

    function set_poker(id, card) {
        content = "<p class = 'card-txt " + card['font'] + "'>" + card['num'] + "</p>";
        content += "<p class = 'card-img " + card['font'] + "'>" + card['color'] + "</p>";
        $('#' + id).html(content);
    }

    function set_poker_null(id) {
        //content = "<p class = 'card-img gray'>#</p>";
        content = "<div class = 'back'></div>";
        $('#' + id).html(content);
    }

    $('#leave_room').on('click', function (event) {
        event.preventDefault(); // Prevent form from being submitted
        var message = {
            'command': 'leave'
        };
        socket.send(JSON.stringify(message));
        window.location.replace('goto_lobby');
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

            $('#player-0')[0].children[0].children[0].children[0].children[0].children[0].innerHTML = '';
            $('#player-0')[0].children[0].children[0].children[0].children[0].children[1].innerHTML = '';
            for (i = 1; i < 9; i++) {
                $('#player-' + i)[0].children[0].children[0].children[0].children[0].children[0].innerHTML = '';
                $('#player-' + i)[0].children[0].children[0].children[0].children[0].children[1].innerHTML = '';
            }

            for (i = 0; i < 9; i++) {
                $('#chips-' + i + '-2').html("Betting: 0");
            }

            for (i = 0; i < 5; i++) {
                $('#desk-' + i).css('background', 'rgba(255,255,255,1)');
            }
            for (i = 0; i < 9; i++) {
                $('#card-' + i + '-1').css('background', 'rgba(255,255,255,1)');
                $('#card-' + i + '-2').css('background', 'rgba(255,255,255,1)');
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

                            $('#chips-' + position + '-1').html("Total chips: " + chips);
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
                            if (position != 0) {
                                $('#player-' + position)[0].children[0].children[0].children[0].children[0].children[2].innerHTML = username;
                            }

                            $('#player-' + position)[0].style.display = '';

                            $('#chips-' + position + '-1').html("Total chips: " + chips);
                            $('#chips-' + position + '-2').html("Betting: 0");
                        }
                    }
                }
            })
        }

        if (data['user_cards']) {
            values = data['user_cards'].split(' ');
            if (values.length === 2) {
                for (i = 0; i < 2; i++) {
                    card = poker_string(parseInt(values[i]));
                    set_poker('card-0-' + (i + 1), card);
                }
            }
            for (i = 1; i < 9; i++) {
                set_poker_null('card-' + i + '-1');
                set_poker_null('card-' + i + '-2');
                $('#player-' + i)[0].children[0].children[0].children[0].children[0].children[0].innerHTML = '';
                $('#player-' + i)[0].children[0].children[0].children[0].children[0].children[1].innerHTML = '';
            }
            for (i = 0; i < 5; i++) {
                set_poker_null('desk-' + i);
            }
        }

        if (data['big_blind'] && data['small_blind'] && data['dealer']) {
            $('#chips').html('Chips in the pool: ' + data['total_chips']);
            big_blind_betting = data['big_blind'][2];
            big_blind_chips = data['big_blind'][3];
            small_blind_betting = data['small_blind'][2];
            small_blind_chips = data['small_blind'][3];
            $.ajax({
                type: 'post',
                url: 'getjob/' + data['big_blind'][1] + '/' + data['small_blind'][1] +
                '/' + data['dealer'][1],
                data: '',
                success: function (data) {
                    pos1 = data['big_blind'];
                    pos2 = data['small_blind'];
                    pos3 = data['dealer'];

                    if (pos1 == pos3) {
                        content = "<span class = 'label label-bgbl'>big blind</span>&nbsp;";
                        content += "<span class = 'label label-dealer'>dealer</span>";
                        $('#job-' + pos1).html(content);
                    }
                    else {
                        content = "<span class = 'label label-bgbl'>big blind</span>";
                        $('#job-' + pos1).html(content);

                        content = "<span class = 'label label-dealer'>dealer</span>";
                        $('#job-' + pos3).html(content);
                    }
                    $('#chips-' + pos1 + '-1').html("Total chips: " + big_blind_chips);
                    $('#chips-' + pos1 + '-2').html("Betting: " + big_blind_betting);

                    content = "<span class = 'label label-smbl'>small blind</span>";
                    $('#job-' + pos2).html(content);

                    $('#chips-' + pos2 + '-1').html("Total chips: " + small_blind_chips);
                    $('#chips-' + pos2 + '-2').html("Betting: " + small_blind_betting);
                }
            })
        }

        if (data['cur_user_pos']) {
            stop_timer_fake();
            stop_timer();

            $('#chips').html('Chips in the pool: ' + data['total_chips_current_game']);


            total_new = data['cur_user_chips'];
            chip_new = data['cur_user_chips_this_game'];
            current_user_target_pos = data['cur_user_pos'];
            current_user_act = data['act'];

            $.ajax({
                type: 'post',
                url: 'get_position',
                data: '',
                success: function (data) {

                    login_user_pos = data['position'];
                    user_pos = parseInt(current_user_target_pos) - 1 - parseInt(login_user_pos);
                    if (user_pos < 0) user_pos += 9;

                    // update chip information
                    $('#chips-' + user_pos + '-1').html("Total chips: " + total_new);
                    $('#chips-' + user_pos + '-2').html("Betting: " + chip_new);

                    if (user_pos == 0) {
                        $('#player-0')[0].children[0].children[0].children[0].children[0].children[0].innerHTML = '~ ' + current_user_act + ' ~';
                        $('#player-0')[0].children[0].children[0].children[0].children[0].children[0].className = "status " + current_user_act;
                    }
                    else {
                        $('#player-' + user_pos)[0].children[0].children[0].children[0].children[0].children[0].innerHTML = '~ ' + current_user_act + ' ~';
                        $('#player-' + user_pos)[0].children[0].children[0].children[0].children[0].children[0].className = "status " + current_user_act;
                    }
                }
            })
        }

        if (data['move']) {
            stop_timer_fake();
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
                    else {
                        start_timer_fake();
                    }
                    $('#player-' + user_pos)
                    .css('background', 'linear-gradient(0deg, rgba(255,255,255,1), rgba(255,255,255,0))');
                }
            })
        }

        if (data['desk_cards']) {
            for (i = 0; i < data['desk_cards'].length; i++) {
                card = poker_string(data['desk_cards'][i]);
                set_poker('desk-' + i, card);
            }
        }

        if (data['winner']) {
            user_cards = data['cards'];
            winner_pos = data['winner_pos'];
            winner_name = data['winner'];
            winner_type = data['type'];
            winner_cards = data['win_cards'];
            $('#start_game')[0].disabled = false;

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

                                card = poker_string(parseInt(pokers[0]));
                                set_poker('card-' + pos + '-1', card);

                                card = poker_string(parseInt(pokers[1]));
                                set_poker('card-' + pos + '-2', card);
                            }
                        }
                    }

                    content = "Winner is";
                    for (j = 0; j < winner_pos.length; j++){
                        winner_pos_j = parseInt(winner_pos[j]) - parseInt(login_user_pos);

                        if (winner_pos_j < 0) winner_pos_j += 9;

                        if (user_cards && winner_cards[0]) {
                            for (i = 0; i < winner_cards[0].length; i++) {
                                if (winner_cards[0][i] < 5) {
                                    $('#desk-' + (winner_cards[0][i])).css('background-color', 'rgba(254,238,117,1)');
                                }
                                else {
                                    $('#card-' + winner_pos_j + '-' + (winner_cards[0][i] - 4)).css('background-color', 'rgba(253,252,202,1)');
                                }
                            }
                        }

                        $('#player-' + winner_pos_j)
                        .css(
                            'background',
                            'linear-gradient(0deg, rgba(254,238,117,0.5), rgba(253,252,202,0))');

                        content += " " + winner_name;
                    }

                    content += "! " + winner_type.toUpperCase();
                    $('#message').html(content);
                }
            })
        }

        if (data['active_players']) {
            player_list = data['active_players'];
            if (player_list.length == 1) {
                $('#player-0')[0].children[0].children[0].children[0].children[0].children[0].innerHTML = '';
                $('#player-0')[0].children[0].children[0].children[0].children[0].children[1].innerHTML = '';
                for (i = 1; i < 9; i++) {
                    $('#player-' + i)[0].children[0].children[0].children[0].children[0].children[0].innerHTML = '';
                    $('#player-' + i)[0].children[0].children[0].children[0].children[0].children[1].innerHTML = '';
                }

                for (i = 0; i < 9; i++) {
                    $('#chips-' + i + '-2').html("Betting: 0");
                }

                for (i = 0; i < 5; i++) {
                    $('#desk-' + i).css('background', 'rgba(255,255,255,1)');
                }
                for (i = 0; i < 9; i++) {
                    $('#card-' + i + '-1').css('background', 'rgba(255,255,255,1)');
                    $('#card-' + i + '-2').css('background', 'rgba(255,255,255,1)');
                }
            }
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
            $('#chips-0-1').html('Total chips: ' + data['cur_user_chips']);
            $('#chips-0-2').html('Betting: 0');

            $('#player-0')[0].children[0].children[0].children[0].children[0].children[1].innerHTML = '';
            $('#player-0')[0].children[0].children[0].children[0].children[0].children[0].innerHTML = '';
            $('#player-0').css('background', 'rgba(255,255,255,0)');
            $('#message').html('Waiting for more players');
            $('#chips').html('<br>');
        }

        if (data['get_out']) {
            window.location.replace('goto_lobby');
        }


    };
});
