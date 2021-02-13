let timerInterval;
const {colorSyntax} = toastui.Editor.plugin;
const editor = new toastui.Editor({
  el: document.querySelector('#editorSection'),
  initialEditType: 'wysiwyg',
  previewStyle: 'vertical',
  height: 'auto',
  plugins: [colorSyntax],
  useDefaultHTMLSanitizer: true,
  toolbarItems: [
    'heading',
    'bold',
    'italic',
    'strike',
    'divider',
    'hr',
    'quote',
    'divider',
    'ul',
    'ol',
    'task',
    'indent',
    'outdent',
    'divider',
    'table',
    'link',
    'divider',
    'code',
    'codeblock'
  ]

});
document.getElementById("but").addEventListener("click", function () {
  fetch(`${window.origin}`, {
    method: "POST",
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({"datahtml": editor.getHtml(), 'datamd': editor.getMarkdown()})
  }).then(response => {
    if (editor.getMarkdown().length >= 1)
      Swal.fire({
        title: 'Working on it!',
        html: 'Data is being transfered to the server!',
        timer: 1000,
        timerProgressBar: true,
        didOpen: () => {
          Swal.showLoading()
          timerInterval = setInterval(() => {
            const content = Swal.getContent()
          }, 1)
        },
        willClose: () => {
          clearInterval(timerInterval)
        }
      })
  });


});