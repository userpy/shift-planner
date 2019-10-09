/*
* Copyright © 2016 ООО «Верме»
* 
* Занимается таймзонами и их разницей между клиентом и сервером.
*/

Model.tz = new function(){
	this.currentServerUTCOffset = 0
	this.currentClientUTCOffset = new Date().getTimezoneOffset() * Date.minute

	// Добавляет/отнимает разницу в таймзонах между клиентом и сервером.
	this.addOffsetFromServer = function(dtime) {
		return dtime + (this.currentServerUTCOffset - this.currentClientUTCOffset)
	}
	this.subOffsetFromServer = function(dtime) {
		return dtime - (this.currentServerUTCOffset - this.currentClientUTCOffset)
	}
}