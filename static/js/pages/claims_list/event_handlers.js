// Обработчик смены клиента
$('#top_org_select_control').on('change', function () {
	tableReloader.reload();
});

// Обработчик нажатия на строку таблицы
$("div#ajax_data").on('click', 'tr.m-datatable__row--hover', function() {
	var row_id = $(this).attr('data-row');
	var claim_id = datatable.getDataSet()[row_id]['id'];
	window.location.href = DETAIL_PAGE_PREFIX + "claim/?id=" + claim_id;
});

// Обработчик нажатия кнопки экспорта
$("#export_claim_button").on('click', function() {
	var data = {
		'orgunit': orgSelect.selectedUnit.code,
		'organization_id': $('#organization_select').val() || '',
		'status_code': function(){
			//return $('#status_select').val();
			var status = $('#status_select').val();
			if (status === ''){
				return 'wait';
			}else{
				return status;
			}
		}(),
		'date': filters.date_select.getValueAsDate(),
		'pagination[page]': $("#ajax_data").mDatatable().getDataSourceParam('pagination')['page'],
		'pagination[perpage]': $("#ajax_data").mDatatable().getDataSourceParam('pagination')['perpage'],
		'[sort][field]': function(){
			if ('sort' in $("#ajax_data").mDatatable().getDataSourceParam()){
				return $("#ajax_data").mDatatable().getDataSourceParam('sort')['field'];
			}
		}() || '',
		'[sort][sort]': function(){
			if ('sort' in $("#ajax_data").mDatatable().getDataSourceParam()) {
				return $("#ajax_data").mDatatable().getDataSourceParam('sort')['sort'];
			}
		}() || '',
		xlsexport: true,
		format: 'json',
		_: new Date().getTime()
	};
	blobXHR({
		url:'/api-get-claims',
		data: data,
	})
})