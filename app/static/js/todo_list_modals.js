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
    document.getElementsByName('open-edit-btn').forEach(function(entry) {
        entry.addEventListener('click', openEditModal);
    });

    document.getElementById('edit-modal-delete').addEventListener(
        'click', deleteModal);
});

function openEditModal(event){
    const modal = document.getElementById('edit-modal');
    console.log(event);
    const button = event.target;
    const taskId = button.getAttribute('data-bs-task-id');
    const taskTime = button.getAttribute('data-bs-time');
    const taskTitle = button.getAttribute('data-bs-title');
    const taskDescription = button.getAttribute('data-bs-description');
    const taskImportant = button.getAttribute('data-bs-important');
    console.log(taskImportant);


    document.getElementById('edit-task-id').value = taskId;
    document.getElementById('customer-time2').value = taskTime;
    console.log(taskTime);
    document.getElementById('customer-title2').value = taskTitle;
    document.getElementById('customer-descrip2').value = taskDescription;
    document.getElementById('is-important2').checked = taskImportant;
}


function deleteModal() {
    const taskId = document.getElementById('edit-task-id').value;
    document.getElementById('delete-task-id').value = taskId;
    document.getElementById('delete-task-form').submit();
}