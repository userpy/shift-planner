// Обработчики событий

// Кнопка
var onAcceptClick = function(){onButtonClick('accept');};
$("#accept-shift").on('click', onAcceptClick);

// Кнопка "Отклонить"
var onRejectClick = function(){onButtonClick('reject');};
$("#reject-shift").on('click', onRejectClick);

var isFirstClick = true
function onButtonClick(action){
	var shiftsData = shifts.map(function(s){
		return {id: s.id, state: s.state}
	})
	var isAnyRejected = shiftsData.some(function(sd){return sd.state == 'reject'})
	if(isAnyRejected || action == 'reject'){
		$('#modal_reject_confirm').modal({backdrop: true})
	} else {
		apply()
	}
	function apply(reject_reason, inPopup){
		if(inPopup && !reject_reason){
			handleNonServerErrorInModal('Нужно указать причину')
			return
		}
		if(outsource_enable){
			if(inPopup && !checkFormRequirments(ae$('#modal_reject_confirm')) )return
			var data = {
				"request_id": request_id,
				"shifts": JSON.stringify(shiftsData),
				"action": action,
				csrfmiddlewaretoken: csrf_token 
			}
			if(reject_reason) data.reject_reason = reject_reason
			OutRequests['update-request']({
				data: data,
				success: function (result) {
					window.location.href = "/requests-list/";
				},
				error: function (result) {
				}
			});
		}
	}
	if(isFirstClick){
		isFirstClick = false
		$('#modal_reject_confirm_btn').on('click', function(){

			apply($('#reject_reason').val(), true)
		})
	}
}