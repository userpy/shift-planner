// Обработчик смены агентства
$('#top_org_select_control').on('change', function() {
	tableReloader.reload();
});

//Обработчик нажатия кнопки в таблице
$("#m_datatable").on("click", ".m-datatable__cell .btn", function(e) {
	shift_id = e.target.attributes.shift_id.nodeValue;
	employee_id = e.target.attributes.employee_id.nodeValue;
	SL_SELECTED_SHIFT = shift_id;

	OutRequests['shift-employee']({
		data: 'shift_id=' + shift_id,
		success: function(data) {
			var response = JSON.parse(data);
			$("#agency_employee_select").html('');
			$("#agency_employee_select").append('<option value="none"> Не назначен </option>');
			for(i = 0; i < response.length; i++) {
				var employee = response[i];
				var selected = "";
				if(employee_id == employee['id'])
					selected = "selected";
				$('#agency_employee_select').append('<option value=\'' + employee['id'] + '\' ' + selected + '>' +
					employee['name'] + ' / ' + employee['number'] + '</option>');
			}
			$('#agency_employee_select').select2({
				placeholder: "Выберите сотрудника...",
				allowClear: true,
			});
		},
	});
	$("#shift_id_hidden").val(shift_id);
});

$("#agency_employee_submit").on('click', function(e) {
	var agency_employee_id = $('#agency_employee_select').val()
	agency_employee_id = (agency_employee_id && agency_employee_id != 'none') ? +agency_employee_id : ''
	blockModalForm()
	OutRequests['shift-employee']({
		type: 'POST',
		data: {
			agency_employee_id: agency_employee_id,
			id: parseInt(SL_SELECTED_SHIFT),
			csrfmiddlewaretoken: csrf_token
		},
		success: function(data) {
			unblockModalForm()
			$('#modal_set_shift').modal('toggle');
			var table = $('#m_datatable').mDatatable();
			table.reload();
		},
		error: function(response){
			unblockModalForm()
			handleServerErrorInModal(response)
		}
	});
});

$('#modal_set_shift').on('shown.bs.modal', function() {
	$("#agency_employee_select option[value='" + employee_id + "']").prop('selected', true);
})

$('#generalSearch').on('keyup', function(e) {
	if(e.keyCode == 13) {
		if($(this).val().length >= 3)
			tableReloader.reload();
	}
	if($(this).val().length == 0)
		tableReloader.reload();
});