// Если редактирование сотрудника

// Нажатие на кнопку "Добавить функцию"
$('#modal_add_job_open').on('click', function(){
	$('.modal_jobs_for_adding').prop("disabled", false);
	$('.modal_jobs_for_editing').prop("disabled", true);
	$('#add_job').show();
	$('#edit_job').hide();
	$('#modal_job').modal({backdrop: true});
});

// Нажатия на кнопку "Добавить" в модальном окне создания должности
$('#add_job').on('click', function(e){
	if(! checkFormRequirments(ae$('#modal_job')) )return
	var data = {
		csrfmiddlewaretoken: csrf_token,
		job_id: $('#jobs_list').val(),
		start: $('#job_start').data('datepicker').getFormattedDate('yyyy-mm-dd'),
		end: $('#job_end').data('datepicker').getFormattedDate('yyyy-mm-dd'),
		agency_employee_id: employee_id,
		agency_employee_id: employee_id ,
		orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null},
	};
	blockModalForm()
	OutRequests['set-job-history']({
		data: data,
		success: function(response) {
			unblockModalForm()
			refresh_employee_data();
			jobs_datatable.reload();
			$('#modal_job').modal('hide');
		},
		error: function(response){
			unblockModalForm()
			handleServerErrorInModal(response)
		}
	})
	
});

// Нажатия на кнопку "Редактировать должность" в модальном окне редактирования должности
$('#edit_job').on('click', function(e){
	if(! checkFormRequirments(ae$('#modal_job')) )return
	var data = {
		csrfmiddlewaretoken: csrf_token,
		job_history_id:	JOB_HISTORY_ID_SELECTED,
		job_id: $('#jobs_list').val(),
		start: $('#job_start').data('datepicker').getFormattedDate('yyyy-mm-dd'),
		end: $('#job_end').data('datepicker').getFormattedDate('yyyy-mm-dd'),
		agency_employee_id: employee_id,
		agency_employee_id: employee_id,
	};
	blockModalForm()
	OutRequests['set-job-history']({
		data: data,
		success: function(response) {
			unblockModalForm()
			refresh_employee_data();
			$('#modal_job').modal('hide');
			jobs_datatable.reload();
		},
		error: function(response){
			unblockModalForm()
			handleServerErrorInModal(response)
		}
	})
});

$('#modal_job_delete_button').on('click', function(){
	var data = {
		csrfmiddlewaretoken: csrf_token,
		job_history_ids:	JSON.stringify([JOB_HISTORY_ID_SELECTED]),
	};
	blockModalForm()
	OutRequests['delete-job-history']({
		data: data,
		success: function() {
			unblockModalForm()
			refresh_employee_data();
			$('#modal_job_delete').modal('hide');
			jobs_datatable.reload();
		},
		error: function(response){
			unblockModalForm()
			handleServerErrorInModal(response)
		}
	})
});

// Нажатие на кнопку "Добавить документ"
$('#modal_add_doc_open').on('click', function(){
	$('#add_doc').show();
	$('#edit_doc').hide();
	$('#modal_doc').modal({backdrop: true});
	if(is_verme_docs_enabled){
		duVM.isCreatingDoc =true
		resetDocUploader()
	}
	$('#docs_modal_title').textContent = 'Добавление документа'
	$('#add_doc_button').css({visibility: 'visible'})
	$('#edit_doc').css({visibility: 'hidden'})
	$('#doc_text').val('')
	$('#doc_start').datepicker( "setDate", new Date())
	$('#doc_end').datepicker( "setDate", null)

	$('#doc_delete_button').hide()
	$('.docs.modal-controls--confirm').hide()
	$('.docs.modal-controls--default').show()
	$('#add_doc_button').show()
});
// Нажатия на кнопку "Добавить" в модальном окне создания документа
$('#add_doc_button').on('click', function(e){
	var data = {
		csrfmiddlewaretoken: csrf_token,
		doc_type_id: $('#doc_types_list').val(),
		start: $('#doc_start').data('datepicker').getFormattedDate('yyyy-mm-dd'),
		end: $('#doc_end').data('datepicker').getFormattedDate('yyyy-mm-dd'),
		agency_employee_id: employee_id ,
		orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null},
		text: $('#doc_text').val()
	};
	blockModalForm()
	OutRequests['set-employee-doc']({
		data: data,
		success: function(response) {
			refresh_employee_data();
			docs_datatable.reload();
			if(is_verme_docs_enabled){
				updateDocUploaderWithReqParams(response)
				uploadDocs()
				return
			}else{
				unblockModalForm()
				$('#modal_doc').modal('hide');
			}
		},
		error: function(response){
			unblockModalForm()
			handleServerErrorInModal(response)
		}
	})
});
// Нажатия на кнопку "Редактировать документ" в модальном окне редактирования должности
$('#edit_doc').on('click', function(e){
	if(! checkFormRequirments(ae$('#modal_doc')) )return
	var data = {
		csrfmiddlewaretoken: csrf_token,
		doc_id:	DOC_ID_SELECTED,
		doc_type_id: $('#doc_types_list').val(),
		start: $('#doc_start').data('datepicker').getFormattedDate('yyyy-mm-dd'),
		end: $('#doc_end').data('datepicker').getFormattedDate('yyyy-mm-dd'),
		agency_employee_id: employee_id,
		text: $('#doc_text').val()
	};
	blockModalForm()
	OutRequests['set-employee-doc']({
		data: data,
		success: function(response) {
			refresh_employee_data();
			docs_datatable.reload();
			if(is_verme_docs_enabled){
				uploadDocs()
				return
			}else{
				unblockModalForm()
				$('#modal_doc').modal('hide');
			}
		},
		error: function(response){
			unblockModalForm()
			handleServerErrorInModal(response)
		}
	})
});



// Обновление данных о сотруднике
refresh_employee_data();
function refresh_employee_data(){
	alerter.hide();
	OutRequests['get-employee']({
		data: {agency_employee_id: employee_id},
		success: function(response) {
			EMPLOYEE = response['employee'];
			JOBS_DISTINCT = response['cur_jobs'];
			var job_start_picker = $('#job_start');
			job_start_picker.datepicker({
					language: 'ru',
					clearBtn: true,
					format: 'dd.mm.yyyy',
					autoclose: true,
					startDate: new Date(EMPLOYEE['receipt'])
			});
			job_start_picker.datepicker('setDate', new Date());
			// Обработка Employee
			$('.fullname').html(EMPLOYEE['surname'] + '<br>' + EMPLOYEE['firstname'] + ' ' + EMPLOYEE['patronymic']);
			for (var key in EMPLOYEE){
				var element = $('#' + key);
				if (element.is('.datepicker')){
					if (EMPLOYEE[key] !== null)
						element.datepicker('setDate', EMPLOYEE[key].replace(/(\d+)[-](\d+)[-](\d+)/, '$3.$2.$1'));
				}
				else if (element.is('select')){
					element.val(EMPLOYEE[key]);
				}
				else if (element.is('div')){
					var $radios = $('input:radio[name=' + key + ']');
					$radios.not('[value=' + EMPLOYEE[key] + ']').prop('checked', false);
					$radios.filter('[value=' + EMPLOYEE[key] + ']').prop('checked', true);
				}
				else {
					$('#' + key).attr('value', EMPLOYEE[key]);
				}
				// agency_id не передается по API
				if(key == 'agency'){
					$('#agency_id_text').html(EMPLOYEE[key])
					$('#agency_id').html('<option value="'+ EMPLOYEE.agency_id +'" selected>' + EMPLOYEE[key] + '<option/>')
				}
			}

			// Функции сотрудника под иконкой в левой стороне
			var employee_jobs = '';
			for (var idx = 0; idx < JOBS_DISTINCT.length; idx++){
				var comma = ','
				if (idx == JOBS_DISTINCT.length - 1)
					comma = ''
				employee_jobs += '<span>' +  JOBS_DISTINCT[idx]['name'] + comma + '</span>';
			}
			$('#profile_jobs').html(employee_jobs);

			// Нарушения сотрудника под функциями
			var employee_violations = '';
			for (var idx = 0; idx < EMPLOYEE['violations'].length; idx++) {
				switch (EMPLOYEE['violations'][idx]['level']) {
					case 'low':
						colorClass = 'alert-info';
						iconClass = 'fa-info-circle';
						break;
					case 'medium':
						colorClass = 'alert-warning';
						iconClass = 'fa-exclamation-triangle';
						break;
					case 'high':
						colorClass = 'alert-danger';
						iconClass = 'fa-exclamation-circle';
						break;
					default:
						break;
				}
				employee_violations += '\
					<div class="m-alert m-alert--icon m-alert--icon-solid m-alert--outline alert alert-brand alert-dismissible fade show empl-violation '+ colorClass +'" role="alert">\
						<div class="m-alert__icon">\
							<i class="m-menu__link-icon fa '+ iconClass +'"></i>\
							<span></span>\
						</div>\
						<div class="m-alert__text">'+
							EMPLOYEE['violations'][idx]['message'] + 
						'</div>\
					</div>'
			}
			$('#profile_violations').html(employee_violations);
		},
		error: function(response){
		}
	});
	OutRequests['get-jobs']({ //загрузка должностей для попапа функций
		data: {agency_employee_id: employee_id},
		success: function(response) {
			$('#jobs_list').html('');
			var jobs_els = '';
			if(response.length == 0) //кнопка над таблицей
				$('#modal_add_job_open').css('visibility', 'hidden');
			else
				$('#modal_add_job_open').css('visibility', 'visible');
			for (idx = 0; idx != response.length; idx++){
				job = response[idx];
				jobs_els += '<option value="' + job.id + '">' + job.name + '</option>';
			}
			$('#jobs_list').html(jobs_els);
			$('#jobs_list').select2();
		}
	});
	OutRequests['get-doc-types']({ //загрузка доктайпов для попапа документа
		data: {agency_employee_id: employee_id},
		success: function(response) {
			$('#doc_types_list').html('');
			var options = '';
			if(response.length == 0) //кнопка над таблицей
				$('#modal_add_doc_open').css('visibility', 'hidden');
			else
				$('#modal_add_doc_open').css('visibility', 'visible');
			for (idx = 0; idx != response.length; idx++){
				var doc_type = response[idx];
				options += '<option value="' + doc_type.id + '">' + doc_type.name + '</option>';
			}
			$('#doc_types_list').html(options);
			$('#doc_types_list').select2();
		}
	});
}




