var QUOTA_ID
var EDIT_QUOTA_MODE
$('#store_select_pp').select2({placeholder: "Магазин", allowClear:true})
$('#promo_select_pp').select2({placeholder: "Вендор", allowClear:true})
$('#area_select_pp').select2({placeholder: "Зона магазина", allowClear:true})
$('#add_quota_dd_button').on('click', function(){ showEditQuotaPp() })
var updatePpStoreSelect = function(stores){
	$('#store_select_pp').empty()
	stores.forEach(function(d){
		var newOption = new Option(d.text, d.id, false, false)
		$('#store_select_pp').append(newOption)
	})
}


var showEditQuotaPp = function(rowData){
	$('#modal_edit_quota').modal({backdrop: true})

	var deleteButt = ae$('#mass_delete_quota_button')
	var submitButt = ae$('#edit_quota_submit_button')
	prepareButtForLoadingState(deleteButt)
	prepareButtForLoadingState(submitButt)
	hideWarningInModal()
	toggleModalControls('default')
	unBlockModalBody()

	$('#quota_end').css({'border-color': '#ebedf2'})
	$('#value_input').css({'border-color': '#ebedf2'})

	if(!rowData) {
		EDIT_QUOTA_MODE = 'creation'
		$('#quota_modal_title')[0].textContent = 'Создание'
		$('#value_input').val(null)
		$('#value_ext_input').val(null)
		$('#edit_quota_delete_button').css({display: 'none'})
		// Установка дат
		$('#quota_start').datepicker('setDate', new Date(topDateChanger.interval.selected_start_dtime).startOfMonth())
		$('#quota_end').datepicker('setDate', null)
	}else{
		EDIT_QUOTA_MODE = 'edition'
		$('#quota_modal_title')[0].textContent = 'Редактирование'
		$('#value_input').val(rowData.value)
		$('#value_ext_input').val(rowData.value_ext)
		$('#edit_quota_delete_button').css({display: ''})
		// Установка дат
		if (rowData.start != 'null') $('#quota_start').datepicker('setDate', rowData.start.replace(/(\d+)[-](\d+)[-](\d+)/, '$2 $1'));
		if (rowData.end != 'null') $('#quota_end').datepicker('setDate', rowData.end.replace(/(\d+)[-](\d+)[-](\d+)/, '$2 $1'))
			else $('#quota_end').datepicker('setDate', null)
	}
	blockModalForm()
	$('#promo_select_pp').empty()
	$('#area_select_pp').empty()
	OutRequests['get-quota-areas-promos']({
		data:{
			orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null}
		},
		success: function(resp){
			unblockModalForm()

			$('#store_select_pp').val($('#store_select_pp option').val()).trigger('change')
			$('#promo_select_pp').val(null)
			$('#area_select_pp').val(null)
			resp.area_list.forEach(function(d){
				var newOption = new Option(d.text, d.id, false, false)
				$('#area_select_pp').append(newOption)
			})
			resp.promo_list.forEach(function(d){
				var newOption = new Option(d.text, d.id, false, false)
				$('#promo_select_pp').append(newOption)
			})
			if(EDIT_QUOTA_MODE != 'creation'){
				$('#area_select_pp').val(rowData.area_id)
				$('#area_select_pp').select2().trigger('change')
				$('#promo_select_pp').val(rowData.promo_id)
				$('#promo_select_pp').select2().trigger('change')
				$('#store_select_pp').val(rowData.store_id)
				$('#store_select_pp').select2().trigger('change')
			}

		}, 
		error: function(response){
			unblockModalForm()
			handleServerErrorInModal(response)
		}
	})
}
clearValidationHiglight = function(){
	$('#quota_end').css({'border-color': '#ebedf2'})
	$('#value_input').css({'border-color': '#ebedf2'})
	$('#value_ext_input').css({'border-color': '#ebedf2'})
}

var applyQuotaFromEdit = function(){
	//blockModalForm()
	clearValidationHiglight()
	var endDtime = $('#quota_end').data('datepicker').getDate() ? $('#quota_end').data('datepicker').getDate().getTime() : null
	var startDtime = $('#quota_start').data('datepicker').getDate() ? $('#quota_start').data('datepicker').getDate().getTime() : null
	if(endDtime && startDtime == endDtime){
		endDtime = new Date(endDtime).setMonth(new Date(endDtime).getMonth()+1) - Date.day
	}
	var data = {
		promo_id: $('#promo_select_pp').val(),
		store_id: $('#store_select_pp').val(),
		area_id:$('#area_select_pp').val(),
		quota_type: 'fix',
		value: $('#value_input').val(),
		value_ext: $('#value_ext_input').val(),
		start: startDtime ? new Date(startDtime).toISODateString() : '',
		end: endDtime ? new Date(endDtime).toISODateString() : '',
		mode: 'apply',
		csrfmiddlewaretoken: csrf_token,
	}
	if(EDIT_QUOTA_MODE != 'creation') data.quota_id = QUOTA_ID
	OutRequests['set-quota']({
		data: data,
		success: function(resp){
			$('#modal_edit_quota').modal('hide')
			unblockModalForm()
			tableReloader.reload()
		}, 
		error: function(response){
			unblockModalForm()
			handleServerErrorInModal(response)
		}
	})
}
$('#edit_quota_delete_button').on('click', function(){
	checkBeforeEdit('delete')
})
$('#edit_quota_submit_button').on('click', function(){
	checkBeforeEdit('apply')
})
$('#edit_quota_cancel_action_button').on('click', function(){
	unBlockModalBody()
	toggleModalControls('default')
})

function checkBeforeEdit(action){
	if(action == 'delete'){
		var deleteButt = ae$('#edit_quota_delete_button')
		toggleButtonLoadingState(deleteButt, true)
		blockModalForm()
		var data = {
			quota_ids: JSON.stringify([QUOTA_ID]),
			mode: 'check',
		}
		OutRequests['delete-quota']({
			data: data,
			success: function(resp){
				unblockModalForm()
				toggleButtonLoadingState(deleteButt, false)
				toggleModalControls('confirm')
				ae$('#edit_quota_submit_action_button').onclick = deleteQuotaFromEdit
				if(resp.result){
					ae$('.controls-tip').textContent = 'Операция приведет к отмене '+ resp.result +' смен, продолжить?'
				} else {
					ae$('.controls-tip').textContent = 'Квота может быть безопасно удалена, продолжить?'
				}
			}, 
			error: function(response){
				unblockModalForm()
				toggleButtonLoadingState(deleteButt, false)
				toggleModalControls('default')
				handleServerErrorInModal(response)
			}
		})
		return
	} else{
		if(EDIT_QUOTA_MODE != 'creation'){
			var submitButt = ae$('#edit_quota_submit_button')
			toggleButtonLoadingState(submitButt, true)
			blockModalForm()
			var data = {
				promo_id: $('#promo_select_pp').val(),
				store_id: $('#store_select_pp').val(),
				area_id:$('#area_select_pp').val(),
				quota_type: 'fix',
				value: $('#value_input').val(),
				value_ext: $('#value_ext_input').val(),
				start: $('#quota_start').data('datepicker').getDate() ? $('#quota_start').data('datepicker').getFormattedDate('yyyy-mm-dd') : '',
				end: $('#quota_end').data('datepicker').getDate() ? $('#quota_end').data('datepicker').getFormattedDate('yyyy-mm-dd') : '',
				mode: 'check',
				csrfmiddlewaretoken: csrf_token,
			}
			if(EDIT_QUOTA_MODE != 'creation') data.quota_id = QUOTA_ID
			OutRequests['set-quota']({
				data: data,
				success: function(resp){
					unblockModalForm()
					//blockModalBody()
					toggleButtonLoadingState(submitButt, false)
					if(resp.result){
						toggleModalControls('confirm')
						ae$('.controls-tip').textContent = 'Операция приведет к отмене '+ resp.result +' смен, продолжить?'
						ae$('#edit_quota_submit_action_button').onclick = applyQuotaFromEdit
					} else {
						applyQuotaFromEdit()
					}
				}, 
				error: function(response){
					unblockModalForm()
					handleServerErrorInModal(response)
					toggleButtonLoadingState(submitButt, false)
				}
			})
		} else {
			applyQuotaFromEdit()
		}
	}
}