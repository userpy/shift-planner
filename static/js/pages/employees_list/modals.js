// ****************
// ИНТЕРФЕЙС
// ****************
$('body').on('orgunits:loaded', function(){
	//требуется загрузить организации для работы
	
	// Сниппеты для модальных окон
	var modals = OUT_SNIPPETS.modal;

	// МОДАЛЬНОЕ ОКНО ДЛЯ НАЙМА СОТРУДНИКА
	var modal_hire_outsourcer = new OutsourceModal();
	modal_hire_outsourcer = modal_hire_outsourcer.create(modals.hire_outsourcer);
	$('body').append(modal_hire_outsourcer);
	modals.hire_outsourcer.constructor();

	// МОДАЛЬНОЕ ОКНО ДЛЯ УВОЛЬНЕНИЯ АУТСОРСЕРА
	var modal_fire_outsourcer = new OutsourceModal();
	modal_fire_outsourcer = modal_fire_outsourcer.create(modals.fire_outsourcer);
	$('body').append(modal_fire_outsourcer);
	modals.fire_outsourcer.constructor();

	// МОДАЛЬНОЕ ОКНО ДЛЯ УВОЛЬНЕНИЯ СОТРУДНИКА
	var modal_fire_employee = new OutsourceModal();
	modal_fire_employee = modal_fire_employee.create(modals.fire_employee);
	$('body').append(modal_fire_employee);

	// МОДАЛЬНОЕ ОКНО ДЛЯ Скачать график смен
	var modal_get_employee_schedule = new OutsourceModal();
	modal_get_employee_schedule = modal_get_employee_schedule.create(modals.get_employee_schedule);
	$('body').append(modal_get_employee_schedule);
	modals.get_employee_schedule.constructor();

	// ****
	// Обработка кнопок в модальных окнах

	// Нажатие кнопки "Нанять" в модальном окна найма сотрудника
	$('#modal_hire_employees_button').on('click', function(){
		if(! checkFormRequirments(ae$('#modal_hire_employee_form')) )return
		var organization_id = $('#modal_hire_organizations_list').find("option:selected").attr('value');
		var hiring_date = $('#hiring_date').data('datepicker').getFormattedDate('yyyy-mm-dd');
		if(!hiring_date){
			handleServerErrorInModal({responseJSON:{recruitment_date: l10n.required}})
			return
		}
		blockModalForm()
		OutRequests['set-employee-recruitment-event']({
			data: {
				csrfmiddlewaretoken: csrf_token,
				organization_id: organization_id,
				recruitment_date: hiring_date,
				employee_list: JSON.stringify(get_selected_employees()),
			},
			success: function(response) {
				unblockModalForm()
				$('#modal_hire_employee_form').modal('hide');
				tableReloader.reload();
			},
			error: function(response){
				unblockModalForm()
				handleServerErrorInModal(response)
			}
		});
	});


	// Нажатие кнопки "Уволить аутсорсера" в модальном окне
	$('#modal_fire_outsourcer_button').on('click', function(){
		if(! checkFormRequirments(ae$('#modal_fire_outsourcer_form')) )return
		var firing_date = $('#modal_fire_outsourcer_date').data('datepicker').getFormattedDate('yyyy-mm-dd');
		var reason = $('#modal_fire_outsourcer_reason').val();
		blockModalForm()
		OutRequests['set-employee-dismissal-event']({
			data: {
				csrfmiddlewaretoken: csrf_token,
				headquater_id: $('#modal_fire_outsourcer_headquater').val(),
				dismissal_date: firing_date,
				dismissal_reason: reason,
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

	// Нажатие кнопки "Уволить сотрудника" в модальном окне
	$('#modal_fire_employee_button').on('click', function(){
		if(! checkFormRequirments(ae$('#modal_fire_employee_form')) )return
		var firing_date = $('#modal_fire_employee_date').data('datepicker').getFormattedDate('yyyy-mm-dd');
		var reason = $('#modal_fire_employee_reason').val();
		blockModalForm()
		OutRequests['dismiss-employee']({
			data: {
				csrfmiddlewaretoken: csrf_token,
				dismissal_date: firing_date,
				dismissal_reason: reason,
				employee_list: JSON.stringify(get_selected_employees()),
			},
			success: function(response) {
				unblockModalForm()
				$('#modal_fire_employee_form').modal('hide');
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
		var data = {
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
	
})
// Получить список выбранных сотрудников в виде массива
function get_selected_employees(){
	var employees_selected = [];
	var ids_selected = [];

	datatable.find('input[type="checkbox"]:checked').each(function (index, rowId) {
		var row = $(this).closest('tr')[0]
		var id = row.ae$('[data-empl-id]') ? row.ae$('[data-empl-id]').dataset.emplId : null
		if (id) ids_selected.push( +id )
	})
	for (var iter = 0; iter < ids_selected.length; iter++){
		employee_index = parseInt(ids_selected[iter]);
		EL_EMPLOYEES_LIST.forEach(function(employee){
			emp_id = employee['id'];
			if(emp_id === employee_index){
				employees_selected.push(emp_id);
				return;
			}
		});
	}
	return employees_selected;
}