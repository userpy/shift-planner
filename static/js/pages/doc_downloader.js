$('#download_employees_docs').on('click', function(){
	blockUILoading()
	if(datatable.getSelectedRecords().length){
		massLoadDocs(get_selected_employees())
	}else{
		var data = {
			'orgunit': orgSelect.selectedUnit.code,
			'state': function(){
				return filters.status_select ? filters.status_select.getValue() : ''
			}(),
			'violation_ids': function(){
				return filters.violation_select ? filters.violation_select.getValueAsFixedArrStr() : ''
			}(),
			'pagination[page]': $(".m-datatable").mDatatable().getDataSourceParam('pagination')['page'],
			'pagination[perpage]': $(".m-datatable").mDatatable().getDataSourceParam('pagination')['perpage'],
			'[sort][field]': function(){
				if ('sort' in $(".m-datatable").mDatatable().getDataSourceParam()){
					return $(".m-datatable").mDatatable().getDataSourceParam('sort')['field'];
				}
			}() || '',
			'[sort][sort]': function(){
				if ('sort' in $(".m-datatable").mDatatable().getDataSourceParam()) {
					return $(".m-datatable").mDatatable().getDataSourceParam('sort')['sort'];
				}
			}() || '',
			'datatable[query][generalSearch]': function() {
				if($('#generalSearch').val().length >= 3)
						return $('#generalSearch').val();
				return '';
			}(),
			medical_export : true,
			medical_export_code: request_page_party + '_employees_list',
			format: 'json',
			_: new Date().getTime()
		}
		if(topDateChanger){
			data.month = new Date(topDateChanger.interval.selected_start_dtime).toISODateString()
			data.start = new Date(topDateChanger.interval.selected_start_dtime).toISODateString()
			data.end = new Date(topDateChanger.interval.selected_end_dtime).toISODateString()
		}
		if(request_page_party == 'client') data.agency_id = function(){
				return filters.agency_select.getValue();
			}()

		$.ajax({
			url:'/api-employees-list',
			data: data,
			success: function(r){
				if(r.type == 'success'){
					blobXHR({url: verme_docs_url + r.url, file:{name: 'Медкнижки.zip'}}, null, function(r){alert(l10n[r.message])})
				}else{
					unBlockUILoading()
					alert(l10n[r.message])
				}
			},
			error: function(r){
				unBlockUILoading()
				alert('Ошибка запроса')
			}
		})
	}
})
$('#nav_download_employee_docs').on('click', function(){
	massLoadDocs([employee_id])
})

function massLoadDocs(employee_ids){
	blockUILoading()
	OutRequests['get-docs-archive']({
		data: {
			employee_ids: JSON.stringify(employee_ids),
			orgunit: orgSelect.selectedUnit.code,
			month: topDateChanger ? new Date(topDateChanger.interval.selected_start_dtime).toISODateString() : '',
			start: topDateChanger ? new Date(topDateChanger.interval.selected_start_dtime).toISODateString() : '',
			end: topDateChanger ? new Date(topDateChanger.interval.selected_end_dtime).toISODateString() : '',
			'_': new Date().getTime()
		},
		success: function(r){
			if(r.type == 'success'){
				blobXHR({url: verme_docs_url + r.url, file:{name: 'Медкнижки.zip'}}, null, function(r){alert(l10n[r.message])})
			}else{
				unBlockUILoading()
				alert(l10n[r.message])
			}
		},
		error: function(r){
			unBlockUILoading()
			alert('Ошибка запроса')
		}
	})
}