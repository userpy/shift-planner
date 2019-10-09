// ****************
// ОБРАБОТЧИКИ
// ****************

$('#top_org_select_control').on('change', function () {
	tableReloader.reload();
});

// Обработчик нажатия на строку таблицы
$("div#employees_datatable_table").on('click', 'tr', function(e) {
	if(e.target.findElemByClass('m-datatable__cell--check')) return
	var row_id = $(this).attr('data-row')
	var employee_id = datatable.getDataSet()[row_id]['id'];
	if(employee_id) {
		window.location.href = DETAIL_PAGE_PREFIX + "employee/" + employee_id;
	} else {
		console.error('ошибка получения данных', employee_id)
	}	
});


// Нажатие dropdown-кнопки "Действие" - выпадающего списка действий
$('#action_button').on('click', function(){
	if(datatable.getSelectedRecords().length == 0){
		$('.mass_action').hide();
		$('.single_action').show();
	}
	else{
		$('.mass_action').show();
		$('.single_action').hide();
	}
});

// Нажатие кнопки "Создать" [сотрудника] в выпадающем списке действий
$('#create_employee_button').on('click', function(){
	window.location.href = DETAIL_PAGE_PREFIX + 'create-employee/'
});


// Нажатие кнопки "Принять на работу" в выпадающем списке действий
$('#hire_to_organization_employee_button').on('click', function(){
	if(datatable.getSelectedRecords().length == 0) return;
	$('#modal_hire_employee_form .datepicker').datepicker({
		language: 'ru',
		clearBtn: true,
		format: 'dd.mm.yyyy',
		autoclose: true,
		startDate: new Date(),
	});
	$('#modal_hire_employee_form').modal({backdrop: true});
});

// Нажатие кнопки "Уволить аутсорсера" в выпадающем списке действий
$('#fire_from_organization_employee_button').on('click', function(){
	if(datatable.getSelectedRecords().length == 0) return

	// Получение списка организаций
	OutRequests['get-headquaters-organizations']({
		data: {
			csrfmiddlewaretoken: csrf_token,
			agency_id: orgSelect.selectedUnit.id
		},
		success: function(response) {
			var options = '';
			resp = response;
			for (var idx = 0; idx != response.length; idx++){
				selected = '';
				if (idx == 0)
						selected = 'selected';
				options += '<option value="';
				options += response[idx]['id'] + '" ' + selected;
				options += ' > ';
				options += response[idx]['name'];
				options += '</option>';
			}
			$('#modal_fire_outsourcer_headquater').html(options);
			$('#modal_fire_outsourcer_headquater').select2()
		},
		error: function(response){}
	});

	$('#modal_fire_outsourcer_form .datepicker').datepicker({
		language: 'ru',
		clearBtn: true,
		format: 'dd.mm.yyyy',
		autoclose: true,
		startDate: new Date(),
	});
	$('#modal_fire_outsourcer_form').modal({backdrop: true});
});

// Нажатие кнопки "Уволить сотрудника" в выпадающем списке действий
$('#fire_from_agency_employee_button').on('click', function(){
	if(datatable.getSelectedRecords().length == 0) return;
	$('#modal_fire_employee_form .datepicker').datepicker({
		language: 'ru',
		clearBtn: true,
		format: 'dd.mm.yyyy',
		autoclose: true,
		startDate: new Date(),
	});
	$('#modal_fire_employee_form').modal({backdrop: true});
});

// Нажатие кнопки "Скачать график смен" в выпадающем списке действий
$('#export_employee_schedule_button').on('click', function(){
	if(datatable.getSelectedRecords().length == 0) return;
	$('#modal_get_employee_schedule_form .datepicker').datepicker({
		language: 'ru',
		clearBtn: true,
		format: 'dd.mm.yyyy',
		autoclose: true,
		//startDate: '-5d'
	});
	$('#modal_get_employee_schedule_form').modal({backdrop: true});
});

// Обработчик нажатия кнопки экспорта
$("#export_employee_button").on('click', function() {
	var data = {
		'orgunit': orgSelect.selectedUnit.code,
		'state': function(){
			return filters.status_select.getValue();
		}(),
		'violation_id': function(){
			return filters.violation_select.getValueAsFixedArrStr();
		}(),
		'pagination[page]': $("#employees_datatable_table").mDatatable().getDataSourceParam('pagination')['page'],
		'pagination[perpage]': $("#employees_datatable_table").mDatatable().getDataSourceParam('pagination')['perpage'],
		'[sort][field]': function(){
			if ('sort' in $("#employees_datatable_table").mDatatable().getDataSourceParam()){
				return $("#employees_datatable_table").mDatatable().getDataSourceParam('sort')['field'];
			}
		}() || '',
		'[sort][sort]': function(){
			if ('sort' in $("#employees_datatable_table").mDatatable().getDataSourceParam()) {
				return $("#employees_datatable_table").mDatatable().getDataSourceParam('sort')['sort'];
			}
		}() || '',
		'datatable[query][generalSearch]': function() {
			if($('#generalSearch').val().length >= 3)
			    return $('#generalSearch').val();
			return '';
		}(),
		xlsexport: true,
		xlsexport_code: request_page_party + '_employees_list',
		format: 'json',
		_: new Date().getTime()
	};
	blobXHR({
		url:'/api-employees-list',
		data: data,
	})
})

$('body').on('orgunits:loaded orgunits:change', function(){
	if(orgSelect.selectedUnit.isHeadquater){
		$('#create_employee_button').hide()
	}else{
		$('#create_employee_button').show()
	}
})