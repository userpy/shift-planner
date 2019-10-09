var UI = {}
document.body.addEventListener('click', function(e){
	var el = e.target.findElemByClass('validation-error')
	el && el.classList.remove('validation-error')
})