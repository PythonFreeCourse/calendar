function openEditModal(taskId, taskTime, taskTitle, taskDescription, taskImportant){
    document.getElementById('modal').addEventListener('show.bs.modal', function (event) {
        document.getElementById('edit-task-id').value = taskId;
        document.getElementById('customer-time2').value = taskTime;
        document.getElementById('customer-title2').value = taskTitle;
        document.getElementById('customer-descrip2').value = taskDescription;
        document.getElementById('is-important2').checked = taskImportant
        document.getElementById('edit-modal').addEventListener('show.bs.modal' ,function (event) {

        }
    }

}

function deleteModal() {
    var taskId = $('#edit-task-id').val();
    $('#delete-task-id').val(taskId);
    $('#delete-task-form').submit();
}