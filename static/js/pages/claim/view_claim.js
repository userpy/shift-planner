
$(document).ready(function(){
	$('#nav_close_claim').on('click', function(){
		if (confirm("Вы уверены, что хотите закрыть претензию?")) {
			actionClaim(claim_id, 'close');
		}
	});

	$('#nav_accept_claim').on('click', function(){
		if (confirm("Вы уверены, что хотите подтвердить согласие с претензией?")) {
			actionClaim(claim_id, 'accept');
		}
	});

	$('#nav_reject_claim').on('click', function(){
		if (confirm("Вы уверены, что хотите подтвердить отказ от претензии?")) {
			commentClaimReject(claim_id);
			//actionClaim(claim_id, 'reject', comment);
		}
	});

	$('#nav_reopen_claim').on('click', function(){
		if (confirm("Вы уверены, что хотите переоткрыть претензию?")) {
			actionClaim(claim_id, 'reopen');
		}
	});

	$('#nav_add_message').on('click', function(){
		messageClaim(claim_id);
	});

	$('#claim_add_message').on('click', function(){
		messageClaim(claim_id);
	});
})

