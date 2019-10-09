// Глобальные переменные

var SL_SELECTED_SHIFT = '';

//фильтрация
var filters = new FilterState([{
	name: 'organization_select',
	storage: 'group_organization_select_shifts_list',
	default: ''
},{
	name: 'status_select',
	storage: 'group_status_select_shifts_list',
	default: '0'
},{
	name: 'date_select',
	storage: 'group_date_select_shifts_list',
	default: '',
	type: 'date_select'
}])

// #status_select
var options = [{
	"id": 'all',
	"text": "Все",
},{
	"id": 'unassigned',
	"text": "Не назначен"
},{
	"id": 'assigned',
	"text": "Назначен"
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

// Функции для использования в теле кода

// Получить клююч из map по значению
function getKeyByValue(map, map_value) {
	var result = "";
	map.forEach(function(value, key) {
		if(value == map_value) {
			result = key;
		}
	});
	return result;
}

// Получение даты на сегодня в формате 'yyyy-mm-dd'
function todayFormatted() {
	var today = new Date();
	//var dd = today.getDate();
	var mm = today.getMonth() + 1;

	var yyyy = today.getFullYear();
	//if(dd<10){
	//    dd='0'+dd;
	//}
	if(mm < 10) {
		mm = '0' + mm;
	}
	var today = yyyy + '-' + mm + '-01';
	return today;
}

