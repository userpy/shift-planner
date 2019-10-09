// <!-- Блок валидации форм -->

var FormControls = {
	init: function() {
		$("#modal_create_message_form").submit(function(e){e.preventDefault()}).validate({
			rules: {
				claim_id: {
					required: !0
				},
				claim_user_name: {
					required: !0
				},
				claim_message_text: {
					required: !0,
					minlength: 2,
					maxlength: 1000
				}
			},
			invalidHandler: function(e, r) {
				var i = $("#modal_create_message_form_msg");
				$('body').scrollTo(i, null, {offset: -200})
			},
			submitHandler: function(e) {
				sendFormData();
			}
		});
		$("#modal_comment_claim_reject_form").submit(function(e){e.preventDefault()}).validate({
			rules: {
				reject_claim_id: {
					required: !0
				},
				reject_claim_user_name: {
					required: !0
				},
				reject_claim_message_text: {
					required: !0,
					minlength: 2,
					maxlength: 1000
				}
			},
			invalidHandler: function(e, r) {
				e.preventDefault()
				var i = $("#modal_comment_claim_reject_form_msg");
				i.removeClass("m--hide").show(),
				$('body').scrollTo(i, null, {offset: -200})
			},
			submitHandler: function(form, e) {
				e.preventDefault()
				actionClaim($("#reject_claim_id").val(), 'reject', $("#reject_claim_message_text").val())
				// Очищаем форму
				// И закрывваем модальное окно
				clearForm();
				$("#modal_comment_claim_reject").modal('toggle');
			}
		});
		$("#claim_create_form").submit(function(e){e.preventDefault()}).validate({
			rules: {
				city_select: {
					required: !0
				},
				agency_select: {
					required: !0
				},
				organization_select: {
					required: !0
				},
				type_select: {
					required: !0
				},
				claim_message: {
					required: !0,
					minlength: 2,
					maxlength: 1000
				}
			},
			invalidHandler: function(e, r) {
				var i = $("#claim_create_form_msg");
				i.removeClass("m--hide").show()
				$('body').scrollTo(i, null, {offset: -200})
			},
			submitHandler: function(form, e) {
				e.preventDefault()
				if (fileform.length < 1){
					var i = $("#claim_create_form_msg");
					i.removeClass("m--hide").show()
					$('body').scrollTo(i, null, {offset: -200})
					return;
				}
				var claim_type = $('#type_select');
				var claim_organization = $('#organization_select');
				var claim_agency = $('#agency_select');
				var claim_message = $('#claim_message');

				// Данные для сохранения претензии
				var data = {
					claim_type_id: claim_type.val(),
					organization_id: claim_organization.val(),
					agency_id: claim_agency.val(),
					text: claim_message.val(),
					guid: guid,
					csrfmiddlewaretoken: csrf_token
				};
				var filesSended = 0
				function goToClaimPage(claim_id){
					if(filesSended >= fileform.length)
					window.location.href = "/hq-claim/?id=" + claim_id;
				}
				blockForm($('#claim_create_form'))
				$.ajax({
					type: 'POST',
					url: '/api-create-claim/?format=json',
					data: data,
					success: function (data) {
						// Если успешно отправили сообщение
						// То отправляем вложенные файлы, если они есть
						var claim_id = data.id
						fileform.forEach(function(item) {
							$.ajax({
								type: 'POST',
								url: '/api-create-claim-attachment/?format=json',
								data: {
									claim_id: claim_id,
									filename: item.filename,
									file: item.data.split(',')[1],
									csrfmiddlewaretoken: csrf_token
								},
								success: function (data) {
									filesSended++
									goToClaimPage(claim_id)
								}
							});
						});
					},
					error: function(){
						// Вывод ошибок сервера
						unblockForm($('#claim_create_form'))
						var i = $("#claim_create_form_msg");
						i.removeClass("m--hide").show(),
							mApp.scrollTo(i, -200)
					}
				});
			}
		})
	}
};
jQuery(document).ready(function() {
	FormControls.init()
});

// <!-- / Блок валидации форм -->