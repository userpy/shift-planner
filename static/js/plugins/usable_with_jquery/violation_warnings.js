/*
* Copyright © 2016 ООО «Верме»
* 
* Движок отображения всплывающих сообщений с описанием ошибки
*/
// сообщение выводится под элементом, если передан элемент,
// иначе выводится язычком сверху страницы
ViolationWarnings = {
	_warnings: [],
	showFor: function(elem, params){
		var cooldown = 3000
		var params = params || {}
		var key = elem || params.message || rd(0,1000)
		var warnings = ViolationWarnings._warnings
		var alreadyCreated = false
		warnings.forEach(function(warning){
			if(warning.key == key) alreadyCreated = true
		})
		if(alreadyCreated) return
		var div = createEl('div')
		div.classList.add('violation-warning')
		if(!elem) div.classList.add('from-top')
		div.innerHTML = '<div class="message"></div>'
		var warning = {key: key, elem: elem, div: div}
		document.body.appendChild(div)
		if(elem) ViolationWarnings._updateDiv(warning)
		warnings.push(warning)
		if(params.message) 
			div.ae$('.message').textContent = params.message
		if(params.type) div.ae$('.message').classList.add(params.type)
		setTimeout(function(){
			ViolationWarnings.hideFor(key)
		}, cooldown+200)
	},
	hideFor: function(key){
		var warnings = ViolationWarnings._warnings
		warnings.forEach(function(warning){
			if(warning.key == key){
				warning.div.remove()
				warnings.aeRemove(warning)
			} 
		})
	},
	updateFor: function(key){},
	_updateDiv: function(warning){
		var margin = 5 
		var elem = warning.elem
		var div = warning.div.ae$('.message')
		var rect = elem.getBoundingClientRect()
		div.classList.toggle('hidden', !rect.height)
		div.style.top = rect.top + rect.height + margin + 'px'
		div.style.left = rect.left + 'px'
	},
	forceClose: function(){
		ViolationWarnings._warnings.forEach(function(warning){
			warning.div.remove()
			ViolationWarnings._warnings.aeRemove(warning)
		})
	}
}
addEventListener('scroll', function(){
	ViolationWarnings._warnings.forEach(function(warning){
		if(warning.elem) ViolationWarnings._updateDiv(warning)
	})
})