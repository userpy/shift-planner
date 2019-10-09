// ****************
// ПЕРЕМЕННЫЕ
// ****************

// Список полученных сотрудников
var EL_EMPLOYEES_LIST = new Array();

// Получение списка организаций
OutRequests['get-headquaters-organizations']({
	data: {
		csrfmiddlewaretoken: csrf_token,
	},
	success: function(response) {
		var options = '';
		resp = response;
		var headquater_id = 0;
		for (var idx = 0; idx != response.length; idx++){
			selected = '';
			if (idx == 0){
				selected = 'selected';
				headquater_id = response[idx]['id'];
			}
			options += '<option value="';
			options += response[idx]['id'] + '" ' + selected;
			options += ' > ';
			options += response[idx]['name'];
			options += '</option>';
		}
		$('.headquaters_list').html(options);
		$('.headquaters_list, .organizations_list').select2();
		//$('.organizations_list').select2();
		if (agency_list) update_organizations_input(headquater_id);

	},
	error: function(){}
});


// ****************
// ФУНКЦИИ
// ****************


// При смене клиента в модальном окне
function update_organizations_input(headquater_id) {
	OutRequests['get-headquaters-organizations']({
		data: {
			csrfmiddlewaretoken: csrf_token ,
		},
		success: function(response) {
			if(response.length == 0) {
				$('.organizations_list').attr('title', 'Не найдено организаций');
				$('#modal_fire_employee_form').modal('hide');
				return;
			}
			presp = response;
			options = '';
			for(var idx = 0; idx != response.length; idx++) {
				var organization = response[idx];
				selected = '';
				if(idx == 0)
					selected = 'selected';
				options += '<option value="';
				options += organization['id'] + '" ' + selected;
				options += ' > ';
				options += organization['name'];
				options += '</option>';
			}
			$('.organizations_list select').html(options);
			$('.organizations_list').select2();
		},
		error: function(response) {
			alert('Не найдено организаций данного клиента');
			$('#modal_fire_employee_form').modal('hide');
		}
	});
}



// Получить список выбранных сотрудников в виде массива

function get_selected_employees() {
	var employees_selected = [];
	var ids_selected = [];

	datatable.find('input[type="checkbox"]:checked').each(function (index, rowId) {
		var row = $(this).closest('tr')[0]
		var id = row.ae$('[data-empl-id]') ? row.ae$('[data-empl-id]').dataset.emplId : null
		if (id) ids_selected.push( +id )
	})

	for(var iter = 0; iter < ids_selected.length; iter++) {
		employee_index = parseInt(ids_selected[iter]);
		EL_EMPLOYEES_LIST.forEach(function(employee) {
			emp_id = employee['id'];
			if(emp_id === employee_index) {
				employees_selected.push(emp_id);
				return;
			}
		});
	}
	return employees_selected;
}

var filters = new FilterState([{
	name: 'agency_select',
	storage: 'group_agency_select_employees_list',
	default: ''
},	{
	name: 'violation_select',
	storage: 'group_violation_select_employees_list',
	default: ''
}
])
// [Ре]инициализация селектора агентства
var setOrUpdateAgencySelect = function(agencies){initCommonSelectors.setOrUpdateAgencySelect(agencies, filters.agency_select)}

var setOrUpdateViolationSelect = function(violations){initCommonSelectors.setOrUpdateViolationSelect(violations, filters.violation_select)}

// Обработчик смены агентства
$('#agency_select').on('change', function () {
	var newValue = $(this).val() || ''
	if(newValue == filters.agency_select.getValue()) return

	filters.agency_select.upd(newValue)
	tableReloader.reload();
});

// Обработчик смены нарушения
$('#violation_select').on('change', function () {
	var newValue = $(this).val() || ''
	if( JSON.stringify(newValue) == filters.violation_select.getValueAsFixedArrStr()) return

	filters.violation_select.upd(newValue)
	tableReloader.reload();
});

// фильтрация по дате
// Обработчик изменения даты
var tableReloader
addEventListener('interval:week:switch', function(e){
	if(tableReloader) tableReloader.reload()
})
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
$('body').on('orgunits:loaded orgunits:change', function(){
	if(tableReloader) tableReloader.reload()
})