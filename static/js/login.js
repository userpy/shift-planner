var initLoginForm = function() {
	clearStorage()
	$("#m_login_signin_submit").click(function(t) {
		t.preventDefault();
		var e = $(this), a = $(".m-login__form");
		var data = a.serializeArray().reduce(function(obj, item) {
				obj[item.name] = item.value;
				return obj;
			}, {});
		a.validate({
			rules: {
				login: {
					required: !0
				},
				password: {
					required: !0
				},
			}
		}), a.valid() && (e.addClass("m-loader m-loader--right m-loader--light").attr("disabled", !0), $.ajax({
			url: '/auth/login/',
			method: "POST",
			headers: {
				'X-CSRFToken': Cookies.get('csrftoken')
			},
			contentType: 'json',
			data: JSON.stringify(data),
			success: function(t, i, n, r) {
				if (t.result === 'ok') {
					window.location.href = '/';
				} else {
					setTimeout(function() {
						e.removeClass("m-loader m-loader--right m-loader--light").attr("disabled", !1),
							function(t, e, a) {
								var i = $('<div class="m-alert m-alert--outline alert alert-' + e + ' alert-dismissible" role="alert">\t\t\t<button type="button" class="close" data-dismiss="alert" aria-label="Close"></button>\t\t\t<span></span>\t\t</div>');
								t.find(".alert").remove(), i.prependTo(t), mUtil.animateClass(i[0], "fadeIn animated"), i.find("span").html(a)
							}(a, "danger", "Неверное имя пользователя или пароль")
					}, 2e3)
				}
			},
			error: function(xhr, textStatus, error) {
					setTimeout(function() {
						e.removeClass("m-loader m-loader--right m-loader--light").attr("disabled", !1),
							function(t, e, a) {
								var i = $('<div class="m-alert m-alert--outline alert alert-' + e + ' alert-dismissible" role="alert">\t\t\t<button type="button" class="close" data-dismiss="alert" aria-label="Close"></button>\t\t\t<span></span>\t\t</div>');
								t.find(".alert").remove(), i.prependTo(t), mUtil.animateClass(i[0], "fadeIn animated"), i.find("span").html(a)
							}(a, "danger", xhr.responseJSON.error ? xhr.responseJSON.error.message : textStatus)
					}, 2e3)
			}
		}))
	})
};

jQuery(document).ready(function() {
	initLoginForm()
	$('.m-login__signin')[0].onkeydown = function(e){
		if(e.keyCode == 13) $('#m_login_signin_submit')[0].click()
	}
});

function clearStorage(){
	var keysToClear = [
		'orgTree_tree_'
	]
	var allKeys = []
	for ( var i = 0, len = localStorage.length; i < len; ++i ) {
		allKeys.push( localStorage.key(i))
	}
	allKeys.forEach(function(k){
		keysToClear.forEach(function(ktc){
			if(~k.indexOf(ktc)) localStorage.removeItem(k)
		})
	})
}