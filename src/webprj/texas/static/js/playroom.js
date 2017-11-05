$(document).ready(function() {
    console.log(window.location.pathname);
    console.log(window.location.host);
    socket = new WebSocket("ws://" + window.location.host + "/chat/");

    // socket.onopen = function() {
    //     socket.send("have opened");
    // };
    // Call onopen directly if socket is already open
    if (socket.readyState === WebSocket.OPEN) socket.onopen();

    $('#get_card').on('click', function(event) {
        event.preventDefault(); // Prevent form from being submitted
        // console.log("click get_card btn");
        // socket.send("click get_card btn");
        var message = {
            message: 'click get_card'
        };
        socket.send(JSON.stringify(message));
    });

    $('#game_hold').on('click', function(event) {
        event.preventDefault(); // Prevent form from being submitted
        // console.log("click get_card btn");
        // socket.send("click get_card btn");
        var message = {
            message: 'click game_hold'
        };
        socket.send(JSON.stringify(message));
    });

    socket.onmessage = function(message) {
        console.log(message);
      // var data = JSON.parse(message.data);
      //   var chat = $("#chat")
      //   var ele = $('<tr></tr>')
      //
      //   ele.append(
      //       $("<td></td>").text(data.timestamp)
      //   )
      //   ele.append(
      //       $("<td></td>").text(data.handle)
      //   )
      //   ele.append(
      //       $("<td></td>").text(data.message)
      //   )
      //
      //   chat.append(ele)
    };
});
