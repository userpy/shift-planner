// Очистка модальной формы
function clearModalForm(){
	$("#claim_id").val('');
	$("#claim_message_text").val('');
	$("#claim_user_name").val('');
	$("#file-form")[0].dropzone.removeAllFiles(true);
	$("#modal_create_message_form_msg").addClass('.m--hide').hide();
	fileform = [];

	// Модальное окно отклонения претензии
	$("#reject_claim_id").val('');
	$("#reject_claim_message_text").val('');
	$("#reject_claim_user_name").val('');

}

// Сообщение к претензии
function messageClaim(claim_id){
	var message_modal = $('#modal_create_message');

	// Очистка сообщения и файлов, если они были
	clearModalForm();

	$("#claim_id").val(claim_id);
	$("#claim_user_name").val(request_user.getFullName());

	message_modal.modal('toggle');

}

// Комментарий к отклонению претензии
function commentClaimReject(claim_id){
	var comment_modal = $('#modal_comment_claim_reject');

	// Очистка сообщения и файлов, если они были
	clearModalForm();

	$("#reject_claim_id").val(claim_id);
	$("#reject_claim_user_name").val(request_user.getFullName());

	comment_modal.modal('toggle');

}

// Отправка формы сообщения + файлов
function sendFormData()
{
	var message_modal = $('#modal_create_message');

	var claim_id = $("#claim_id");
	var claim_message = $("#claim_message_text");
	var claim_user_name = $("#claim_user_name");


	var data = {
		claim_id: claim_id.val(),
		user_name: claim_user_name.val(),
		text: claim_message.val(),
		party: request_page_party,
		csrfmiddlewaretoken: csrf_token
	};

	var dropzoneForm = $('#file-form')[0];
	// Если были загружены файлы
	if (dropzoneForm.dropzone.files.length > 0){
		// И хотя бы один из них не прошел валидацию по размеру
		if (dropzoneForm.dropzone.getRejectedFiles().length){
			// Отображаем ошибку
			var i = $("#modal_create_message_form_msg");
			i.removeClass("m--hide").show(),
				mApp.scrollTo(i, -200)
			return
		}
	}
	blockModalForm()
	$.ajax({
		type: 'POST',
		url: '/api-create-claim-message/?format=json',
		data: data,
		success: function (data) {
			unblockModalForm()
			// Если успешно отправили сообщение
			// То отправляем вложенные файлы, если они есть

			if (fileform.length > 0){
				fileform.forEach(function(item) {
					$.ajax({
						type: 'POST',
						url: '/api-create-claim-attachment/?format=json',
						data: {
							message_id: data['id'],
							filename: item.filename,
							file: item.data.split(',')[1],
							csrfmiddlewaretoken: csrf_token
						},
						success: function (data) {
						}
					});

				});
				// Очищаем форму, спискок файлов в dropzone
				// И закрывваем модальное окно
				message_modal.modal('toggle');
				clearModalForm();
			}else{

				// Очищаем форму
				// И закрывваем модальное окно
				message_modal.modal('toggle');
				clearModalForm();
			}
			// Перезагрузка таблицы с сообщениями, если она инициализирвоана
			try{
				$("#datatable_claim_messages").mDatatable().reload();
			}catch (e){
				//
			}
		},
		error: function(response){
			unblockModalForm()
			handleServerErrorInModal(response)
			// Вывод ошибок сервера
			var i = $("#modal_create_message_form_msg");
			i.removeClass("m--hide").show(),
				mApp.scrollTo(i, -200)
		}
	});
}
