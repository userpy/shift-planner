LoadingScreen = {
	_sceens: [],
	showFor: function(elem, params){
		//heightUntil - allScreen для высоты экрана или элемент, до которого будет растягиваться заглушка
		var params = params || {}
		if(!elem) throw new Error('LoadingScreen: calling without target element')
		var screens = LoadingScreen._sceens
		var alreadyCreated = false
		screens.forEach(function(screen){
			if(screen.elem == elem) alreadyCreated = true
		})
		if(alreadyCreated) return
		var div = createEl('div')
		div.classList.add('custom-loading-screen')
		div.innerHTML = custom_loading_screen_template.innerHTML
		var screen = {elem: elem, div: div, params: params}
		document.body.appendChild(div)
		LoadingScreen._updateDiv(screen)
		screens.push(screen)
		if(params.message) 
			div.$('.icon').textContent = params.message
		if(params.messageColor) 
			div.$('.icon').style.color = params.messageColor
		if(params.backgroundColor) 
			div.style.backgroundColor = params.backgroundColor
		if(params.zIndex) 
			div.style.zIndex = params.zIndex
	},
	_updateDiv: function(screen){
		var elem = screen.elem
		var div = screen.div
		var rect = elem.getBoundingClientRect()
		div.classList.toggle('hidden', !rect.height)
		div.style.top = rect.top + 'px'
		div.style.left = rect.left + 'px'
		div.style.width = rect.width + 'px'
		div.style.height = rect.height + 'px'
		if(screen.params.heightUntil == 'allScreen'){
			div.style.height = window.innerHeight - rect.top + 'px'
		}
	},
	hideFor: function(elem){
		var screens = LoadingScreen._sceens
		screens.forEach(function(screen){
			if(screen.elem == elem){
				screen.div.remove()
				screens.remove(screen)
			} 
		})
	},
	updateFor: function(elem){
		var screens = LoadingScreen._sceens
		screens.forEach(function(screen){
			if(screen.elem == elem){
				LoadingScreen._updateDiv(screen)
			}
		})
	}
}
addEventListener('resize', function(){
			LoadingScreen._sceens.forEach(function(screen){
				LoadingScreen._updateDiv(screen)
			})
		})