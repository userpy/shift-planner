window.addEventListener('load', asefy)
function asefy(){
	var textareas = document.getElementsByClassName('acefyelable-textarea')
	if( !textareas.length ) return
	for( i=0; i<textareas.length; i++) initArea(textareas[i])
	
	function initArea(textarea){
		var mode = textarea.dataset.mode
		script = document.createElement('script')
		script.type = 'text/javascript'
		script.async = true
		script.src = '/static/admin/js/ace/mode-'+ mode +'.js'
		document.getElementsByTagName('head')[0].appendChild(script)
		script.onload = function(){
			var parent = textarea.parentElement
			var div = document.createElement('div')
			div.style.width = '512px'
			div.style.height = '384px'
			div.style.display = 'inline-block'
			parent.appendChild(div)
			var editor = ace.edit(div)
			editor.getSession().setMode('ace/mode/'+ mode)
			textarea.style.display = 'none'
			editor.setValue(textarea.value)
			editor.clearSelection()
			editor.getSession().addEventListener('change', function () {
				textarea.value = editor.getSession().getValue()
			})
		}
	}
}