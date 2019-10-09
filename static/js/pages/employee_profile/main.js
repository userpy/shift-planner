



var DETAIL_PAGE_PREFIX = '/'
if(request_page_party == 'client') {
	DETAIL_PAGE_PREFIX = '/'
}
if(request_page_party == 'agency') {
	DETAIL_PAGE_PREFIX = '/'
}
if(request_page_party == 'promo') {
	DETAIL_PAGE_PREFIX = '/promo-'
}

$('body').on('orgunits:loaded', function() {
	if (request_page_party == 'agency' || request_page_party == 'promo' || request_page_party == 'broker'){
		if (employee_id)
			$('#agency_id_jobs').attr('value', orgSelect.selectedUnit.id)
			else
			$('#agency_id').html("<option value='" + orgSelect.selectedUnit.id + "' selected>" + orgSelect.selectedUnit.name + "</option>");
	}
})
$('#jobs_list').select2();

if (!employee_id)
	$('#agency_id').select2();


// Оповвещение об ошибках во время сохранения/изменения сотрудника
var alerter = $('#error_alert');

// Обработчики событий
$('#reset_button').on('click', function(){
	window.location.href = DETAIL_PAGE_PREFIX + 'employees-list'
});



// Кнопка сохранения сотрудника
$('#submit_button').on('click', function(e){
	e.preventDefault();
	if(! checkFormRequirments(ae$('#create-employee-form')) )return
	blockForm($('#create-employee-form'))
	var emp_form_data = {
		csrfmiddlewaretoken: csrf_token,
		orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null},
		agency_id: employee_id ? $('#agency_id').val() : orgSelect.selectedUnit.id,
		number: $('#number').val(),
		surname: $('#surname').val(),
		firstname: $('#firstname').val(),
		patronymic: $('#patronymic').val(),
		gender: $('#gender input:radio:checked').val(),
		date_of_birth: $('#date_of_birth').data('datepicker').getFormattedDate('yyyy-mm-dd'),
		place_of_birth: $('#place_of_birth').val(),
		receipt: $('#receipt').data('datepicker').getFormattedDate('yyyy-mm-dd'),
	};
	if (employee_id){
		emp_form_data.agency_employee_id = employee_id
		emp_form_data.dismissal = $('#dismissal').data('datepicker').getFormattedDate('yyyy-mm-dd')
	}

	OutRequests['set-employee']({
		data: emp_form_data,
		success: function(response) {
			unblockForm($('#create-employee-form'))
			for (var key in response.responseJSON){
				$('#' + key + '-help' ).hide();
				$('#' + key + '-help' ).text('');
				$('#' + key + '-help' ).removeClass('text-danger');
			}
			alerter.hide();
			if (employee_id){
				window.location.href = DETAIL_PAGE_PREFIX + "employee/"+ employee_id;
			} else {
				window.location.href = DETAIL_PAGE_PREFIX + "employee/" + response['id'];
			}
		},
		error: function(response){
			unblockForm($('#create-employee-form'))
			resp = response.responseJSON;
			$('.m-form__help').hide();
			for (var key in resp){
				$('#' + key + '-help' ).show();
				$('#' + key + '-help' ).text('* ' + resp[key][0]);
				$('#' + key + '-help' ).addClass('text-danger');
				if(key == "non_field_errors"){
					alerter.html(resp[key][0]);
					alerter.show();
				}
			}
		}
	})
});




// Функции
function find_job_history_by_id(index){
	var result = 0;
	JOBS.forEach(function(job){
		if (job.id === index){
			result = job;
			return;
		}
	});
	return result;
}
function find_doc_by_id(index){
	var result = 0;
	DOCS.forEach(function(doc){
		if (doc.id === index){
			result = doc;
			return;
		}
	});
	return result;
}


// Обработчик событий в таблице назначения должностей (функций)
$('#jobs_datatable_table').on('m-datatable--on-layout-updated', function () {

	// Обработка нажатия на иконку редактирования сотрудника в таблице должностей
	$('.jobs_edit').on('click', function(e){
		// Инициализация интерфейса модального окна
		$('#add_job').hide();
		$('#edit_job').show();
		$('#modal_job').modal({backdrop: true});

		JOB_HISTORY_ID_SELECTED = parseInt($(this).attr('job_his_id'));
		var jh = find_job_history_by_id(JOB_HISTORY_ID_SELECTED);
		job_id = $(this).attr('job_id');
		// Для активации отправки поля с job_history_id
		$('.modal_jobs_for_adding').prop("disabled", true);
		$('.modal_jobs_for_editing').prop("disabled", false);
		$('#jobs_list').val(job_id);

		$('#jobs_list').trigger('change')
		// Установка дат
		$('#job_start').datepicker('setDate', null)
		$('#job_end').datepicker('setDate', null)
		$('#job_start').datepicker('setDate', jh.start.replace(/(\d+)[-](\d+)[-](\d+)/, '$3.$2.$1'));
		if (jh.end != null) $('#job_end').datepicker('setDate', jh.end.replace(/(\d+)[-](\d+)[-](\d+)/, '$3.$2.$1'));
	});

	// Обработка нажатия на иконку удаления сотрудника в таблице должностей
	$('.jobs_remove').on('click', function(e){
		JOB_HISTORY_ID_SELECTED = parseInt($(this).attr('job_his_id'));
		$('#modal_job_delete').modal({backdrop: true});
		$('#modal_form_delete_job_history_id').attr('value', JOB_HISTORY_ID_SELECTED);
	});
});
// Обработчик событий в таблице назначения документов
showDocPp = function(DOC_ID_SELECTED){
	var doc_id = +DOC_ID_SELECTED
	// Инициализация интерфейса модального окна
	$('.docs.modal-controls--default').show()
	$('.docs.modal-controls--confirm').hide()

	$('#add_doc').hide();
	$('#edit_doc').show();
	$('#modal_doc').modal({backdrop: true});
	$('#docs_modal_title').textContent = 'Редактирование документа'
	$('#add_doc_button').hide()
	$('.docs.modal-controls--confirm').hide()
	$('#doc_delete_button').show()

	$('#edit_doc').css({visibility: 'visible'})
	var doc = find_doc_by_id(doc_id)
	if(is_verme_docs_enabled){
		duVM.isCreatingDoc = false
		resetDocUploader()
		loadDocData({
			doc_id: doc_id,
		})
	}
	// Для активации отправки поля с doc_id
	$('.modal_docs_for_adding').prop("disabled", true);
	$('.modal_docs_for_editing').prop("disabled", false);
	$('#doc_types_list').val(doc.doc_type.id);
	$('#doc_types_list').trigger('change')
	//текст
	$('#doc_text').val(doc.text)
	// Установка дат
	$('#doc_start').datepicker('setDate', doc.start.replace(/(\d+)[-](\d+)[-](\d+)/, '$3.$2.$1'));
	if (doc.end != null) $('#doc_end').datepicker('setDate', doc.end.replace(/(\d+)[-](\d+)[-](\d+)/, '$3.$2.$1'));
}
removeDocFromPp = function(DOC_ID_SELECTED){
	var data = {
		csrfmiddlewaretoken: csrf_token,
		doc_ids: JSON.stringify([DOC_ID_SELECTED]),
	};
	blockModalForm()
	OutRequests['delete-employee-doc']({
		data: data,
		success: function() {
			unblockModalForm()
			refresh_employee_data();
			$('#modal_doc').modal('hide');
			docs_datatable.reload();
		},
		error: function(response){
			unblockModalForm()
			handleServerErrorInModal(response)
		}
	})
}



var EP_INITED_TABS = new Map();
EP_INITED_TABS.set('main_tab', function(){})


$('#jobs_tab').on('click', function(){
	$('#main_tab').off('click');
	init_jobs_datatable();
});

$('#docs_tab').on('click', function(){
	$('#main_tab').off('click');
	init_docs_datatable();
});

$('#organizations_tab').on('click', function(){
	$('#organizations_tab').off('click');
	init_organizations_datatable();
});

$('#events_tab').on('click', function(){
	$('#events_tab').off('click');
	init_events_datatable();
});
$('#transitions_tab').on('click', function(){
	$('#transitions_tab').off('click');
	init_transitions_datatable();
});

// нельзя создавать сотрудника, когда выбран хедквотер
$('body').on('orgunits:loaded orgunits:change', function(){
	if(orgSelect.selectedUnit.isHeadquater){
		$('.agency-needed-error').show()
		$('#submit_button').hide()
	}else{
		$('.agency-needed-error').hide()
		if($('#reset_button')[0].style.display != 'none') $('#submit_button').show()// если активно редактирование
	}
})

$('body').on('orgunits:loaded orgunits:change', function(){
	if( !orgSelect.selectedUnit.isHeadquater ){
		showElViaCSS($('#hire_to_organization_employee_button'))
		showElViaCSS($('#nav_create_employee'))
		showElViaCSS($('#nav_hire_outsourcer'))
	}else{
		hideElViaCSS($('#hire_to_organization_employee_button'))
		hideElViaCSS($('#nav_create_employee'))
		hideElViaCSS($('#nav_hire_outsourcer'))
	}
})

// скрываем меню действий для создания сотрудника
if(!!~location.href.indexOf('create-employee')){
	$("#actions").hide();
}