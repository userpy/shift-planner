/*
Copyright 2018 ООО «Верме»
Файл для русской локализации компонента datepicker.
JS-сниппеты для портала аутсорсинга
Цель - создание типичных решений для работы с outsource_utils.js
Author: Artem Bulatov
*/
var OUT_SNIPPETS = {
	// Модальные окна
	modal: {
		// Нанять сотрудника
		hire_outsourcer: {
			options: {
				id: 'modal_hire_employee_form',
				title: 'Прикрепить к клиенту',
			},
			rows: [{
					id: 'modal_hire_headquaters_list',
					name: 'headquater-id',
					label: 'Клиент',
					type: 'select',
					required: true,
					helper: true,
					extra_classes: 'headquaters_list',
					title: 'Выберете клиента',
				},
				{
					id: 'modal_hire_organizations_list',
					name: 'organization_id',
					label: 'Организация',
					type: 'select',
					extra_classes: 'organizations_list',
					required: true,
					helper: true,
					title: 'Выберите организацию'
				},
				{
					id: 'hiring_date',
					name: 'recruitment_date',
					label: 'Дата приема',
					type: 'datepicker',
					extra_classes: 'datepicker',
					required: true,
					helper: true,
				}
			],
			buttons: [{
				id: 'modal_hire_employees_button',
				type: 'success',
				content: 'Прикрепить'
			}, ],
			constructor: function constructor() {
				var hq_handler = function(response) {
					var options = '';
					var headquater_id = 0;
					for(var idx = 0; idx != response.length; idx++) {
						selected = '';
						if(idx == 0) {
							selected = 'selected';
							headquater_id = response[idx]['id'];
						}
						options += '<option value="';
						options += response[idx]['id'] + '" ' + selected;
						options += ' > ';
						options += response[idx]['name'];
						options += '</option>';
					}
					$('#modal_hire_headquaters_list').html(options);
					$('#modal_hire_headquaters_list').select2();
					update_organizations_input(headquater_id, orgSelect.selectedUnit.id);
				};
				// Вызов AJAX-метода с нашим обработчиком.
				// Вызов идет один раз
				OutsourceAPI.getHeadquatersList(orgSelect.selectedUnit.id, hq_handler);

				// Обновление списка сотрудников в модальном окне
				function update_organizations_input(headquater_id, agency_id) {
					// Обработчик успешного ответа
					var org_handler = function(response) {
						if(response.length == 0) {
							$('#modal_hire_organizations_list').html('');
							$('#modal_hire_organizations_list').attr('disabled', true);
							$('#hiring_date').attr('disabled', true);
							$('#modal_hire_organizations_list').select2();
							$('#modal_hire_employees_button').attr('disabled', true);
							return;
						}
						var options = '';
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
						$('#modal_hire_organizations_list').html(options);
						$('#modal_hire_organizations_list').attr('disabled', false);
						$('#hiring_date').attr('disabled', false);
						$('#modal_hire_organizations_list').select2();
						$('#modal_hire_employees_button').attr('disabled', false);
					};
					// Вызов AJAX-метода с нашим обработчиком
					OutsourceAPI.getOrganizationsByHeadquater(headquater_id, agency_id, org_handler);
				}

				// Выбор клиента в модальном окна найма сотрудника
				$('#modal_hire_headquaters_list').on('change', function() {
					headquater_id = $(this).find("option:selected").attr('value');
					agency_id = orgSelect.selectedUnit.id
					update_organizations_input(headquater_id, agency_id);
				});
				// Появление модального окна
				$('#modal_hire_employee_form').on('shown.bs.modal', function() {
					agency_id = orgSelect.selectedUnit.id
					headquater_id = $(this).find("option:selected").attr('value');
					update_organizations_input(headquater_id, agency_id);
				});
			},
		},
		fire_outsourcer: {
			options: {
				id: 'modal_fire_outsourcer_form',
				title: 'Открепить от клиента'
			},
			rows: [{
					id: 'modal_fire_outsourcer_headquater',
					name: 'headquater_id',
					label: 'Клиент',
					type: 'select',
					extra_classes: 'headquaters_list required',
					required: true,
					helper: true,
				},
				{
					id: 'modal_fire_outsourcer_date',
					name: 'dismissal_date',
					label: 'Дата открепления',
					type: 'datepicker',
					extra_classes: 'datepicker required',
					required: true,
					helper: true,
				},
				{
					id: 'modal_fire_outsourcer_reason',
					name: 'dismissal_reason',
					label: 'Комментарии',
					type: 'textarea',
				},
			],
			buttons: [{
				id: 'modal_fire_outsourcer_button',
				type: 'danger',
				content: 'Открепить'
			}, ],
			constructor: function constructor() {
				var hq_handler = function(response) {
					var options = '';
					for(var idx = 0; idx != response.length; idx++) {
						selected = '';
						if(idx == 0) {
							selected = 'selected';
							headquater_id = response[idx]['id'];
						}
						options += '<option value="';
						options += response[idx]['id'] + '" ' + selected;
						options += ' > ';
						options += response[idx]['name'];
						options += '</option>';
					}
					$('#modal_fire_outsourcer_headquater').html(options);
					$('#modal_fire_outsourcer_headquater').select2();
				};
				// Вызов AJAX-метода с нашим обработчиком.
				// Вызов идет один раз
				OutsourceAPI.getHeadquatersList(orgSelect.selectedUnit.id, hq_handler);
			},
		},
		fire_employee: {
			options: {
				id: 'modal_fire_employee_form',
				title: 'Уволить сотрудника'
			},
			rows: [{
					id: 'modal_fire_employee_date',
					name: 'dismissal_date',
					label: 'Дата открепления',
					type: 'datepicker',
					required: true,
					extra_classes: 'datepicker required',
				},
				{
					id: 'modal_fire_employee_reason',
					name: 'dismissal_reason',
					label: 'Комментарии',
					type: 'textarea',
				},
			],
			buttons: [{
				id: 'modal_fire_employee_button',
				type: 'danger',
				content: 'Уволить'
			}, ],
			constructor: function constructor() {}
		},
		get_employee_schedule: {
			options: {
				id: 'modal_get_employee_schedule_form',
				title: 'Скачать график смен'
			},
			rows: [{
					id: 'modal_get_employee_schedule_start_date',
					name: 'start_date',
					label: 'С',
					type: 'datepicker',
					required: true,
					extra_classes: 'datepicker required',
				},
				{
					id: 'modal_get_employee_schedule_end_date',
					name: 'end_date',
					label: 'По',
					type: 'datepicker',
					required: true,
					extra_classes: 'datepicker required',
				},
				{
					id: 'modal_get_employee_schedule_error',
					name: 'error',
					label: ''
				}
			],
			buttons: [{
				id: 'modal_get_employee_schedule_button',
				type: 'success',
				content: 'Выгрузить'
			}, ],
			constructor: function constructor() {
				$('#modal_get_employee_schedule_button').attr('disabled',true);
				$('#modal_get_employee_schedule_form .datepicker').on('changeDate',function(){
					var today = new Date();
					var start_date = $('#modal_get_employee_schedule_start_date').val() != '' ? $('#modal_get_employee_schedule_start_date').datepicker('getDate') : null;
					var end_date = $('#modal_get_employee_schedule_end_date').val() != '' ? $('#modal_get_employee_schedule_end_date').datepicker('getDate') : null;
					if(start_date && end_date && (start_date <= end_date)){
						$('#modal_get_employee_schedule_error-help').hide();
						$('#modal_get_employee_schedule_button').attr('disabled',false);
					} 
					if(start_date && end_date && (start_date > end_date)) {
						$('#modal_get_employee_schedule_button').attr('disabled',true);
						$('#modal_get_employee_schedule_error-help').text("Даты 'с' и 'по' должны быть указаны. Дата 'по' не может быть раньше даты 'с'.").show();
					};
				});
				$('#modal_get_employee_schedule_form .datepicker').on('change', function(){
					var start_date = $('#modal_get_employee_schedule_start_date').val() != '' ? $('#modal_get_employee_schedule_start_date').datepicker('getDate') : null;
					var end_date = $('#modal_get_employee_schedule_end_date').val() != '' ? $('#modal_get_employee_schedule_end_date').datepicker('getDate') : null;
					if(!start_date || !end_date) {
						$('#modal_get_employee_schedule_button').attr('disabled',true);
					}
				})
				// событие закрытие окна: очистка полей формы
				$("#modal_get_employee_schedule_form [data-dismiss='modal']").on('click',function(){
					$('#modal_get_employee_schedule_button').attr('disabled',true);
					$('#modal_get_employee_schedule_form input[type=text]').each(function(){this.value = ''});
					$('#modal_get_employee_schedule_error-help').text('').hide();
				});
			}
		},
		hq_fire_outsourcer: {
			options: {
				id: 'modal_fire_outsourcer_form',
				title: 'Открепить от клиента'
			},
			rows: [{
					id: 'modal_fire_outsourcer_date',
					name: 'dismissal_date',
					label: 'Дата открепления',
					type: 'datepicker',
					required: true,
					extra_classes: 'datepicker required',
				},
				{
					id: 'modal_fire_outsourcer_reason',
					name: 'dismissal_reason',
					label: 'Комментарии',
					type: 'textarea',
				},
				{
					id: 'modal_fire_outsourcer_blacklist',
					name: 'blacklist',
					label: 'Без возможности повторного приема',
					type: 'checkbox',
				},
			],
			buttons: [{
				id: 'modal_fire_outsourcer_button',
				type: 'danger',
				content: 'Открепить'
			}, ],
			constructor: function constructor() {

				// Обработчик успешного получения списка клиентов по AJAX
				var hq_handler = function(response) {
					var options = '';
					for(var idx = 0; idx != response.length; idx++) {
						selected = '';
						if(idx == 0) {
							selected = 'selected';
							headquater_id = response[idx]['id'];
						}
						options += '<option value="';
						options += response[idx]['id'] + '" ' + selected;
						options += ' > ';
						options += response[idx]['name'];
						options += '</option>';
					}
					$('#modal_fire_outsourcer_headquater').html(options);
					$('#modal_fire_outsourcer_headquater').select2();
				};
				// Вызов AJAX-метода с нашим обработчиком.
				// Вызов идет один раз
				OutsourceAPI.getHeadquatersList(null, hq_handler);
			},
		},
		agency_card: {
			options: {
				id: 'modal_agency_card',
				title: 'Карточка агентства',
				closeBtnName: 'Закрыть',
				noFooter: true
			},
			rows: [],
			buttons: [],
			constructor: function constructor() {}
		},
	} // modal -- модальные окна
}
