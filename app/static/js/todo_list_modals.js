//function openEditModal(taskId, taskTime, taskTitle, taskDescription, taskImportant){
//    $('#list-modal').modal('toggle');
//    $('#edit-task-id').val(taskId);
//    $('#customer-time2').val(taskTime);
//    $('#customer-title2').val(taskTitle);
//    $('#customer-descrip2').val(taskDescription);
//    $('#is-important2').prop('checked', taskImportant);
//    $('#edit-modal').modal('toggle');
//}

window.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('open-edit').addEventListener('click', openEditModal);
});

function openEditModal(){
    alert("GUY HAGEVER")
    var modal = document.getElementById('edit-modal')
    modal.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget
        var taskId = button.getAttribute('data-bs-task-id')
        var taskTime = button.getAttribute('data-bs-time')
        var taskTitle = button.getAttribute('data-bs-title')
        var taskDescription = button.getAttribute('data-bs-description')
        var taskImportant = button.getAttribute('data-bs-important')
        var modalTitleInput = exampleModal.querySelector('#customer-title2')
        modalTitleInput.value = taskTitle
    })
//    document.getElementById('edit-modal').addEventListener('show.bs.modal' ,function (event) {
//        document.getElementById('edit-task-id').value = taskId;
//        document.getElementById('customer-time2').value = taskTime;
//        document.getElementById('customer-title2').value = taskTitle;
//        document.getElementById('customer-descrip2').value = taskDescription;
//        document.getElementById('is-important2').checked = taskImportant
//    })

}


function deleteModal() {
    var taskId = $('#edit-task-id').val();
    $('#delete-task-id').val(taskId);
    $('#delete-task-form').submit();
}