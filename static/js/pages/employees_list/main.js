
// ****************
// ПЕРЕМЕННЫЕ
// ****************

// Список полученных сотрудников
var EL_EMPLOYEES_LIST = new Array();

var DETAIL_PAGE_PREFIX = '/'
if(request_page_party == 'agency') {
	DETAIL_PAGE_PREFIX = '/'
}
if(request_page_party == 'promo') {
	DETAIL_PAGE_PREFIX = '/promo-'
}
if(request_page_party == 'broker') {
	DETAIL_PAGE_PREFIX = '/broker-'
}
//фильтрация
var filters = new FilterState([{
	name: 'status_select',
	storage: 'group_status_select_employees_list',
	default: '0'
},	{
	name: 'violation_select',
	storage: 'group_violation_select_employees_list',
	default: ''
}])
// Фильтрация по полю статуса
// Инициализация селектора статуса
initCommonSelectors.statusSelect($('#status_select'),{
	options: [{
			"id": 'all',
			"text": "Все",
		},{
			"id": 'active',
			"text": "Работает"
		},{
			"id": 'dismissed',
			"text": "Уволен"
		}
	],
	defaultOpt: filters.status_select.getValue(),
})

var setOrUpdateViolationSelect = function(violations){initCommonSelectors.setOrUpdateViolationSelect(violations, filters.violation_select)}

$('#status_select').on('change', function(){
	filters.status_select.upd(	$('#status_select').find("option:selected").attr('value') )
	tableReloader.reload();
});

// Обработчик смены нарушения
$('#violation_select').on('change', function () {
	var newValue = $(this).val() || ''
	if( JSON.stringify(newValue) == filters.violation_select.getValueAsFixedArrStr()) return

	filters.violation_select.upd(newValue)
	tableReloader.reload();
});

$('#generalSearch').val('')

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