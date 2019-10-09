// фильтрация
var filters = new FilterState([{
	name: 'area_select',
	storage: 'group_area_select_hq_quotas_list',
	default: ''
},{
	name: 'promo_select',
	storage: 'group_promo_select_hq_quotas_list',
	default: ''
},{
	name: 'violation_select',
	storage: 'group_violation_select_hq_quotas_list',
	default: ''
}])
// [Ре]инициализация селектора Зона магазина
var setOrUpdateAreaSelect = function(areas){initCommonSelectors.setOrUpdateAreaSelect(areas, filters.area_select)}
// Обработчик смены Зона магазина
$('#area_select').on('change', function () {
	var newValue = $(this).val() || ''
	if(newValue == filters.area_select.getValue()) return

	filters.area_select.upd(newValue)
	tableReloader.reload();
});
// [Ре]инициализация селектора Промоутера
var setOrUpdatePromoSelect = function(promos){initCommonSelectors.setOrUpdatePromoSelect(promos, filters.promo_select)}
// Обработчик смены Промоутера
$('#promo_select').on('change', function () {
	var newValue = $(this).val() || ''
	if(newValue == filters.promo_select.getValue()) return

	filters.promo_select.upd(newValue)
	tableReloader.reload();
});

var setOrUpdateViolationSelect = function(violations){initCommonSelectors.setOrUpdateViolationSelect(violations, filters.violation_select)}
// Обработчик смены нарушения
$('#violation_select').on('change', function () {
	var newValue = $(this).val() || ''
	if( JSON.stringify(newValue) == filters.violation_select.getValueAsFixedArrStr()) return

	filters.violation_select.upd(newValue)
	tableReloader.reload();
});

$('#top_org_select_control').on('change', function () {
	tableReloader.reload();
});

// фильтрация по дате
// Обработчик изменения даты
var tableReloader
addEventListener('interval:week:switch', function(e){
	if(tableReloader) tableReloader.reload()
})