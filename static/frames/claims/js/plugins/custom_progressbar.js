InitCustomProgressbar = function(elem){
	elem.classList.add('custom-progressbar')
	elem.innerHTML = ''+
		'<div class="bar"></div>'+
		'<div class="done-total">'+
			'<span class="done"></span><span class="total"></span>'+
		'</div>'
	elem.setPercents = function(percents, done, total){
		elem.$('.bar').style.width = percents + '%'
		if(typeof(total) !== 'undefined'){
			elem.$('.done').textContent = done +'/'
			elem.$('.total').textContent = total
		}
	}
}