// Инициализация DatePicker'а
$('.datepicker, .outsource_js_datepicker').not('#modal_fire_employee_date, #modal_fire_outsourcer_date').datepicker({
	language: 'ru',
	clearBtn: true,
	format: 'dd.mm.yyyy',
	autoclose: true,
});
$('#modal_fire_employee_date, #modal_fire_outsourcer_date').datepicker({
	language: 'ru',
	clearBtn: true,
	format: 'dd.mm.yyyy',
	autoclose: true,
	startDate: new Date(),
});
$('.datepicker, .outsource_js_datepicker').datepicker('setDate', 'today');