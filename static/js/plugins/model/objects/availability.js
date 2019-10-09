function Availability(data, p){
	var p = p || {}
	var availability = this
	var oks = Object.keys(data)
	oks.forEach(function(ok){
		availability[ok] = data[ok]
	})
	if(p.reverseIds){
		var oid = availability.organization_id
		availability.organization_id = availability.agency_id
		availability.agency_id = oid
	}
	availability.kind = data.kind || 0
	if(!data.id || p.isNewId) availability.id = -rd(1000, 9999)
}
Object.defineProperties(Availability.prototype, {
	'start_dtime': { get: function(){ return new Date(this.start).getTime()  } },
	'start_date': { get: function(){ return new Date(this.start_dtime).startOfDay().getTime() } },
	'start_time': { get: function(){ return new Date(this.start_dtime).getTime() - new Date(this.start_dtime).startOfDay().getTime() } },

	'end_dtime': { get: function(){ return new Date(this.end).getTime() } },
	'end_date': { get: function(){ return new Date(this.end_dtime).startOfDay().getTime() } },
	'end_time': { get: function(){ return new Date(this.end_dtime).getTime() - new Date(this.end_dtime).startOfDay().getTime() } },

	'duration': { get: function(){ return this.end_dtime - this.start_dtime } },
})
Availability.prototype.setStart = function(newDtime, silent){
	this.start = new Date( Model.tz.subOffsetFromServer(newDtime) ).toISODateString()
	if(!silent) throwEvent('availablity:modified', {shift: this})
}
Availability.prototype.setEnd = function(newDtime, silent){
	this.end = new Date( Model.tz.subOffsetFromServer(newDtime) ).toISODateString()
	if(!silent) throwEvent('availablity:modified', {shift: this})
}
Availability.prototype.stretchEnd = function(delta){
	this.setEnd(this.start_dtime + delta, true)
	throwEvent('availablity:modified')
}
Availability.prototype.getDayZone = function(){
	if(this.start_time < shift_assign.lightDayStart) return 0
	if(this.start_time < shift_assign.nightStart) return 1
	return 2
}