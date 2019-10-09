function loadDocData(data){
	OutRequests['get-employee-doc']({
		data: data,
		success: function(r){
			updateDocUploaderWithReqParams(r)
		},
		error: function(r){alert(r)},
	})
}
function uploadDocs(){
	duVM.doUpload()
}
function updateDocUploaderWithReqParams(r){
	var reqParams = r.reqParams
	reqParams.guid = r.doc.guid
	duVM.reqParams = reqParams
}
function resetDocUploader(){
	duVM.callReset()
	duVM.docsUrl = verme_docs_url 
	duVM.afterUpload = function(){
		unblockModalForm()
		$('#modal_doc').modal('hide');
	}
	duVM.toggleLoadingState = function(flag){
		if(flag) blockModalForm()
			else unblockModalForm()
	}
}