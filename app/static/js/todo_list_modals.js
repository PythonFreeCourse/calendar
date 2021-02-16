function openEditModal(taskId, taskTime, taskTitle, taskDescription, taskImportant){
    $('#Modal').modal("toggle");
    $('#editTaskId').val(taskId);
    $('#customerTime2').val(taskTime);
    $('#customerTitle2').val(taskTitle);
    $('#customerDescrip2').val(taskDescription);
    $('#isImportant2').prop('checked', taskImportant);
    $('#editModal').modal("toggle");
}

function deleteModal() {
    var taskId = $('#editTaskId').val();
    $('#deleteTaskId').val(taskId);
    $('#deleteTaskForm').submit();
}