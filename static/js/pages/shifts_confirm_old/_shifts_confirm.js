var shift_confirm = new function(){

	var shift_confirm = this
	this.vm = null
	this.components = []
	this.init = function(){
		initComponents()
		var data = getInitialData()
		var vm = new Vue({
			el: '.shift_confirm_nest',
			template: '#shift_confirm_template',
			data: data,
			mixins: [],
			methods:{
				calcWeekWidth: function(week){
					if(this.zoomMode == 'week') return '100%'
					return week.length * 100 / topDateChanger.interval.month.duration * Date.day + '%'
				},
			},
			computed:{
				widgetBody: function(){
					return this.$refs["widget-body"]
				}
			},
			mounted: function(){
				this.bodyHeightCss = shift_confirm.calcBodyHeight()
				this.tableHeaderHeightCss = shift_confirm.calcHeadHeight() +'px'
				this.workflowLineWidthCSS = shift_confirm.calcWorkflowLineWidth() +'px'
				this.headButtsLeftCss = shift_confirm.calcHeadButtsLeftPos()
				this.monthDayWidth = shift_confirm.calcWorkflowLineWidth() / topDateChanger.interval.month.duration * Date.day +'px'
			},
			updated: function(){
				this.$refs.table_body.scrollTop = this.bodyScrollPos
			}
		})
		this.vm = vm
		this.initEventListners()
	}
	initComponents = function(){
		shift_confirm.components.forEach(function(c){c.init()})
	}
	getInitialData = function(){
		return{
			compWrap: shift_confirm,
			tableHeaderHeightCss: 0,
			bodyPaddingTopCSS: 0,
			bodyPaddingBottomCSS: 0,
			workflowLineWidthCSS: 0,
			headButtsLeftCss: 0, // отступ слева у верхних таблицы
			monthDayWidth: 0,
			rowsHeight:{
				row: 54
			},
			bodyScrollPos: 0,
			start_dtime: Date.now(),
			zoomMode: 'week',
			scrollFixPadding: getScrollbarSize().width +'px',
			bodyHeightCss: 0,
			isLoading: true,
			rows: [],
			daySumms: [],
			totalDaysSumm: 0,
		}
	}
}()
document.addEventListener("DOMContentLoaded", function(event) {
	shift_confirm.init()
});

var scrollBarSize
getScrollbarSize = function(){
	if(scrollBarSize){
		return {width: scrollBarSize.width, height: scrollBarSize.height}
	}
	var div = document.createElement('div')
	div.style.position = 'absolute'
	div.style.top = '90000px'
	div.style.overflow = 'scroll'
	document.body.appendChild(div)
	var width = div.getBoundingClientRect().width
	var height = div.getBoundingClientRect().height
	div.remove()
	scrollBarSize =  {width: width, height: height}
	return {width: width, height: height}
}
addEventListener('resize', function(){
	scrollBarSize = null
})
