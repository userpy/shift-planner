var DETAIL_PAGE_PREFIX = '/'
if(request_page_party == 'agency') {
	DETAIL_PAGE_PREFIX = '/'
}
if(request_page_party == 'promo') {
	DETAIL_PAGE_PREFIX = '/promo-'
}

// фильтрация
var filters = new FilterState([{
	name: 'organization_select',
	storage: 'group_organization_select_claims_list',
	default: ''
},{
	name: 'status_select',
	storage: 'group_status_select_claims_list',
	default: 'wait'
},{
	name: 'date_select',
	storage: 'group_date_select_claims_list',
	default: '',
	type: 'date_select'
}])


// Инициализация селектора выбора состояния
var options = [
	{"id":"all", "text":"Все"},
	{"id":"wait", "text":"На рассмотрении"},
	{"id":"accept", "text":"В работе"},
	{"id":"reject", "text":"Отклонена"},
	{"id":"closed", "text":"Закрыта"}
]
initCommonSelectors.statusSelect($('#status_select'), {
	options: options, 
	defaultOpt: filters.status_select.getValue(),
})
$('#status_select').on('change', function () {
	filters.status_select.upd($(this).val())
	tableReloader.reload();
});



// инициализация селектора магазина/организации
var setOrUpdateOrgSelect = function(organizations){initCommonSelectors.setOrUpdateOrgSelect(organizations, filters.organization_select)}

$('#organization_select').on('change', function () {
	var newValue = $(this).val() || ''
	if(newValue == filters.organization_select.getValue()) return

	filters.organization_select.upd(newValue)
	tableReloader.reload();
});

// фильтрация по дате
// Инициализация DatePicker'а
initCommonSelectors.monthDatePicker($('#date_select'), {defDate: filters.date_select.getValue() })

// Обработчик изменения даты
$( "#date_select" ).change(function() {
	var newValue = $(this).val() || ''
	if(newValue == filters.date_select.getValue()) return

	filters.date_select.upd(newValue)
	tableReloader.reload();
});