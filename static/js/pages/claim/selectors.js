$('body').on('orgunits:loaded', function() {
	if(claim_id){
		getClaim();
	}else{
		$('#agency_selected').attr("disabled", true);
		$('#hq_selected').attr("disabled", true);
		$('#claim_message').attr("disabled", true);
		initSelectors();
		setCitySelector();
	}
	//FormControls.init();

	// Обработчик смены агентства
	$('#city_select').on('change', function (){
		clearForm();
		initSelectors();
		$.ajax({
			type: 'GET',
			cache: false,
			url: '/api-get-claim-stores-agencies-types/?format=json',
			data: {
				city_id: $('#city_select').val(),
			},
			success: function (data) {
				document.getElementById("organization_select").innerHTML='<option></option>';
				$('#organization_select').attr("disabled", false);
				set_organization_select2(data['orgunit_list']);
			}
		});
	});
	$('#organization_select').on('change', function (){
		$.ajax({
			type: 'GET',
			cache: false,
			url: '/api-get-claim-stores-agencies-types/?format=json',
			data: {
				city_id: $('#city_select').val(),
				orgunit_id: $('#organization_select').val(),
			},
			success: function (data) {
				document.getElementById("agency_select").innerHTML='<option></option>';
				document.getElementById("type_select").innerHTML='<option></option>';
				$('#agency_select').attr("disabled", false);
				$('#type_select').attr("disabled", false);
				$('#claim_message').attr("disabled", false)
				set_agency_select2(data['agency_list']);
				set_type_select2(data['claim_types']);
			}
		});
	});


	// Получение значений для селекторов
	function setCitySelector(){
		$.ajax({
			type: 'GET',
			cache: false,
			url: '/api-get-claim-cities/?format=json',
			data: {
				headquater_id: orgSelect.selectedUnit.id
			},
			success: function (data) {
				set_city_select2(data['city_list']);
			}
		});
	}

	function initSelectors(){
		$('#organization_select').attr("disabled", true);
		$('#agency_select').attr("disabled", true);
		$('#type_select').attr("disabled", true);
		set_organization_select2();
		set_agency_select2();
		set_type_select2();
	}

	// Инициализация селектора города
	function set_city_select2(city_list) {
		$('#city_select').select2({
			placeholder: "Город...",
			allowClear: false,
			data: city_list,
			width: '100%'
		});
	}

	// Инициализация селектора магазина/организации
	function set_organization_select2(organization_list) {
		$('#organization_select').select2({
			placeholder: "Магазин...",
			allowClear: true,
			data: organization_list,
			width: '100%'
		});
	}

	// Инициализация селектора агентства
	function set_agency_select2(agency_list) {
		$('#agency_select').select2({
			placeholder: "Агентство...",
			allowClear: true,
			data: agency_list,
			width: '100%'
		});
	}

	// Инициализация селектора типа
	function set_type_select2(types_list) {
		$('#type_select').select2({
			placeholder: "Тип...",
			allowClear: true,
			data: types_list,
			width: '100%'
		});
	}
});
