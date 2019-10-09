// Блок загрузки файлов
Dropzone.autoDiscover = false;
$(document).ready(function(){
	// Массив для хранения файлов
	fileform = [];
	Dropzone.autoDiscover = false;
	$("#file-form").dropzone({
		paramName: 'file',
		clickable: true,
		maxFilesize: max_filesize,
		maxFiles: 5,
		addRemoveLinks: true,
		uploadMultiple: false,
		autoProcessQueue: false,
		dictRemoveFile: 'Удалить',
		dictFileTooBig: 'Максимальный размер загружаемых файлов составляет '+ max_filesize +' Мб',
		init: function() {
			this.on("removedfile", function(file) {
				// При удалении файла из dropzone удаляем его также из массива
				// файлов для отправки по имени
				fileform = fileform.filter(function(item){
					if (item.filename == file.name) return false
					return true
				})
			});
		},
		accept: function(file, done){
			var reader = new FileReader();
			reader.onload = handleReaderLoad;
			reader.readAsDataURL(file);
			// Добавляем base64 файлы в массив для отправки
			function handleReaderLoad(evt) {
				fileform.push({data: evt.target.result, filename: file.name})
			}
			done();
		}
	});
});
// Блок загрузки файлов