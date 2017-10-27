/**
 * Created by Nausicaasnow on 2017/10/27.
 */

$(document).ready(function() {
    console.log('hello world!');
    // Create a new WebSocket
    ws = new WebSocket("ws://" + window.location.host + "/test/");
    // Make it show an alert when a message is received
    ws.onmessage = function(message) {
        console.log(message.data + 'hi!');
    }
    // Send a new message when the WebSocket opens
    ws.onopen = function() {
        ws.send('Hello, world');
    }
    if (ws.readyState == WebSocket.OPEN) ws.onopen();
    console.log('ws finished!');
});

