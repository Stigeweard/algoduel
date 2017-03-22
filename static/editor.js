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
        data = data.replace(/'/g, '"')
        let x = JSON.parse(data)
        editorTwo.setValue(x.data);
    });

    editor.getSession().setMode('ace/mode/javascript');
    editorTwo.getSession().setMode('ace/mode/javascript');

    $('#submitButton').click(() => {
        console.log(editor.getValue());
    });

    function leave_room() {
        socket.emit('left', {}, function() {
            socket.disconnect();
            // go back to the login page
            window.location.href = "{{ url_for('main.index') }}";
        });
    }
});
