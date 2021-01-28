$(document).ready(function () {
    $('#summernote').summernote({
        codeviewFilter: false,
        codeviewIframeFilter: true,
        height: 100,
        toolbar: [
            ['fontname', ['fontname']],
            ['fontsize', ['fontsize']],
            ['style', ['style']],
            ['font', ['bold', 'italic', 'underline', 'strikethrough', 'superscript', 'subscript', 'clear']],
            ['color', ['color']],
            ['para', ['ol', 'ul', 'paragraph', 'height']],
            ['table', ['table']],
            ['insert', ['link']],
            ['view', ['undo', 'redo', 'fullscreen', 'codeview']]
        ]
    });
});