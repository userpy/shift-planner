var valueToCell = function(row, params){
	function nullOr(value){
		return value || (params.noDash ? '' : '—')
	}
	function dmy(date){
		var d = new Date(date)
		return d.getDate().toLen(2) +'.'+ (d.getMonth()+1).toLen(2) +'.'+ d.getFullYear()
	}
	function hm(date){
		var d = new Date(date)
		var hours = d.getHours()
		var minutes = "0" + d.getMinutes()
		return hours + ':' + minutes.substr(-2)
	}
	function dmyhm(date){
		return dmy(date)+ ' ' +hm(date)
	}
	function deltaHm(timedelta){
		// var minutes = row.count_hours % 60;
		// var hours = (row.count_hours - minutes) / 60;
		// if (minutes < 10) minutes = '0' + minutes;
		// if (hours < 10) hours = '0' + hours;
		// return hours + ':' +minutes;
		var prefix = ''
		if (timedelta < 0){ timedelta*=-1; prefix='-' }
		return prefix+(timedelta/60/60/1000|0).toLen(2) + ':' + ((timedelta/60/1000|0)%60).toLen(2)
	}
	function deltaHmFromMinutes(timedelta){
		return deltaHm(timedelta * 60 * 1000)
	}
	try{
		switch (params.type){
			case 'tnumber':
				return nullOr( row.number )
			case 'tnumber-short':
				return nullOr( row.number )
			case 'user':
				return nullOr( row.user )
			case 'organization':
				return nullOr( row.organization.name )
			case 'organization_full':
				return nullOr( row.organization.headquater + ' / ' + row.organization.name )
			case 'organization_parent':
				return nullOr( row.organization.parent.name )
			case 'agency':
				return nullOr( row.agency.name )
			case 'headquater':
				return nullOr( row.headquater.name )
			case 'claim_type':
				return nullOr( row.claim_type.name )
			case 'status_name':
				return nullOr( row.status.name )
			case 'dt_updated':
				return row.dt_updated ? dmyhm(row.dt_updated) : nullOr()
			case 'dt_accepted':
				return row.dt_accepted ? dmyhm(row.dt_accepted) : nullOr()
			case 'start':
				return row.start ? dmy(row.start) : nullOr()
			case 'end':
				return row.end ? dmy(row.end) : nullOr()
			case 'period':
				return dmy(row.start)+ '–' +dmy(row.end)
			case 'period_hours':
				return hm(row.start)+ '–' +hm(row.end)
			case 'timedelta_minutes':
				return deltaHmFromMinutes(row.duration)
			case 'timedelta':
				return deltaHm(row.duration)
			case 'dt_created_full':
				return row.dt_created ? dmyhm(row.dt_created) : nullOr()
			case 'date_of_birth':
				return row.date_of_birth ? dmy(row.date_of_birth) : nullOr()
			case 'medical_end_date':
				return row.medical_end_date ? dmy(row.medical_end_date) : nullOr()
			case 'store_parent_name':
				return row.store.parent ? nullOr(row.store.parent.name) : nullOr()
			case 'text':
				var sliced = row['text'].slice(0,200);
				if (row['text'].length > sliced.length) {
					sliced += '...';
				}
				return sliced
			case 'dt_status_changed':
				return nullOr( dmyhm(row.dt_status_changed) )
				
			case 'attachments':
				var attachments = '';
				for (var att in row.attachments){
					attachments += '<i class="fa fa-file-alt" style="font-size: 1rem !important;"></i>&nbsp;<a href="' +
													row.attachments[att].attachment + '" title="'+ row.attachments[att].filename + 
													'">' + row.attachments[att].filename + '</a><br />'
				}
				return nullOr(attachments)

			default:
			return nullOr()
		}
	}catch(e){
		//что-то потеряли
		console.warn('Error in valueToCell: '+ e)
		return nullOr()
	}
}