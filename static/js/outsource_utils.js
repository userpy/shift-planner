/*
Copyright 2018 ООО «Верме»
Файл для русской локализации компонента datepicker.
JS-утилиты для портала аутсорсинга
Использован babel для преобразования в формат, принимаемый IE 11
Author: Artem Bulatov
*/
'use strict';

var _createClass = function() {
	function defineProperties(target, props) {
		for(var i = 0; i < props.length; i++) {
			var descriptor = props[i];
			descriptor.enumerable = descriptor.enumerable || false;
			descriptor.configurable = true;
			if("value" in descriptor) descriptor.writable = true;
			Object.defineProperty(target, descriptor.key, descriptor);
		}
	}
	return function(Constructor, protoProps, staticProps) {
		if(protoProps) defineProperties(Constructor.prototype, protoProps);
		if(staticProps) defineProperties(Constructor, staticProps);
		return Constructor;
	};
}();

function _classCallCheck(instance, Constructor) {
	if(!(instance instanceof Constructor)) {
		throw new TypeError("Cannot call a class as a function");
	}
}


/*
	Класс для работы с модальными окнами.
	Основные методы:
			constructor()
			addButton(options) - добавить кнопку
			addButtons(options) - добавить кнопки
			addRow(options) - добавить строку с контентом
			addRows(options) - добавить строки с контентом
			create(options) - создать объект JQuery. Все options возможно указать только в этом методе
*/
var OutsourceModal = function() {
	function OutsourceModal() {
		_classCallCheck(this, OutsourceModal);

		this.__content = [];
		this.__buttons = [];
		this.__modal = null;
	}

	_createClass(OutsourceModal, [{
		key: 'addButton',
		value: function addButton(options) {
			var id = options['id'];
			var type = options['type'];
			var content = options['content'];

			// Набор классов для кнопки
			var __classes_set = 'btn m-btn m-btn--air m-btn--custom ' + 'btn-' + type;
			var button = ['<button type="button" id="' + id + '" class="' + __classes_set + '">' + content + '</button>'].join('\n');

			this.__buttons.push(button);
			return $(button);
		}
	}, {
		key: 'addButtons',
		value: function addButtons(buttons) {
			for(var idx = 0; idx < buttons.length; idx++) {
				this.addButton(buttons[idx]);
			}
		}

		// Функция добавляет строку в модальное окно. СТрока формата label -- action,
		//      где label -- отоображение, action - плейсмент для действия, которое нужно сделать пользователю (ввести дату, текст и т.д.... )
		// input: options - options to be set in structured ( JSON ) format
		//      id - id элемента action и значение атрибута for для label
		//      [deprecated] class - класс для вставки в row
		//      label - название строки || label, который будет отображаться в левой части
		//      name - атрибут name для action-элемента

	}, {
		key: 'addRow',
		value: function addRow(options) {
			var id = options['id'];
			var name = '';
			var required = ''
			var label = options['label'];
			var type = options['type'];
			var extra_classes = '';
			// var helper
			var title = ''; // Параметр - placeholder для selectpicker
			if(typeof options['extra_classes'] !== 'undefined') extra_classes = options['extra_classes'];
			if(typeof options['name'] !== 'undefined') name = options['name'];
			if(typeof options['required'] !== 'undefined') required = 'data-required';
			else name = options['id'];
			// if(typeof options['helper'] !== 'undefined') helper = options['helper'];
			// else helper = false;
			if(typeof options['title'] !== 'undefined') title = options['title'];
			else title = '';


			var action_body = '';
			// Условия по типу добавляемого объекта.
			if(type == 'datepicker') {
				action_body = '<input '+ required +' type="text" class="form-control outsource_js_datepicker ' + extra_classes + '" name="' + name + '" id="' + id + '"></input>';
			} else if(type == 'textarea') {
				action_body = '<textarea '+ required +' class="form-control m-input ' + extra_classes + '" id="' + id + '" name="' + name + '" rows="3"></textarea>';
			} else if(type == 'input') {
				action_body = '<input '+ required +' name="' + name + '" id="' + id + '" class="form-control m-input ' + extra_classes + '" type="text" ></input>';
			} else if(type == 'select') {
				action_body = '<select '+ required +' name="' + name + '" class="form-control ' + extra_classes + '" type="text" ' + 'id="' + id + '" title="' + title + '"></select>';
			} else if(type == 'checkbox') {
				action_body = '<label name="' + name + '" class="m-checkbox ' + extra_classes + '">' + '<input id="' + id + '" type="checkbox">' + label + '<span></span></label>';
			}
			// Строка (row)
			if(type !== 'checkbox')
				var row = ['<div class="form-group m-form__group row">',
					'<label for="' + id + '" class="col-3 col-form-label" style="text-align: right;">' + label + '</label>',
					'<div class="col-9">',
					action_body,
					'<span id="' + name + '-help" class="m-form__help text-danger" style="display: none;"></span>',
					'</div>',
					'</div>'
				];
			else
				var row = ['<div class="form-group m-form__group row">',
					'<label for="' + id + '" class="col-3 col-form-label" style="text-align: right;"></label>',
					'<div class="col-9">',
					action_body,
					'<span id="' + name + '-help" class="m-form__help text-danger" style="display: none;"></span>',
					'</div>',
					'</div>'
				];
			/*if (helper === true)
			    row = row.concat([
			        '<span for="' + name + '" class="m-form__help text-danger" style="display: none;"></span>'
			    ]);
			*/
			row = row.join('\n');

			this.__content.push(row);
			return $(row);
		}
	}, {
		key: 'addRows',
		value: function addRows(rows) {
			for(var idx = 0; idx < rows.length; idx++) {
				this.addRow(rows[idx]);
			}
		}
	}, {
		key: 'create',
		value: function create(options) {
			this.__content = []
			this.__buttons = []
			if(typeof options['options'] !== 'undefined') {
				this.id = options['options']['id'];
				this.title = options['options']['title'];
			}
			if(typeof options['rows'] !== 'undefined') this.addRows(options['rows']);
			if(typeof options['buttons'] !== 'undefined') this.addButtons(options['buttons']);
			this.closeBtnName = ('closeBtnName' in options['options']) ? options['options']['closeBtnName'] : "Отмена";
			this.footer = ('noFooter' in options['options']) ? '' : '<div class="modal-footer">'+this.__buttons.join('\n')+'<button type="button" class="btn btn-secondary" data-dismiss="modal">' + this.closeBtnName + '</button></div>';
			
			var modal = [
				'<div class="modal fade" id="' + this.id + '" role="dialog" aria-labelledby="exampleModalLabel" style="display: none;" aria-hidden="true">',
				'<div class="modal-dialog modal-lg modal-dialog-centered" role="document">',
				'<div class="modal-content">',
				// Header
				'<div class="modal-header">',
				'<h5 class="modal-title">' + this.title + '</h5>',
				'<button type="button" class="close" data-dismiss="modal" aria-label="Close">',
				'<span aria-hidden="true">×</span>',
				'</button>',
				'</div>',
				// Body
				'<div class="modal-body">',
				this.__content.join('\n'),
				'</div>',
				// Footer
				this.footer,
				'</div>',
				'</div>',
				'</div>'
			].join('\n');

			this.__modal = modal;
			return $(modal);
		}
	}]);

	return OutsourceModal;
}();

var OutsourceAPI = function() {
	function OutsourceAPI() {
		_classCallCheck(this, OutsourceAPI);
	}

	_createClass(OutsourceAPI, null, [{
		key: 'getHeadquatersList',

		// Получение списка организаций
		value: function getHeadquatersList(agency_id, success_handler, error_handler) {
			var ajax_data = {};
			if(agency_id !== null) ajax_data = {agency_id: agency_id}

			OutRequests['get-headquaters-organizations']({
				data: ajax_data,
				success: function success(data) {
					if(typeof success_handler !== 'undefined') success_handler(data);
					return data;
				},
				error: function error(data) {
					if(typeof error_handler !== 'undefined') error_handler(data);
					return data;
				}
			});
		}

		// Список организацй по ID клиента
	}, {
		key: 'getOrganizationsByHeadquater',
		value: function getOrganizationsByHeadquater(headquater_id, agency_id, success_handler, error_handler) {
			OutRequests['get-headquaters-organizations']({
				data: {
					agency_id: agency_id,
					headquater_id: headquater_id
				},
				success: function success(data) {
					if(typeof success_handler !== 'undefined') success_handler(data);
					return data;
				},
				error: function error(data) {
					if(typeof error_handler !== 'undefined') error_handler(data);
					return data;
				}
			})
		}
	}]);

	return OutsourceAPI;
}();

;

/*
    Получить значение, если оно определено
        variable - переменная
        default_value - значение, если variable - 'undefined'
    Елси variable == null, то значение считается определенным
*/

function get(variable, default_value) {
	if(typeof variable === 'undefined') return default_value;
	return variable;
}