// фильтрация
var filters = new FilterState([{
	name: 'area_select',
	storage: 'group_area_select_hq_quotas_volume_list',
	default: ''
},{
	name: 'organization_select',
	storage: 'group_organization_select_hq_quotas_volume_list',
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
// [Ре]инициализация селектора магазина/организации
var setOrUpdateOrgSelect = function(organizations){initCommonSelectors.setOrUpdateOrgSelect(organizations, filters.organization_select)}
// Обработчик смены магазина/организации
$('#organization_select').on('change', function () {
	var newValue = $(this).val() || ''
	if(newValue == filters.organization_select.getValue()) return

	filters.organization_select.upd(newValue)
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