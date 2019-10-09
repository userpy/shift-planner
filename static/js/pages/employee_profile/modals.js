// Сниппеты для модальных окон
var modals = OUT_SNIPPETS.modal;
var outsourceModal = new OutsourceModal();
$('body').on('orgunits:loaded', function() {
	//требуется загрузка орг единиц для работы
	
	if(request_page_party == 'agency' || request_page_party == 'promo' || request_page_party == 'broker') {
		// МОДАЛЬНОЕ ОКНО ДЛЯ НАЙМА СОТРУДНИКА -- только для сотрудника агентства
		var modal_hire_outsourcer = outsourceModal.create(modals.hire_outsourcer);
		$('body').append(modal_hire_outsourcer);
		modals.hire_outsourcer.constructor();
		// Инициализация конструктора для модального окна найма аутсорсера
	}

	if(request_page_party == 'agency' || request_page_party == 'promo' || request_page_party == 'broker') {
		// МОДАЛЬНОЕ ОКНО ДЛЯ УВОЛЬНЕНИЯ АУТСОРСЕРА -- только для сотрудника агентства
		var modal_fire_outsourcer = outsourceModal.create(modals.fire_outsourcer);
		$('body').append(modal_fire_outsourcer);
		modals.fire_outsourcer.constructor();
	}

	if(request_page_party == 'client') {
		// МОДАЛЬНОЕ ОКНО 'открепить от клиента' -- только для клиента
		var modal_fire_outsourcer = outsourceModal.create(modals.hq_fire_outsourcer);
		$('body').append(modal_fire_outsourcer);
		modals.hq_fire_outsourcer.constructor();
	}

	if(request_page_party == 'agency' || request_page_party == 'promo' || request_page_party == 'broker') {
		// МОДАЛЬНОЕ ОКНО ДЛЯ УВОЛЬНЕНИЯ СОТРУДНИКА -- только для сотрудника агентства
		var modal_fire_employee = outsourceModal.create(modals.fire_employee);
		$('body').append(modal_fire_employee);
		modals.fire_employee.constructor()
	}

	if(request_page_party == 'client' || request_page_party == 'agency' || request_page_party == 'promo' || request_page_party == 'broker') {
		// МОДАЛЬНОЕ ОКНО ДЛЯ Выгрузить график работы сотрудника -- только для сотрудника агентства
		var modal_get_employee_schedule = outsourceModal.create(modals.get_employee_schedule);
		$('body').append(modal_get_employee_schedule);
		modals.get_employee_schedule.constructor();
	}

	//модальное окно для карточки агентства
	var modal_agency_card = outsourceModal.create(modals.agency_card);
	$('body').append(modal_agency_card);
	modals.agency_card.constructor()

	/*
		ОБРАБОТЧИКИ КНОПОК ВЫПАДАЮЩЕГО МЕНЮ
	*/

	// Нажатие кнопки "Создать" [сотрудника] в выпадающем списке действий
	$('#nav_create_employee').on('click', function(){
		window.location.href = DETAIL_PAGE_PREFIX + "create-employee/";
	});

	$('#nav_edit_employee').on('click', function(){
		$('#m_user_profile_tab_main .form-control').not('#agency_id').enable();
		$('#submit_button, #reset_button').show();
	});

	if(request_page_party == 'agency' || request_page_party == 'promo' || request_page_party == 'broker') {
		// Нажатие кнопки "Принять на работу" в выпадающем списке действий
		$('#nav_hire_outsourcer').on('click', function(){
			$('#modal_hire_employee_form .datepicker').datepicker({
				language: 'ru',
				clearBtn: true,
				format: 'dd.mm.yyyy',
				autoclose: true,
				startDate: new Date(),
			});
			$('#modal_hire_employee_form').modal({backdrop: true});
		});
	}

	// Нажатие кнопки "Уволить из аутсорсера" в выпадающем списке действий
	$('#nav_fire_outsourcer').on('click', function(){
		$('#modal_fire_outsourcer_form .datepicker').datepicker({
			language: 'ru',
			clearBtn: true,
			format: 'dd.mm.yyyy',
			autoclose: true,
			startDate: new Date(),
		});
		$('#modal_fire_outsourcer_form').modal({backdrop: true});
	});

	if(request_page_party == 'agency' || request_page_party == 'promo' | request_page_party == 'broker') {
		// Нажатие кнопки "Уволить сотрудника" в выпадающем списке действий
		$('#nav_fire_employee').on('click', function(){
			$('#modal_fire_employee_form .datepicker').datepicker({
				language: 'ru',
				clearBtn: true,
				format: 'dd.mm.yyyy',
				autoclose: true,
				startDate: new Date(),
			});
			$('#modal_fire_employee_form').modal({backdrop: true});
		});
	}

	if(request_page_party == 'client' || request_page_party == 'agency' || request_page_party == 'promo' | request_page_party == 'broker') {
		// Нажатие кнопки "Выгрузить график работы сотрудника" в выпадающем списке действий
		$('#nav_get_employee_schedule').on('click', function(){
			$('#modal_get_employee_schedule_form .datepicker').datepicker({
				language: 'ru',
				clearBtn: true,
				format: 'dd.mm.yyyy',
				autoclose: true
			});
			$('#modal_get_employee_schedule_form').modal({backdrop: true});
		});
	}

	// кнопка карточки агентства
	$('.agency_card_btn').on('click', function(){
		const AgencyCardFields = {
			name:{label:'название'},
			code:{label:'код'}, 
			full_name:{label: 'полное название'},
			address:{label: 'адрес'},
			actual_address:{label: 'фактический адрес'},
			phone:{label: 'телефон'},
			site:{label: 'web-сайт'},
			email:{label: 'email'},
			description:{label: 'описание'},
			managers:{
				label:'менеджеры',
				full_name:{label:'ФИО'},
				position:{label:'должность'},
				phone:{label:'телефон'},
				email:{label:'почта'}
			}
		}
		$.ajax({
			url:'/api-agency-info?employee_id='+employee_id,
			success: function(res){
				$('#modal_agency_card .modal-body').html(res);
				$('#modal_agency_card').modal({backdrop: true});
			},
			error: function(res){
				unBlockUILoading()
				alert('Ошибка запроса')
			}
		})
	});

	// ****
	// Обработка кнопок в модальных окнах

	// Нажатие кнопки "Нанять" в модальном окна найма сотрудника
	$('#modal_hire_employees_button').on('click', function(){
		if(! checkFormRequirments(ae$('#modal_hire_employee_form')) )return 
		var organization_id = $('#modal_hire_organizations_list').find("option:selected").attr('value');
		var hiring_date = $('#hiring_date').data('datepicker').getFormattedDate('yyyy-mm-dd');
		blockModalForm()
		OutRequests['set-employee-recruitment-event']({
			data: {
				csrfmiddlewaretoken: csrf_token,
				organization_id: organization_id,
				recruitment_date: hiring_date,
				employee_list: JSON.stringify([employee_id]),
			},
			success: function(response) {
				unblockModalForm()
				$('#modal_hire_employee_form').modal('hide');
				// jobs_datatable.reload()
				if (typeof events_datatable !== 'undefined') events_datatable.reload()
				// organizations_datatable.reload()
				// docs_datatable.reload()
			},
			error: function(response){
				unblockModalForm()
				handleServerErrorInModal(response)
			}
		})
	});


	// Нажатие кнопки "Уволить аутсорсера" в модальном окне
	$('#modal_fire_outsourcer_button').on('click', function(){
		if(! checkFormRequirments(ae$('#modal_fire_outsourcer_form')) )return
		var firing_date = $('#modal_fire_outsourcer_date').data('datepicker').getFormattedDate('yyyy-mm-dd');
		var reason = $('#modal_fire_outsourcer_reason').val();
		var data = {
			csrfmiddlewaretoken: csrf_token,
			headquater_id: $('#modal_fire_outsourcer_headquater').val() || orgSelect.selectedUnit.id,
			dismissal_date: firing_date,
			dismissal_reason: reason,
			employee_list: JSON.stringify([employee_id]),
		}
		if(user.is_superuser || request_page_party == 'client'){
			data.blacklist = $('#modal_fire_outsourcer_blacklist').is(':checked')
		}
		blockModalForm()
		OutRequests['set-employee-dismissal-event']({
			data: data,
			success: function(response) {
				unblockModalForm()
				$('#modal_fire_outsourcer_form').modal('hide');
			},
			error: function(response){
				unblockModalForm()
				handleServerErrorInModal(response)
			}
		})
	});

	// Нажатие кнопки "Уволить сотрудника" в модальном окне
	$('#modal_fire_employee_button').on('click', function(){
		if(! checkFormRequirments(ae$('#modal_fire_employee_form')) )return
		var firing_date = $('#modal_fire_employee_date').data('datepicker').getFormattedDate('yyyy-mm-dd');
		var reason = $('#modal_fire_employee_reason').val();
		var data =  {
			csrfmiddlewaretoken: csrf_token,
			dismissal_date: firing_date,
			dismissal_reason: reason,
			employee_list: JSON.stringify([employee_id]),
		}
		if(user.is_superuser || request_page_party == 'client'){
			data.blacklist = $('#modal_fire_outsourcer_blacklist').is(':checked')
		}
		blockModalForm()
		OutRequests['dismiss-employee']({
			data: data,
			success: function(response) {
				unblockModalForm()
				$('#modal_fire_employee_form').modal('hide');
				refresh_employee_data();
			},
			error: function(response){
				unblockModalForm()
				handleServerErrorInModal(response)
			}
		})
	});

	// Нажатие кнопки "Выгрузить" в модальном окне Выгрузить график смен сотрудника
	$('#modal_get_employee_schedule_button').on('click', function(){
		if(! checkFormRequirments(ae$('#modal_get_employee_schedule_form')) )return
		var start_date = $('#modal_get_employee_schedule_start_date').data('datepicker').getFormattedDate('yyyy-mm-dd');
		var end_date = $('#modal_get_employee_schedule_end_date').data('datepicker').getFormattedDate('yyyy-mm-dd');
		var data =  {
			csrfmiddlewaretoken: csrf_token,
			start: start_date,
			end: end_date,
			employee_list: JSON.stringify([employee_id])
		}
		blobXHR(
			{data:data, url: '/api-export-employee-shifts'},
			onOk = function(){
				$('#modal_get_employee_schedule_form input[type=text]').each(function(){this.value = ''});
				$('#modal_get_employee_schedule_form').modal('hide');
			}	
		)
		//OutRequests['get_employee_schedule']
		// $.ajax({
		// 	url: "/api-export-employee-shifts",
		// 	data: data,
		// 	success: function(r){
		// 		if(r.type == 'success'){
		// 			blobXHR({url: verme_docs_url + r.url, file:{name: 'График смен'}}, null, function(r){alert(l10n[r.message])})
		// 		}else{
		// 			unBlockUILoading()
		// 			alert(l10n[r.message])
		// 		}
		// 	},
		// 	// success: function(response) {
		// 	// 	unblockModalForm()
		// 	// 	$('#modal_get_employee_schedule_form').modal('hide');
		// 	// 	refresh_employee_data();
		// 	// },
		// 	error: function(response){
		// 		unblockModalForm()
		// 		handleServerErrorInModal(response)
		// 	}
		// })
	});

	// Окно перевода
	$('#nav_employee_transition').on('click', function(){
		$('#modal_transitions').modal({backdrop: true})
		blockModalForm()
		OutRequests['transition-agency-employee']({
			data: {
				agency_employee_id: employee_id
			},
			type: 'GET',
			success: function(r) {
				$('#mt_agency_select').select2({
					data: r.agencies,
					placeholder: 'Выберите вариант'
				})
				$('#mt_date').datepicker({
					minDate: new Date(r.min_date_transition),
					defaultDate: new Date(),
				})
			},
			error: function(response){
				unblockModalForm()
				handleServerErrorInModal(response)
			}
		})
	})
	$('#mt_do_transiton').on('click', function(){
		if(! checkFormRequirments(ae$('#modal_transitions')) )return
		var selectedAgensy = $('#mt_agency_select').val()
		var startDate = $('#mt_date').data('datepicker').getFormattedDate('yyyy-mm-dd')

		var data = {
			csrfmiddlewaretoken: csrf_token,
			agency_employee_id: employee_id,
			agency: selectedAgensy,
			date_transition: startDate,
		}
		blockModalForm()
		OutRequests['transition-agency-employee']({
			data: data,
			type: 'POST',
			success: function(response) {
				unblockModalForm()
				if(transitions_datatable) transitions_datatable.reload()//может быть андифайнд, если попап открыли не со вкладки таблицы
				$('#modal_transitions').modal('hide')
			},
			error: function(response){
				unblockModalForm()
				handleServerErrorInModal(response)
			}
		})
	});
})

// ЗАВЕРШЕНИЕ ИНИЦИАЛИЗАЦИИ МОДАЛЬНЫХ ОКОН
