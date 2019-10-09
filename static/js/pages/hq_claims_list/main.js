// фильтрация
var filters = new FilterState([{
	name: 'status_select',
	storage: 'group_status_select_hq_claims_list',
	default: 'all'
},{
	name: 'agency_select',
	storage: 'group_agency_select_hq_claims_list',
	default: ''
},{
	name: 'date_select',
	storage: 'group_date_select_hq_claims_list',
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

// [Ре]инициализация селектора агентства
var setOrUpdateAgencySelect = function(agencies){initCommonSelectors.setOrUpdateAgencySelect(agencies, filters.agency_select)}
// Обработчик смены агентства
$('#agency_select').on('change', function () {
	var newValue = $(this).val() || ''
	if(newValue == filters.agency_select.getValue()) return

	filters.agency_select.upd(newValue)
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