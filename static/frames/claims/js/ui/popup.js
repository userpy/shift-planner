UI.showPopup = function(data){
	// title, body, afterRender, onSubmit, onAbort, onApply,
	// prevNextButts, isPrevEnabled, isNextEnabled, onPrev, onNext
	if(!data) data = {}
	var div = document.createElement('div')
	div.classList.add('big-popup-wrap')
	div.classList.add('pp-closer')
	div.innerHTML = ''+
		'<div class="pp-closer">'+
			'<div class="pp-closer">'+
				'<div id="main_popup_content" class="big-popup-self"></div>'+
			'</div>'+
		'</div>'
	document.body.appendChild(div)
	var buttPrev = ''
	var buttNext = ''
	if (data.prevNextButts) buttPrev = '<button class="pp-prev fa fa-caret-left '+ ( data.isPrevEnabled ? '':'disabled' )+'"></button> '
	if (data.prevNextButts) buttNext = '<button class="pp-next fa fa-caret-right '+( data.isNextEnabled ? '':'disabled' )+'"></button> '
	main_popup_content.innerHTML = ''+
		'<div class="pp-title cf '+( data.prevNextButts? 'prev-next-butts' : '' )+'">'+
			'<div class="title-inner">'+
				buttPrev +
				'<div id="pp_title_content">'+(data.title|| 'РЎРѕРѕР±С‰РµРЅРёРµ')+'</div>'+
				buttNext +
				'<div id="pp_close" class="pp-closer">&#10005;</div>'+
			'</div>'+
		'</div>'+
		'<div class="pp_main">'+
			(data.body|| '') +
		'</div>'
	$('.big-popup-wrap').addEventListener('click', closePopup)
	pp_close.addEventListener('click', closePopup)
	if(data.afterRender) data.afterRender()

	function closePopup(e){
		if(e.target.classList.contains('pp-closer')){
			//С‚РєРЅСѓР»Рё С‚РѕС‡РЅРѕ РІ РєРЅРѕРїРєСѓ Р·Р°РєСЂС‹С‚РёСЏ
			closePp()
			return
		}
		if(e.target.classList.contains('pp-submiter')){
			submitPopup(e)
			return
		}
		if(e.target.classList.contains('pp-remover')){
			removeThroughPopup(e)
			return
		}
		if(e.target.classList.contains('pp-apply')){
			applyPopup(e)
			return
		}
		if(e.target.classList.contains('pp-prev') && !e.target.classList.contains('disabled')){
			data.onPrev(e)
			return
		}
		if(e.target.classList.contains('pp-next') && !e.target.classList.contains('disabled')){
			data.onNext(e)
			return
		}
		if(e.target.findElemByClass('big-popup-self')){
			//С‚РєРЅСѓР»Рё РєСѓРґР°-С‚Рѕ РІРЅСѓС‚СЂРё РїРѕРїР°РїР°
			var closer = e.target.findElemByClass('pp-closer')
			if(closer.findElemByClass('big-popup-self')){
				//С‚РєРЅСѓР»Рё РІ Р·Р°РєСЂС‹РІР°С€РєСѓ, РєРѕС‚РѕСЂР°СЏ РІРЅСѓС‚СЂРё РїРѕРїР°РїР°
				closePp()
				return
			} else {
				return
			}
		}
		function closePp(){
			var continueClosing = true
			if(data.onAbort) continueClosing = data.onAbort()
			if(continueClosing) if($('.big-popup-wrap'))$('.big-popup-wrap').parentNode.removeChild($('.big-popup-wrap'))
		}
	}
	function submitPopup(e){
		if(e && !e.target.classList.contains('pp-submiter')){
			return
		}
		var continueClosing = data.onSubmit()
		if(continueClosing)  if($('.big-popup-wrap'))$('.big-popup-wrap').parentNode.removeChild($('.big-popup-wrap'))
	}
	function removeThroughPopup(e){
		if(e && !e.target.classList.contains('pp-remover')){
			return
		}
		var continueClosing = true
		if(data.onRemove) continueClosing = data.onRemove()
		if(continueClosing) if($('.big-popup-wrap'))$('.big-popup-wrap').parentNode.removeChild($('.big-popup-wrap'))
	}
	function applyPopup(e){
		if(e && !e.target.classList.contains('pp-apply')){
			return
		}
		if(data.onApply) data.onApply()
	}
}
// end popup core