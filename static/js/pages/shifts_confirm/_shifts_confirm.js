var shift_confirm = new function(){
	this.morningStart = 6..hours
	this.lightDayStart = 14..hours
	this.nightStart = 18..hours
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
					return week.length * 100 /  this.monthDaysLength + '%'
				},
				onShiftClick: function(s){
					if(s.state == 'delete')  return
					if(this.areShiftsReadonly)  return
					var newS = new Shift(s)
					changedShifts = this.changedShifts.filter(function(s){
						return s.id != newS.id
					})
					if(s.state == 'wait') newS.state = 'accept'
					if(s.state == 'reject') newS.state = 'accept'
					if(s.state == 'accept') newS.state = 'reject'
					newS = shift_confirm.setShiftColor(newS)
					changedShifts.push(newS)
					this.changedShifts = changedShifts
					shift_confirm.generate()
				},
				confirmAction: function(){
					shift_confirm.performAction('accept')
				},
				rejectAction: function(){
					shift_confirm.performAction('reject')
				},
				backAction: function(){
					history.back()
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
				this.monthDayWidth = shift_confirm.calcWorkflowLineWidth() / this.monthDaysLength * Date.day +'px'
				this.headButtsLeftCss = shift_confirm.calcHeadButtsLeftPos()
			},
			updated: function(){
				this.$refs.table_body.scrollTop = this.bodyScrollPos
			}
		})
		this.vm = vm
		this.initEventListners()
	}
	var initComponents = function(){
		page_main_widget.components.forEach(function(c){c.init()})
	}
	var getInitialData = function(){
		return{
			compWrap: shift_confirm,
			changedShifts: [],
			tableHeaderHeightCss: 0,
			bodyPaddingTopCSS: 0,
			bodyPaddingBottomCSS: 0,
			workflowLineWidthCSS: 0,
			headButtsLeftCss: 0, // отступ слева у верхних таблицы
			monthDayWidth: 0,
			rowsHeight:{
				row: 54
			},
			monthDaysLength: 0,//количество дней в месяце
			bodyScrollPos: 0,
			start_dtime: Date.now(),
			zoomMode: 'week',
			scrollFixPadding: getScrollbarSize().width +'px',
			bodyHeightCss: 0,
			isLoading: true,
			rawRowsData: [],
			rawShiftsData: [],
			rawWorkloadData: [],
			blocks: [],
			daySumms: [],
			totalDaysSumm: 0,
			areShiftsReadonly: are_shifts_readonly,
			settings:{
				emptyTablePlaceholder: 'Нет данных для отображения'
			}
		}
	}
	this.setShiftColor = function(rs){
		var color
		if(rs.state == 'accept') color = '#0abb87'
		if(rs.state == 'reject') color = '#fd397a'
		if(rs.state == 'delete') color = 'grey'
		rs.color = color
		return new Shift(rs)
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
