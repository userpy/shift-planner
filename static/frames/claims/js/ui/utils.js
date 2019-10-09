UI.utils = {}
UI.utils.calcPosForDropDown = function(params, ddWidth, ddHeight, margin){
	//params: ClientRect
	var tWidth = document.body.clientWidth
	var tHeight = document.body.clientHeight
	var margin = margin || 0
	var x = 0
	var y = 0
	//если дропдаун можно показать вниз
	if(params.bottom + ddHeight < tHeight){
		//если он влезает по ширине
		if(params.left + ddWidth < tWidth){
			x = params.left
			y = params.bottom
		} else {
			x = params.right - ddWidth
			y = params.bottom
		}
	} else {
		if(params.left + ddWidth < tWidth){
			x = params.left
			y = params.top - ddHeight - margin
		} else {
			x = params.right - ddWidth
			y = params.top - ddHeight - margin
		}
	}
	return {x:x, y:y}
}
UI.utils.getScrollbarSize = function(){
	if(UI.scrollBarSize){
		return {width: UI.scrollBarSize.width, height: UI.scrollBarSize.height}
	}
	var div = document.createElement('div')
	div.style.position = 'absolute'
	div.style.top = '90000px'
	div.style.overflow = 'scroll'
	document.body.appendChild(div)
	var width = div.getBoundingClientRect().width
	var height = div.getBoundingClientRect().height
	div.remove()
	UI.scrollBarSize =  {width: width, height: height}
	return {width: width, height: height}
}
addEventListener('resize', function(){
	UI.scrollBarSize = null
})