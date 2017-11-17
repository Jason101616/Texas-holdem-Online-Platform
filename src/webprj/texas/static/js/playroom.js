var timer = 10;
function timer_10sec() {
    if (timer >= 0) {
        var time_str = '0' + timer;
        timer--;
        time_str = time_str.substring(time_str.length - 2, time_str.length)
        $('#message').html('00:' + time_str);
        setTimeout(timer_10sec, 1000);
    }
    else{
        timer = 10;
        $('#message').html('timeout!');
        socket = new WebSocket("ws://" + window.location.host + "/chat/");
        if (socket.readyState === WebSocket.OPEN) {
            socket.onopen();
        }
        socket.send("timeout");
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

  $('#get_card').on('click', function (event) {
        event.preventDefault(); // Prevent form from being submitted
        var message = {
            message: 'click get_card'
        };
        socket.send(JSON.stringify(message));
    });

  $('#game_hold').on('click', function (event) {
        event.preventDefault(); // Prevent form from being submitted
        var message = {
            message: 'click game_hold'
        };
        socket.send(JSON.stringify(message));
    });

  $('#game_fold').on('click', function (event) {
        event.preventDefault(); // Prevent form from being submitted
        var message = {
            message: 'click game_fold'
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

  socket.onmessage = function (message) {
    console.log(message.data);
    var data = JSON.parse(message.data)
    if (message.data['new_player']){
        console.log('1')
        return
    }

    if (data.card){
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
    } else if (data.status === 'hold') {
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
    } else if (data.status === 'fold') {
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