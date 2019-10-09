//фильтрация
var filters = new FilterState([{
		name: 'organization_select',
		storage: 'group_organization_select_requests_list',
		default: ''
	},{
		name: 'status_select',
		storage: 'group_status_select_requests_list',
		default: 'accepted'
	},{
		name: 'date_select',
		storage: 'group_date_select_requests_list',
		default: '',
		type: 'date_select'
	}]
)

// Инициализация селектора выбора состояния
var options = [{
		"id": 'all',
		"text": "Все",
	},{
		"id": 'accepted',
		"text": "Получена"
	},{
		"id": 'ready',
		"text": "Обработана"
}]
initCommonSelectors.statusSelect($('#status_select'), {
	options: options, 
	defaultOpt: filters.status_select.getValue(),
})
$('#status_select').on('change', function () {
	filters.status_select.upd($(this).val())
	tableReloader.reload();
});


// [Ре]инициализация селектора магазина/организации
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