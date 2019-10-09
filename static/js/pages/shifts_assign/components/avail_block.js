page_main_widget.components.push(new function(){
	this.init = function(){
		Vue.component('sa-avail-block', {
			name: 'sa-avail-block',
			props: ['avail', 'comp_start_dtime', 'comp_end_dtime'],
			template: '\
				<div class="avail"\
					:style="{\
						left: leftCss,\
						width: widthCss,\
					}"\
				></div>\
			',
			computed: {
				start_dtime: function(){
					return new Date(this.avail.start_dtime).startOfDay().getTime()
				},
				leftCss: function(){
					return (this.start_dtime - this.comp_start_dtime) / (this.comp_end_dtime - this.comp_start_dtime) * 100 +'%'
				},
				widthCss: function(){
					//return this.avail.duration / (this.comp_end_dtime - this.comp_start_dtime) * 100+'%'
					var compDaysDiff = this.daysDiff(this.comp_end_dtime,this.comp_start_dtime)
					var availDaysDiff = this.daysDiff(this.avail.end,this.avail.start)+1
					return  availDaysDiff/compDaysDiff  * 100+'%'
				},
			},
			methods: {
				daysDiff: function(end, start){
					return ((new Date(end)).startOfDay().getTime() - (new Date(start)).startOfDay().getTime())/(1000*60*60*24)
				}
			}
		})
	}
}())