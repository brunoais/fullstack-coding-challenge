$(document).ready(function(){
    var socket = io() //.connect('http://' + document.domain + ':' + location.port + '/');
    socket.on('my response', function(msg) {
        console.log("response got", msg);
        $('#log').append('<p>Received: ' + msg.data + '</p>');
    });
    $('form#emit').submit(function(event) {
        socket.emit('my event', {data: $('#emit_data').val()});
        event.preventDefault()
        return false;
    });
//    $('form#broadcast').submit(function(event) {
//        socket.emit('my broadcast event', {data: $('#broadcast_data').val()});
//        event.preventDefault()
//        return false;
//    });
});