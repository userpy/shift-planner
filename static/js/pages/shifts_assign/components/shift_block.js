page_main_widget.components.push(new function(){
	this.init = function(){
		Vue.component('sa-shift-block', {
			name: 'sa-shift-block',
			props: ['shift', 'on-click', 'day-shifts', 'zoom-mode', 'row', 'month-day-width', 'comp-wrap', 'tooltip'],
			template: '\
				<div class="shift "\
					:class="{\'zoom-week\': zoomMode == \'week\', \
									\'zoom-month\': zoomMode == \'month\', \
									\'ver-flex-child-long\': zoomMode == \'month\', \
								}"\
					:style="{\
						left: leftCss,\
						width: widthCss,\
						height: heightCss,\
					}"\
					@click="onClick && onClick(localShift, $event)">\
					<div class="shift-inner"\
						:style="{background: shift.color || row.area.color || \'black\'}">\
						<div class="time" :title="localTooltip">\
							<template v-if="isFullTimeVisible">\
								<span class="time-start" :text-content.prop="localShift.start_time | timeDeltaHM">\
								</span>&nbsp;- <span class="time-end" :text-content.prop="localShift.end_time | timeDeltaHM"></span>\
							</template>\
							<template v-if="!isFullTimeVisible">\
								<span class="time-start" \
									:text-content.prop="localShift.start_time | timeDeltaH"\
								></span>-<span class="time-end" \
									:text-content.prop="localShift.end_time | timeDeltaH"\
								></span><i class="fa fa-user" v-if="localShift.employee" :class="ownerClass"></i>\
							</template>\
							<span class="owner-name" v-if="isEmplNameVisible" v-text="localShift.employee.text" :class="ownerClass"></span>\
						</div>\
					</div>\
				</div>\
			',
			computed: {
				localTooltip: function(){
					return this.tooltip ? this.tooltip : this.localShift.employee ? this.localShift.employee.text : ''
				},
				localShift: function(){return new Shift(this.shift)},
				leftCss: function(){
					return timeToPercents(Math.max( (this.localShift.start_time - this.compWrap.morningStart), 0), this.compWrap )
				},
				widthCss: function(){
					// var allDayLength = 1..day - shift_assign.morningStart
					// var alpha = allDayLength / 1..day //во сколько раз уменьшили день, надо уменьшить и смену
					// return timeToPercents(this.shift.duration * alpha)
					return this.zoomMode == 'week' ? timeToPercents(this.localShift.duration * 0.95, this.compWrap) : this.monthDayWidth+'!important'
				},
				heightCss: function(){
					if(this.zoomMode != 'month') return ''
					switch(this.dayShifts.length){
						case 1:
							return '100%'
						case 2:
							return '50%'
						case 3:
							return '33%'
					}
				},
				isEmplNameVisible: function(){
					if(this.zoomMode != 'month' && this.localShift.employee) return true
					if(!this.localShift.employee) return false
					if(this.dayShifts.length > 2) return false
					return true
				},
				isFullTimeVisible: function(){
					return this.zoomMode != 'month' || this.dayShifts.length == 1
				},
				ownerClass: function(){
					return {
						'm--font-danger': this.shift.has_violations
					}
				}
			},
		})
		function timeToPercents(delta, compWrap){
			var allDayLength = 1..day - compWrap.morningStart
			return delta / allDayLength * 100 + '%'
		}
	}
}())