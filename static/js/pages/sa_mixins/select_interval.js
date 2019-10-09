function calcSelectionZoneCss(startCoords, currCoords){
	return {
		top: Math.min(startCoords.y, currCoords.y) +'px',
		left: Math.min(startCoords.x, currCoords.x) +'px',
		width: Math.abs(startCoords.x - currCoords.x)+'px',
		height: Math.abs(startCoords.y - currCoords.y) +'px',
	}
}
var selectIntervalMix = {
	data: function(){return{
		isSelectingViaMouse: false,
		selectionStartCoords: null,
		selectionCurrCoords: null,
		selectionZoneCss: null,
		clickedWhileEditing: false,
		mouseDownTimeStamp: 0,
	}},
	computed:{
		onMousemoveBt: function(){return this.onMousemove.bind(this)},
		onMouseupBt: function(){return this.onMouseup.bind(this)},
		onTabBlurBt: function(){return this.onTabBlur.bind(this)}
	},
	methods:{
		isEventEqClick: function(e){
			return e.timeStamp - this.mouseDownTimeStamp > 300
		},
		clearZoneSelection: function(){
			this.isSelectingViaMouse = false
			this.selectionStartCoords = null
			this.selectionCurrCoords = null
			this.selectionZoneCss = null
			document.body.style.userSelect = ''
		},
		onMousedown: function(e){
			this.mouseDownTimeStamp = e.timeStamp
			if(e.button) return
			this.selectionStartCoords = {x: e.clientX, y: e.clientY}
			if(this.editShiftData){
				this.clickedWhileEditing = e
				this.addDragEvents()
				return
			}
			this.isSelectingViaMouse = true
			this.selectionCurrCoords = {x: e.clientX, y: e.clientY}
			document.body.style.userSelect = 'none'
			this.clearHighlightRowsUnderZone()
			this.removeHoverSelectionFromDayAndRows()
			this.addDragEvents()
		},
		onMousemove: function(e){
			if(!this.isMousePressed){
				this.removeDragEvents()
				return
			}
			if(this.clickedWhileEditing){
				var sc = this.selectionStartCoords
				if(Math.max( Math.abs(e.clientX - sc.x) || Math.abs(e.clientY - sc.y)) < 50) return //слишком маленькая область
				clearUserSelectionOnPage()
				removeEventListener('mousemove', this.onMousemoveBt)
				this.editShiftData = null
				this.onMousedown(this.clickedWhileEditing)
				this.clickedWhileEditing = null
			} else if(!this.isSelectingViaMouse) return
			this.selectionCurrCoords = {x: e.clientX, y: e.clientY}
			this.selectionZoneCss = calcSelectionZoneCss(this.selectionStartCoords, this.selectionCurrCoords)
			this.highlightRowsUnderZone()
		},
		onMouseup: function(e){
			if(!this.isEventEqClick(e)) {
				this.exitCopyToPresent()
				this.removeDragEvents()
				return
			}
			this.exitSelection()
		},
		onTabBlur: function(){
			if(!this.isSelectingViaMouse) return
			this.exitSelection()
		},
		addDragEvents: function(){
			addEventListener('mousemove', this.onMousemoveBt)
			addEventListener('mouseup', this.onMouseupBt)
			addEventListener('blur', this.onTabBlur)
		},
		removeDragEvents: function(){
			removeEventListener('mousemove', this.onMousemoveBt) 
			removeEventListener('mouseup', this.onMouseupBt)
			removeEventListener('blur', this.onTabBlur)
		},
		exitSelection: function(){
			var compVm = this
			this.applySelection(function(){
				compVm.clearZoneSelection()
				compVm.removeDragEvents()
			})
		}
	},
}