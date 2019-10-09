$('#top_org_select_control').on('change', function () {
	tableReloader.reload();
});

// Обработчик нажатия на строку таблицы
$("div#hq_employees_datatable_table").on('click', 'tr', function(e) {
	if(e.target.findElemByClass('m-datatable__cell--check')) return
 	var row_id = $(this).attr('data-row')
	var employee_id = datatable.getDataSet()[row_id]['id'];
	if(employee_id) {
		window.location.href = "/hq-employee/" + employee_id;
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

// Нажатие кнопки "Уволить аутсорсера" в выпадающем списке действий
$('#fire_from_organization_employee_button').on('click', function(){
	if(datatable.getSelectedRecords().length == 0)
		return;

	$('#modal_fire_outsourcer_form .datepicker').datepicker({
		language: 'ru',
		clearBtn: true,
		format: 'dd.mm.yyyy',
		autoclose: true,
		startDate: new Date(),
	});
	$('#modal_fire_outsourcer_form').modal({backdrop: true});
});


// // Обработчик наведения на последнюю ячейку строки
// $('#hq_employees_datatable_table').
// 	on('mouseenter', 'td:last-child', function(e) {
// 				var element = $(this).find('a');
// 				element.addClass('a-active');
// });
// $('#hq_employees_datatable_table').
// 	on('mouseleave', 'td:last-child', function(e) {;
// 				var element = $(this).find('a');
// 				element.removeClass('a-active');
// });
$('#hq_employees_datatable_table').
	on('click', 'td:last-child', function(e) {
				var element = $(this).find('a');
				var url = element.attr('href');
				window.location.href = url;
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
		'agency_id': function(){
			return filters.agency_select.getValue();
		}(),
		'state': function(){
			return filters.violation_select.getValueAsFixedArrStr();
		}(),
		'violation_ids': function(){
			return filters.violation_select.getValueAsFixedArrStr();
		}(),
		'pagination[page]': $("#hq_employees_datatable_table").mDatatable().getDataSourceParam('pagination')['page'],
		'pagination[perpage]': $("#hq_employees_datatable_table").mDatatable().getDataSourceParam('pagination')['perpage'],
		'[sort][field]': function(){
			if ('sort' in $("#hq_employees_datatable_table").mDatatable().getDataSourceParam()){
				return $("#hq_employees_datatable_table").mDatatable().getDataSourceParam('sort')['field'];
			}
		}() || '',
		'[sort][sort]': function(){
			if ('sort' in $("#hq_employees_datatable_table").mDatatable().getDataSourceParam()) {
				return $("#hq_employees_datatable_table").mDatatable().getDataSourceParam('sort')['sort'];
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


