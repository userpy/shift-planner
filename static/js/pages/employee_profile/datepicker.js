// Инициализация DatePicker'а
$('.datepicker').not('#hiring_date, #modal_fire_employee_date, #modal_fire_outsourcer_date, #job_start').datepicker({
	language: 'ru',
	clearBtn: true,
	format: 'dd.mm.yyyy',
	autoclose: true,
});
$('#hiring_date, #modal_fire_employee_date, #modal_fire_outsourcer_date').datepicker({
	language: 'ru',
	clearBtn: true,
	format: 'dd.mm.yyyy',
	autoclose: true,
	defaultDate: new Date(),
});
$('.modal-body .datepicker').datepicker({
	language: 'ru',
	clearBtn: true,
	format: 'dd.mm.yyyy',
	autoclose: true,
	defaultDate: new Date(),
});
$('#receipt').datepicker('setDate', 'today');