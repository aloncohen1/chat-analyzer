document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('file-upload-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        var formData = new FormData(form);
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/', true);
        xhr.onload = function() {
            if (xhr.status === 200) {
                document.getElementById('response').textContent = xhr.responseText;
            }
        };
        xhr.send(formData);
    });
});