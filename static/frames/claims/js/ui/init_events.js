UI.initEvents = function(view, key){
	var events = view.events
	if(key) events = events[key]
	var ok = Object.keys(events)
	for(var i = 0; i< ok.length; i++){
		var type = ok[i]
		var inEvents = events[ok[i]]
		var inOk = Object.keys(inEvents)
		try{
			if(type != 'custom'){
				for(var j=0; j<inOk.length; j++){
					$(inOk[j]).addEventListener(type, inEvents[inOk[j]])
				}
			} else {
				for(var j=0; j<inOk.length; j++){
					addEventListener(inOk[j], inEvents[inOk[j]])
				}
			}
		}catch(e){
			console.warn('Развешивание эвентов: нет такого элемента: '+ inOk[j])
		}
	}
}
UI.removeEvents = function(view, key){
	var events = view.events
	if(key) events = events[key]
	var ok = Object.keys(events)
	for(var i = 0; i< ok.length; i++){
		var type = ok[i]
		var inEvents = events[ok[i]]
		var inOk = Object.keys(inEvents)
		try{
			if(type != 'custom'){
				for(var j=0; j<inOk.length; j++){
					$(inOk[j]).removeEventListener(type, inEvents[inOk[j]])
				}
			} else {
				for(var j=0; j<inOk.length; j++){
					removeEventListener(inOk[j], inEvents[inOk[j]])
				}
			}
		}catch(e){
			console.warn('Сброс эвентов: нет такого элемента: '+ inOk[j])
		}
	}
}
