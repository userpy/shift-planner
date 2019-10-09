function Shift(data, p){
	var p = p || {}
	var shift = this
	var oks = Object.keys(data)
	oks.forEach(function(ok){
		shift[ok] = data[ok]
	})
	if(p.reverseIds){
		var oid = shift.organization_id
		shift.organization_id = shift.agency_id
		shift.agency_id = oid
	}
	if(!data.id || p.isNewId) shift.id = -rd(1000, 9999)
}
Object.defineProperties(Shift.prototype, {
	'start_dtime': { get: function(){ return Model.tz.subOffsetFromServer(new Date(this.start).getTime() ) } },
	'start_date': { get: function(){ return new Date(this.start_dtime).startOfDay().getTime() } },
	'start_time': { get: function(){ return new Date(this.start_dtime).getTime() - new Date(this.start_dtime).startOfDay().getTime() } },

	'end_dtime': { get: function(){ return Model.tz.subOffsetFromServer(new Date(this.end).getTime() ) } },
	'end_date': { get: function(){ return new Date(this.end_dtime).startOfDay().getTime() } },
	'end_time': { get: function(){ return new Date(this.end_dtime).getTime() - new Date(this.end_dtime).startOfDay().getTime() } },

	'duration': { get: function(){ return this.end_dtime - this.start_dtime } },
})
Shift.prototype.move = function(delta){
	this.setStart(this.start_dtime + delta, true)
	this.setEnd(this.end_dtime + delta, true)
	throwEvent('shift:modified')
}
Shift.prototype.setStart = function(newDtime, silent){
	this.start = new Date( Model.tz.addOffsetFromServer(newDtime) ).toISOString()
	if(!silent) throwEvent('shift:modified', {shift: this})
}
Shift.prototype.setEnd = function(newDtime, silent){
	this.end = new Date( Model.tz.addOffsetFromServer(newDtime) ).toISOString()
	if(!silent) throwEvent('shift:modified', {shift: this})
}
Shift.prototype.stretchEnd = function(delta){
	this.setEnd(this.start_dtime + delta, true)
	throwEvent('shift:modified')
}
Shift.prototype.getDayZone = function(){
	if(this.start_time < shift_assign.lightDayStart) return 0
	if(this.start_time < shift_assign.nightStart) return 1
	return 2
}