
// Сниппеты для модальных окон
var modals = OUT_SNIPPETS.modal;

// МОДАЛЬНОЕ ОКНО ДЛЯ УВОЛЬНЕНИЯ АУТСОРСЕРА
var modal_fire_outsourcer = new OutsourceModal();
var modal_fire_outsourcer = modal_fire_outsourcer.create(modals.hq_fire_outsourcer);
$('body').append(modal_fire_outsourcer);

// МОДАЛЬНОЕ ОКНО ДЛЯ Скачать график смен
var modal_get_employee_schedule = new OutsourceModal();
modal_get_employee_schedule = modal_get_employee_schedule.create(modals.get_employee_schedule);
$('body').append(modal_get_employee_schedule);
modals.get_employee_schedule.constructor();

// Выбор клиента в модальном окна найма сотрудника
$('.headquaters_list').on('change', function(){
	headquater_id = $(this).find("option:selected").attr('value');
	if(agency_list)	update_organizations_input(headquater_id);
});

// Нажатие кнопки "Скачать график смен" в выпадающем списке действий
$('#export_employee_schedule_button').on('click', function(){
	if(datatable.getSelectedRecords().length == 0) return;
	$('#modal_get_employee_schedule_form .datepicker').datepicker({
		language: 'ru',
		clearBtn: true,
		format: 'dd.mm.yyyy',
		autoclose: true
	});
	$('#modal_get_employee_schedule_form').modal({backdrop: true});
});

// Нажатие кнопки "Уволить аутсорсера" в модальном окне
$('#modal_fire_outsourcer_button').on('click', function(){
	if(! checkFormRequirments(ae$('#modal_fire_outsourcer_form')) )return
	var orgunit_code = orgSelect.selectedUnit.code;
	var firing_date = $('#modal_fire_outsourcer_date').data('datepicker').getFormattedDate('yyyy-mm-dd');
	var reason = $('#modal_fire_outsourcer_reason').val();
	var blacklist = $('#modal_fire_outsourcer_blacklist').is(':checked');
	blockModalForm()
	OutRequests['set-employee-dismissal-event']({
		data: {
			csrfmiddlewaretoken: csrf_token,
			orgunit: orgunit_code,
			dismissal_date: firing_date,
			dismissal_reason: reason,
			blacklist: blacklist,
			employee_list: JSON.stringify(get_selected_employees()),
		},
		success: function(response) {
			unblockModalForm()
			$('#modal_fire_outsourcer_form').modal('hide');
			tableReloader.reload();
		},
		error: function(response){
			unblockModalForm()
			handleServerErrorInModal(response)
		}
	});
});

// Нажатие кнопки "Выгрузить" в модальном окне Выгрузить график смен сотрудника
$('#modal_get_employee_schedule_button').on('click', function(){
	if(! checkFormRequirments(ae$('#modal_get_employee_schedule_form')) )return
	var start_date = $('#modal_get_employee_schedule_start_date').data('datepicker').getFormattedDate('yyyy-mm-dd');
	var end_date = $('#modal_get_employee_schedule_end_date').data('datepicker').getFormattedDate('yyyy-mm-dd');
	var data =  {
		csrfmiddlewaretoken: csrf_token,
		start: start_date,
		end: end_date,
		employee_list: JSON.stringify(get_selected_employees())
	}
	blobXHR(
		{data:data, url: '/api-export-employee-shifts'},
		onOk = function(){
			$('#modal_get_employee_schedule_form input[type=text]').each(function(){this.value = ''});
			$('#modal_get_employee_schedule_form').modal('hide');
		}
	)
});