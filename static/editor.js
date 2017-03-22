$(document).ready(() => {

    let editor = ace.edit('editor');
    let editorTwo = ace.edit('editorTwo');
    let socket = io.connect('http://127.0.0.1:5000/algoview');

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

    socket.on('editor', (data)=>{
        data = data.replace(/'/g, '"')
        let x = JSON.parse(data)
        editorTwo.setValue(x.data);
    });

    editor.getSession().setMode('ace/mode/javascript');
    editorTwo.getSession().setMode('ace/mode/javascript');

    $('#submitButton').click(() => {
        console.log(editor.getValue());
    });
});
