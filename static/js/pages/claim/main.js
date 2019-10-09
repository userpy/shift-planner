


// Очистка формы
function clearForm(){
	$("#agency_select").val('').trigger('change');
	$("#organization_select").val('').trigger('change');
	$("#type_select").val('').trigger('change');
	$("#claim_message").val('');
	$("#file-form")[0].dropzone.removeAllFiles(true);
	fileform = [];
}

// Получение претензии и установка полей
function getClaim(){
	$.ajax({
		type: 'GET',
		url: '/api-get-claim/?format=json',
		cache: false,
		data: {
			claim_id: claim_id
		},
		success: function (data) {
			//$("#type_select").val(data['claim_type']['id']).trigger('change');
			//$("#agency_select").val(data['agency']['id']).trigger('change');
			//$("#organization_select").val(data['organization']['id']).trigger('change');
			//$("#claim_message").val(data['text']);
			document.getElementById("claim_city").innerText = data['organization']['parent']['name'];
			document.getElementById("claim_agency").innerText = data['agency']['name'];
			document.getElementById("claim_organization").innerText = data['organization']['name'];
			document.getElementById("claim_type").innerText = data['claim_type']['name'];
			document.getElementById("claim_message").innerText = data['text'];
			document.getElementById("claim-data").innerText = '№ ' + data['headquater']['prefix'] + data['number'] + ' от ' + valueToCell(data, {type: 'dt_created_full'})
			document.getElementById("claim-data").innerHTML += '<br /><br />' + data['status']['name'] + ' ' + valueToCell(data, {type: 'dt_status_changed'})
			// Новые статусы

			if (data['status']['code'] == 'wait'){
				$("#nav_accept_claim").show();
				$("#nav_reject_claim").show();
				$("#nav_close_claim").hide();
				$("#nav_reopen_claim").hide();
				$("#nav_add_message").show();
				$("#claim_add_message").show();
			} else if (data['status']['code'] == 'accept'){
				$("#nav_accept_claim").hide();
				$("#nav_reject_claim").hide();
				$("#nav_reopen_claim").hide();
				$("#claim_add_message").show();
				$("#nav_add_message").show();
				$("#nav_close_claim").show();
			} else if (data['status']['code'] == 'reject'){
				$("#nav_accept_claim").hide();
				$("#nav_reject_claim").hide();
				$("#claim_add_message").hide();
				$("#nav_add_message").hide();
				$("#nav_close_claim").show();
				$("#nav_reopen_claim").show();
			} else {
				$("#nav_accept_claim").hide();
				$("#nav_reject_claim").hide();
				$("#nav_close_claim").hide();
				$("#nav_reopen_claim").hide();
				$("#claim_add_message").hide();
				$("#nav_add_message").hide();
				$(".m-dropdown.page-actions").hide()
			}

			//

			if (data['attachments'] && data['attachments'].length > 0) {
				var files = '';
				data['attachments'].forEach(function (item) {
					files += '<div class="dz-preview dz-file-preview dz-complete">' + '<a href="' + item['attachment'] + '" title="'+ item['filename'] + '">' + '<i class="fa fa-file-alt" style="font-size: 4rem !important;"></i><br />' + item['filename'] + '</a></div>';

				});
				document.getElementById("claim-files").innerHTML = files;
			}
			//getClaimFiles();
		}
	});
}

// Закрытие претензии
function closeClaim(claim_id){
	$.ajax({
		type: 'POST',
		url: '/api-close-claim/?format=json',
		data: {
			claim_id: claim_id,
			csrfmiddlewaretoken: csrf_token
		},
		success: function (data) {
			getClaim(claim_id);
		}
	});
}

// Переоткрытие претензии
function reopenClaim(claim_id){
	$.ajax({
		type: 'POST',
		url: '/api-reopen-claim/?format=json',
		data: {
			claim_id: claim_id,
			csrfmiddlewaretoken: csrf_token
		},
		success: function (data) {
			getClaim(claim_id);
		}
	});
}

// Действие по претензии
function actionClaim(claim_id, action, comment){
	var data = {
		claim_id: claim_id,
		action: action,
		csrfmiddlewaretoken: csrf_token
	};

	if (comment !== ''){
		data['comment'] = comment
	};

	$.ajax({
		type: 'POST',
		url: '/api-set-claim-action/?format=json',
		data: data,
		success: function (data) {
			getClaim(claim_id);
			// Перезагрузка таблицы с сообщениями/историей действий, если она инициализирвоана
			try{
				$("#datatable_claim_messages").mDatatable().reload();
			}catch (e){
				//
			}
		}
	});
}

// <!-- Обработчики событий -->
$('.m-form__actions #reset').on('click', function(e){
	e.preventDefault()
	window.location.href = "/hq-claims-list/";
})

$('#messages_tab').on('click', function(){
	init_messages_datatable();

});

$('#files_tab').on('click', function(){
	init_files_datatable();
});



// <!-- / Обработчики событий -->


// нельзя создавать претензию, когда выбран НЕ хедквотер
$('body').on('orgunits:loaded orgunits:change', function(){
	if( !orgSelect.selectedUnit.isHeadquater ){
		$('.hq-needed-error').show()
		$('#submit_button').hide()
	}else{
		$('.hq-needed-error').hide()
		$('#submit_button').show()
	}
})