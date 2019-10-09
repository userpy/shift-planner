// Инициализация DatePicker'а
$('.modal-body .datepicker').datepicker({
	language: 'ru',
	clearBtn: true,
	format: 'MM yyyy',
	autoclose: true,
	defaultDate: new Date(),
	startView: 1,
	minViewMode: 1,
	maxViewMode: 2,
});