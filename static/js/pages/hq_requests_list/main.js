// фильтрация
var filters = new FilterState([{
	name: 'status_select',
	storage: 'group_status_select_hq_requests_list',
	default: 'accepted'
},{
	name: 'agency_select',
	storage: 'group_agency_select_hq_requests_list',
	default: ''
}])

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
// Обработчик изменения даты
var tableReloader
addEventListener('interval:week:switch', function(e){
	if(tableReloader) tableReloader.reload()
})