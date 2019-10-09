page_main_widget.components.push(new function(){
	this.init = function(){
		Vue.component('sa-copy-to-future', {
			name: 'sa-copy-to-future',
			props: ['shifts', 'get-selected-week-start', 'on-ok', 'on-cancel', 'widget-body'],
			template: '\
			<div class="sa-dropdown copy-to-future-dd" :style="{top: cssTop, left: cssLeft}" ref="ddBody">\
				<div class="sse-row head-row">\
					<b>Повторить интервал</b>\
					<div class="btn m-btn--pill btn-secondary btn-sm" @click="onCancel"><i class="fa fa-times"></i></div>\
				</div>\
				<div class="sse-row time-row">\
					<vue-jq-date-range-picker\
						:start_dtime="start_dtime"\
						:end_dtime="end_dtime"\
						:min_dtime="\'today\'"\
						:on-change="onRangeChange"\
					></vue-jq-date-range-picker>\
				</div>\
				<div class="sse-row controls-row" >\
					<button class="btn btn-success" @click="onSubmit">ОК</button>\
				</div>\
			</div>\
			',
			data: function(){return{
				cssTop: 0,
				cssLeft: 0,
				start_dtime: Math.max(new Date().startOfWeek().getTime(), this.getSelectedWeekStart()) + 1..week,
				end_dtime: Math.max(new Date().startOfWeek().getTime(), this.getSelectedWeekStart()) + 1..week + 6..day,
			}},
			methods: {
				onRangeChange: function(start, end){
					this.start_dtime = start
					this.end_dtime = end
				},
				onSubmit: function(){
					this.onOk(this.start_dtime, this.end_dtime)
				}
			},
			mounted: function(){
				var ddBody = this.$refs.ddBody
				var daysLine = this.widgetBody.ae$('.days-line')
				var tRect = daysLine.getBoundingClientRect()
				var ddRect = ddBody.getBoundingClientRect()
				this.cssTop = tRect.top + tRect.height +'px'
				this.cssLeft = tRect.left + (tRect.width - ddRect.width) / 2 +'px'
			},
		})
	}
}())