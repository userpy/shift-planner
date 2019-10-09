var set_employee_options = {
	options: {
		id: 'modal_set_shift',
		title: 'Назначить сотрудника'
	},
	rows: [{
		id: 'agency_employee_select',
		name: 'agency_employee_id',
		label: 'Сотрудник',
		type: 'select',
		extra_classes: ''
	}, ],
	buttons: [{
		id: 'agency_employee_submit',
		type: 'primary',
		content: 'Назначить'
	}, ],
};


var modal_set_employee = new OutsourceModal();
var modal_set_employee = modal_set_employee.create(set_employee_options);
$('body').append(modal_set_employee);
modal_set_employee.removeAttr('tabindex');