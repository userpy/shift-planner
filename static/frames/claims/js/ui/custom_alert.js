UI.alert = function(message, title, noclose){
	var title = title || 'РџСЂРµРґСѓРїСЂРµР¶РґРµРЅРёРµ'

	if(Model.DEBUG && noclose) noclose = false
	var params = {
		'title': title,
		'body': message + ( !noclose ? '<br><br><button class="pp-closer">РћРљ</button>' : ''),
	}
	if(noclose){
		params.onAbort = function(){return false}
		params.afterRender = function(){$('#pp_close').classList.add('hidden')}
	}
	if($('.pp_main')) return //РїРѕРїР°Рї СѓР¶Рµ РµСЃС‚СЊ
	UI.showPopup(params)
	if($('.pp_main').offsetWidth > document.body.offsetWidth*0.3) $('.pp_main').style.width = document.body.offsetWidth*0.3 + 'px'
	if($('.pp_main').offsetWidth < 300) $('.pp_main').style.width = '300px'
}

UI.alertAppError = function(message){
	var title
	var message
	var long_description = ''
	if(typeof(message) == 'string'){
		message = message
		UI.alert(
		message+'<br><br><button onclick="location.reload()">РћР±РЅРѕРІРёС‚СЊ</button>',
		title,
		true
		)
	}else{
		var locale
		if(message){
			locale = L10n.messages.getDescriptionFor(message.name || ('type:'+message.type))
			long_description = message.long_description
		}else{
			locale = L10n.messages.getDescriptionFor()
		} 
		UI.alert(
			locale.message+'<div class="pp-error-long-descr hidden">'+long_description
				+'</div><br><br><button onclick="location.reload()">РћР±РЅРѕРІРёС‚СЊ</button>'+
				(long_description ? 
					'<span class="inline-text-button link pp-closer" style="margin-left:20px; padding-top: 10px;"'+
					'onclick="UI.alertAppError.expandDesrc()">РџРѕРєР°Р·Р°С‚СЊ РґРµС‚Р°Р»Рё</span>'
				:''),
			locale.title,
		true
	)
	}
}
UI.alertAppError.expandDesrc = function(){
	$(".pp-error-long-descr").classList.remove("hidden")
}
UI.confirm = function(message, onOk, onAbort){
	//message, onOk, onAbort
	var params = {
		'title': 'РџРѕРґС‚РІРµСЂРґРёС‚Рµ РґРµР№СЃС‚РІРёРµ',
		'body': message + '<br><br>'+
			'<button class="pp-submiter f_l">РћРє</button>'+
			'<button class="pp-closer inline-text-button borderless link f_l" style="margin-left: 10px">РћС‚РјРµРЅР°</button>'+
			'<br clear="all">',
		'onSubmit': onOk,
		'onAbort': onAbort ? onAbort : function(){return true},
	}
	if($('.pp_main')) return //РїРѕРїР°Рї СѓР¶Рµ РµСЃС‚СЊ
	UI.showPopup(params)
	if($('.pp_main').offsetWidth > document.body.offsetWidth*0.3) $('.pp_main').style.width = document.body.offsetWidth*0.3 + 'px'
	if($('.pp_main').offsetWidth < 300) $('.pp_main').style.width = '300px'
}