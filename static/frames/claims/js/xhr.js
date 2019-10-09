function xhr(params, onOk, onErr){
	var params = params || {}
	var xhr = new XMLHttpRequest();
	var dataString = ''
	if(params.data){
		dataString = '?'+joinGetParams(params.data)
	}
	
	xhr.open(params.type || 'GET', params.url + dataString, true);
	xhr.setRequestHeader('Authorization', 'Token ' + getAuthTokenData().token)
	xhr.send(params.formData || null);
	xhr.onload = function (e) {
		var s = xhr.status
		if (s >= 200 && s <= 204) {
			onOk && onOk(xhr)
		} else if(s == 403){
			claims.showNoPermissionPlaceholder()
		} else{
			onErr && onErr(xhr)
		}
	}
}
joinGetParams = function(params){
	var arr = []
	for (var name in params) {
		var value = params[name]
		if (typeof value == "object") value = JSON.stringify(value)
		arr.push(name +'='+ encodeURIComponent(value))
	}
	return arr.join('&')
}
