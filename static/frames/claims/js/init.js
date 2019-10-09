new function(){
	function dmy(date){
		var d = new Date(date)
		return d.getDate().toLen(2) +'.'+ (d.getMonth()+1).toLen(2) +'.'+ d.getFullYear()
	}
	function hm(date){
		var d = new Date(date)
		var hours = d.getHours()
		var minutes = "0" + d.getMinutes()
		return hours + ':' + minutes.substr(-2)
	}
	function dmyhm(date){
		return dmy(date)+ ' ' +hm(date)
	}
	Vue.filter('fullDate', function(time){
		return dmyhm(time)
	})
	UI.vueComponents.init()
	claims.init()
}()