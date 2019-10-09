var TableReloader = function(table){
	var timeout = null
	var count = 0
	this.reload = function(){
		clearTimeout(timeout)
		count++
		if(count > 30){
			count = 0
			throw new Error('too many calls')
		} 
		timeout = setTimeout(function(){
			clearTimeout(timeout)
			count = 0
			table.reload()
		}, 100)
	}
}