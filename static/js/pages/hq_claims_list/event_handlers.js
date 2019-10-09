
// Обработчик смены клиента
$('#top_org_select_control').on('change', function () {
	tableReloader.reload();
});

// Обработчик изменения даты
$( "#date_select" ).change(function() {
	tableReloader.reload();
});

// Обработчик нажатия на строку таблицы
$("div#ajax_data").on('click', 'tr.m-datatable__row--hover', function() {
	var row_id = $(this).attr('data-row');
	var claim_id = datatable.getDataSet()[row_id]['id'];
	window.location.href = "/hq-claim/?id=" + claim_id;
});

// Фикс пропадания названия колонки
$(".m_datatable").on("m-datatable--on-layout-updated", function() {
	$('.m-datatable__cell[data-field="dt_created"]').removeAttr('style');
});

// Обработчик нажатия кнопки создания претензии
$("#create_claim_button").on('click', function() {
	window.location.href = "/hq-claim/";
});

// Обработчик нажатия кнопки экспорта
$("#export_claim_button").on('click', function() {
	var data = {
		'orgunit': orgSelect.selectedUnit.code,
		'agency_id': $('#agency_select').val() || '',
		'status_code': function() {
			var status = $('#status_select').val();
			if(status === '') {
				return 'wait';
			} else {
				return status;
			}
		}(),
		'date': filters.date_select.getValueAsDate(),
		'pagination[page]': $("#ajax_data").mDatatable().getDataSourceParam('pagination')['page'] || '',
		'pagination[perpage]': $("#ajax_data").mDatatable().getDataSourceParam('pagination')['perpage'] || '',
		'[sort][field]': function() {
			if('sort' in $("#ajax_data").mDatatable().getDataSourceParam()) {
				return $("#ajax_data").mDatatable().getDataSourceParam('sort')['field'];
			}
			return ''
		}(),
		'[sort][sort]': function() {
			if('sort' in $("#ajax_data").mDatatable().getDataSourceParam()) {
				return $("#ajax_data").mDatatable().getDataSourceParam('sort')['sort'];
			}
			return ''
		}(),
		xlsexport: true,
		format: 'json',
		_: new Date().getTime()
	}
	blobXHR({
		data: data,
		url: '/api-get-claims'
	})
})
$('body').on('orgunits:loaded orgunits:change', function(){
	if(orgSelect.selectedUnit.isHeadquater){
		$('#create_claim_button').show()
	}else{
		$('#create_claim_button').hide()
	}
})
