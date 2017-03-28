$(document).ready(() => {

    let editor = ace.edit('editor');
    let editorTwo = ace.edit('editorTwo');
    let socket = io.connect('http://' + document.domain + ':' + location.port + '/algoview');
    socket.on('connect', () => {
        socket.send('user connected')
        socket.emit('join', {
            data: 'wow'
        });
    })
    editor.setTheme('ace/theme/monokai');
    editorTwo.setTheme('ace/theme/monokai');
    editorTwo.setReadOnly(true);

    editor.getSession().on('change', function(e) {
        if (e.action === 'insert' || e.action === 'remove') {
            socket.emit('editor', {
                data: editor.getValue()
            });
            console.log('emitted data! ' + editor.getValue());
        }
    });

    socket.on('message', (data)=>{
        console.log(data);
    })

    socket.on('editor', (data) => {
        // TODO: MAKE STRINGS WORK
        data = data.replace(/'/g, '"');
        let x = JSON.parse(data);
        editorTwo.setValue(x.data);
    });

    socket.on('worked', (data)=>{
        $('#status').removeClass('alert-danger');
        $('#status').addClass('alert-success');
        $('#attempt').text(data.message);
        $('#error').text('');
        editor.setReadOnly(true);
    })

    socket.on('incorrect', (data)=>{
        $('#status').addClass('alert-danger');
        $('#attempt').text(data.message);
        $('#error').text(data.error);
    })

    editor.getSession().setMode('ace/mode/python');
    editorTwo.getSession().setMode('ace/mode/python');

    $('#submitButton').click(() => {
        console.log(editor.getValue());
        socket.emit('submission',{
            data: editor.getValue(),
            username: $('#username').text()
        })
    });

    $('#logout').click(leave_room);

    function leave_room() {
        socket.emit('left', {}, function() {
            socket.disconnect();
            // go back to the login page
            console.log('left room');
            window.location.href = "{{ url_for('main.index') }}";
        });
    }
});
