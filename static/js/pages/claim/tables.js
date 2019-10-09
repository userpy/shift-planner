



// <!-- Инициализация таблиц -->
function init_messages_datatable(){
	var messages_datatable = $('#datatable_claim_messages').mDatatable({
		stateSave: true,
		stateSaveCallback: function(settings,data) {
			localStorage.setItem( 'local_dataTables_' + settings.sInstance, JSON.stringify(data) )
		},
		stateLoadCallback: function(settings) {
			return JSON.parse( localStorage.getItem( 'local_dataTables_' + settings.sInstance ) )
		},
		translate:{
			records:{
				processing:"Поиск..",
				noRecords:"Сообщений не найдено"
			},
			toolbar:{
				pagination:{
					items:{
						default:{
							first:"Первая",
							prev:"Предыдущая",
							next:"Следующая",
							last:"Последняя",
							more:"Больше",
							input:"Ввести",
							select:"Выбрать"
						},
						info:"Показаны сообщения с {" + "{start}} по {" + "{end}} из {" + "{total}}"
					}
				}
			}
		},
		data: {
			type: "remote",
			source: {
				read: {
					method: 'GET',
					url: "/api-get-claim-messages/",
					params: {
						orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null},
						claim_id: claim_id,
						'_': function(){return new Date().getTime()}
					}
				}
			},
			pageSize: 10,
			serverPaging: true,
			serverFiltering: true,
			serverSorting: true
		},
		layout: {
			theme: "default",
			scroll: false,
			//height: 300,
			footer: !1,
			spinner: {
				type: 1,
				theme: "default"
			}
		},
		sortable: !0,
		columns: [{
			field: "party",
			title: "Сторона",
			sortable: true,
			filterable: false,
			width: 150,
			template: function (row) {
				if (row['party_detail']){
					return row['party_detail'] + '<br />' + row['user_name'];

				}else{
						var party = {
							'agency': {'title': 'Агентство'},
							'client': {'title': 'Клиент'}
						};
					return party[row['party']]['title'] + '<br />' + row['user_name'];
				}
			}
		}, {
			field: "dt_created",
			title: "Сообщение",
			sortable: true,
			filterable: false,
			width: 500,
			template: function (row) {
				return valueToCell(row, {type: 'dt_created_full'}) + '<br />' + row['text'];
			}
		}, {
			field: "attachments",
			title: "Файлы",
			sortable: false,
			filterable: false,
			width: 180,
			template: function (row) {
				if (row['attachments']){
					var attachments = '';
					for (var att in row['attachments']){
						attachments += '<i class="fa fa-file-alt" style="font-size: 1rem !important;"></i>&nbsp;<a href="' + row['attachments'][att]['attachment'] + '" title="'+ row['attachments'][att]['filename'] + '">' + row['attachments'][att]['filename'] + '</a><br />';
					}
					return attachments;
				} else{
					return ''
				}
			}
		}]
	})
}

function init_files_datatable(){
	var files_datatable = $('#datatable_claim_files').mDatatable({
		stateSave: true,
		stateSaveCallback: function(settings,data) {
			localStorage.setItem( 'local_dataTables_' + settings.sInstance, JSON.stringify(data) )
		},
		stateLoadCallback: function(settings) {
			return JSON.parse( localStorage.getItem( 'local_dataTables_' + settings.sInstance ) )
		},
		translate:{
			records:{
				processing:"Поиск..",
				noRecords:"Файлов не найдено"
			},
			toolbar:{
				pagination:{
					items:{
						default:{
							first:"Первая",
							prev:"Предыдущая",
							next:"Следующая",
							last:"Последняя",
							more:"Больше",
							input:"Ввести",
							select:"Выбрать"
						},
						info:"Показаны сообщения с {" + "{start}} по {" + "{end}} из {" + "{total}}"
					}
				}
			}
		},
		data: {
			type: "remote",
			source: {
				read: {
					method: 'GET',
					url: "/api-get-claim-files/",
					params: {
						orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null},
						claim_id: claim_id,
						'_': function(){return new Date().getTime()}
					}
				}
			},
			pageSize: 10,
			serverPaging: true,
			serverFiltering: true,
			serverSorting: true
		},
		layout: {
			theme: "default",
			scroll: false,
			//height: 300,
			footer: !1,
			spinner: {
				type: 1,
				theme: "default"
			}
		},
		sortable: !0,
		columns: [{
			field: "message_party",
			title: "Сторона",
			sortable: false,
			filterable: false,
			width: 90,
			template: function (row) {
				var party = {
					'agency': {'title': 'Агентство'},
					'client': {'title': 'Клиент'}
				};
				if (row['message']){
					return party[row['message']['party']].title;
				}else{
					return party['client'].title;
				}
			}
		}, {
			field: "message_user_name",
			title: "ФИО",
			sortable: false,
			filterable: false,
			width: 200,
			template: function (row) {
				if (row['message']){
					return row['message']['user_name'];
				}else{
					return row['claim']['user_name'];
				}
			}
		},  {
			field: "file",
			title: "Файл",
			sortable: false,
			filterable: false,
			width: 250,
			template: function (row) {
				return '<i class="fa fa-file-alt" style="font-size: 1rem !important;"></i>&nbsp;<a href="' + row['attachment'] + '" title="'+ row['filename'] + '">' + row['filename'] + '</a><br />';
			}
		}, {
			field: "dt_created",
			title: "Добавлен",
			sortable: true,
			filterable: false,
			width: 150,
			template: function(row){
				return valueToCell(row, {type: 'dt_created_full'})
			}
		}]
	})
}
// <!-- / Инициализация таблиц -->
