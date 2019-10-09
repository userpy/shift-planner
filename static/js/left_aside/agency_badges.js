document.addEventListener('DOMContentLoaded', function() {
	// обновление счетчиков
	$('body').on('orgunits:loaded', function(){
		$.ajax({
			type: 'get',
			cache: false,
			url: '/api-get-agency-user-counters/?format=json&orgunit_id='+ orgSelect.selectedUnit.code,
			success: function(r){
				$('#request_count_badge')[0].textContent = r.request_count
				$('#claims_count_badge')[0].textContent = r.claim_count
				$('#request_count_badge').css({
					'visibility': r.request_count ? 'visible': 'hidden'
				})
				$('#claims_count_badge').css({
					'visibility': r.claim_count ? 'visible': 'hidden'
				})
			}
		})
	})
});



