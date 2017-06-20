(function ($) {

    function inherits(ctor, superCtor) {
        ctor.super_ = superCtor;
        ctor.prototype = Object.create(superCtor.prototype, {
            constructor: {
                value: ctor,
                enumerable: false,
                writable: true,
                configurable: true
            }
        });
    }

    function objCheckListItem(data){
        this.item_section_txt = function(){
            var section_id = data.item_section;
            var section_detail_url = 'http://127.0.0.1:8000/api/soamgr/soas/sections/'+section_id+'/detail/';
            var item_section_txt = "";
            $.ajax({
                url: section_detail_url,
                dataType: 'json',
                contentType: "application/json",
                async: false, 
                complete : function(){
                    console.log("Ajax request completed.")
                    console.log(this.url);
                },
                success: function(data){
                    console.log("Ajax request successful.")
                    console.log(data);
                    item_section_txt =  data.name;
                }
            });
            return item_section_txt;
        };
        
    }

    var ChecklistItem = function(element, options){
        var self = this;
        this.VERSION = '0.1.0';
        this.$el = $(element);
        this.ajax = {
            type: "POST",
            url: "{% url 'checklist_api:soa_checklist_list' 'all' %}",
            beforeSend: function (xhr, settings){
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    // Only send the token to relative URLs i.e. locally.
                    var csrftoken = self.getCookie('csrftoken');
                    // console.log(csrftoken);
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            data: {},
            // dataType: "json",
            // contentType: "application/json",
            success: {},
            error: function (xhr, ajaxOptions) {
                console.log(xhr.status);
                console.log(xhr);
                console.log(xhr.responseText);
                console.log(ajaxOptions);
            },
        };

        /** Table Objects **/
        this.table = null;

        this.tblElems = {
            $div: $('#ChecklistItem'),
            $tblDiv: $('#ChecklistItemTable'),
            $DataTable: $('#ChecklistItemDataTable'),  
            objDataTable: {                
                "bProcessing": true,
                'sAjaxSource': self.ajax.url,
                "sAjaxDataProp" : "",
                "aoColumns": [
                    {"data": "item_section"},
                    {"data": "item_subsection"},
                    {"data": "description"},
                    {"data": "check_where"},
                    {"data": "check_type"},
                    {"data": "check_sot"},
                    {"data": "check_how"},
                    {"data": "is_material"},
                    {"data": "item_score"},
                    {"data": "related_preference"},
                    {"data": "sort"},
                    {'render': function (data, type, full, meta) {                       
                        var btn_edit = '<button id="edit-'+ full.id +
                            '" class="tbl-btn-edit btn btn-xs btn-default" '+
                            'style="float: none;" type="button">'+
                            '<span class="glyphicon glyphicon-pencil"></span></button>';
                        var btn_del = '<button id="delete-'+ full.id +
                            '" class="tbl-btn-delete btn btn-xs btn-default" '+
                            'style="float: none;" type="button">'+
                            '<span class="glyphicon glyphicon-trash"></span></button>';
                        var btn =  btn_edit + btn_del;
                        return btn;
                   }}
                ]
            }
        };

        /** Modal Form objects/methods **/
        this.modalElems = {            
            $form: $('#modalChecklistItem'),
            $body: $('.modal-body'),
            $div: $('<div>'),
            $errorDiv:  $('#errorDiv'),
            $msgDiv: $('#msgDiv'),
            $id: $('#id'),
            $btnAddItem: $('.addChecklistItem'),
            $btnSubmit: $('.btnSubmit'),
            $btnCancel: $('.btnCancel')
        };

        this.modalFormModeChange = function (mode) {
            var modal = self.modalElems;
            var modes = [
                'createRecordMode-ChecklistItem',
                'updateRecordMode-ChecklistItem',
                'deleteRecordMode-ChecklistItem'
            ];

            modes.forEach(function (m, i) {
                if (m == mode) {
                    modal.$btnSubmit.addClass(mode);
                } else {
                    modal.$btnSubmit.removeClass(m);
                }

                if (mode == "deleteRecordMode-ChecklistItem") {
                    modal.$btnSubmit.addClass('btn-danger');
                    modal.$btnSubmit.html('Delete');
                } else {
                    modal.$btnSubmit.removeClass('btn-danger');
                    modal.$btnSubmit.html('Submit');
                }
            });
        };

        this.setModalData = function(data){
            $('#item_section').val(data.item_section);
            $('#item_subsection').val(data.item_subsection);
            $('#description').val(data.description);
            $('#check_where').val(data.check_where);
            $('#check_type').val(data.check_type);
            $('#check_sot').val(data.check_sot);
            $('#check_how').val(data.check_how);
            $('#is_material').val(data.is_material);
            $('#item_score').val(data.item_score);
            $('#related_preference').val(data.related_preference);
            $('#sort').val(data.sort);
        };

        /** TABLE METHODS **/
        this.constructTable = function() {
            console.log('ChecklistItem.prototype.constructTable method.');
            var tbl = self.tblElems;
            self.table = tbl.$DataTable.DataTable(tbl.objDataTable);
        };

        this.refreshTable = function(){
            //TODO: Can be improved by caching the jsonData instead of ajaxing
            //      always everytime the table is updated
            console.log('ChecklistItem.prototype.refreshTable method.');
            var tbl = self.tblElems;
            self.table = tbl.$DataTable.DataTable(tbl.objDataTable);
        };

        /** CRUD METHODS **/
        this.crud_urls = {
            list: "/api/checklist/checklist-item/all/",
            create: "/api/checklist/checklist-item/create/",
            retrieve: function (id) {
                return "/api/checklist/checklist-item/" + id + "/detail/";
            },
            update: function (id) {
                return "/api/checklist/checklist-item/" + id + "/update/";
            },
            delete: function (id) {
                return "/api/checklist/checklist-item/" + id + "/delete/";
            }
        };

        this.createRecord = function(data){
            // AJAX Add
            console.log("AJAX Create");
            var modal = self.modalElems;
            var ajax = self.ajax;
            var crud_urls = self.crud_urls;
            
            ajax.type = "POST";
            ajax.url = crud_urls.create;
            ajax.success = function (data) {   
                // append success msg    
                var msgSuccess = modal.$div.text('The checklist item is successfully added to the database...')
                                           .css('color', 'green')
                                           .attr('id', 'success');
                modal.$body.append(msgSuccess);

                // set modal element vals to empty
                setTimeout(function () {
                    modal.$body.each(function () {
                        $(this).val('');
                    });
                }, 1000);
                
                // redirect to /checklist/settings/
                window.location.replace('/checklist/settings/');
                
            };
            // ajax.data = data;
            ajax.data = data;
            console.log(ajax);
            $.ajax(ajax);
        };

        this.retrieveRecord = function(id){
            // AJAX Retrieve
            var modal = self.modalElems;
            var ajax = self.ajax;
            var crud_urls = self.crud_urls;
                        
            ajax.type = "GET";
            ajax.url = crud_urls.retrieve(id);
            ajax.success = function (data) {    
                if (data) {
                    self.setModalData(data);
                }                            
            };
            ajax.error = function (xhr, ajaxOptions) {
                console.log(xhr.status);
                console.log(ajaxOptions);
            };
            $.ajax(ajax);
        };

        this.updateRecord = function(data){
            // AJAX Update
            var modal = self.modalElems;
            var ajax = self.ajax;
            var crud_urls = self.crud_urls;
            
            ajax.type = "PUT";
            ajax.url = crud_urls.update(modal.$id.val());
            ajax.success = function () {                
                var msgSuccess = modal.$div.text('The checklist item is successfully updated to the database...')
                                           .css('color', 'green')
                                           .attr('id', 'success');
                modal.$body.append(msgSuccess);
                setTimeout(function () {
                    modal.$body.each(function () {
                        $(this).val('');
                    });
                }, 2000);

                // redirect to /checklist/settings/
                window.location.replace('/checklist/settings/');
            };
            ajax.data = data;
            $.ajax(ajax);
        };

        this.deleteRecord = function(id){
            // AJAX Delete            
            var modal = self.modalElems;
            var ajax = self.ajax;
            var crud_urls = self.crud_urls;

            ajax.type = "DELETE";            
            ajax.url = crud_urls.delete(id);
            ajax.success = function () {     
                
                var msgSuccess = modal.$div.text('The checklist item is successfully deleted to the database...')
                                           .css('color', 'green')
                                           .attr('id', 'success');
                modal.$body.append(msgSuccess);
                setTimeout(function () {
                    modal.$body.each(function () {
                        $(this).val('');
                    });
                }, 2000);

                // redirect to /checklist/settings/
                window.location.replace('/checklist/settings/');
                
            };     
            $.ajax(ajax);      
        };

        /** Utility Functions **/
        this.getIndexByID = function (id, data) {
            var i=0;
            for (let r of data){
                if (r.id == id){
                    break;
                }
                i++;
            }
            return i;
        };

        this.getNameByID = function (key, data) {
            var name = '';
            for (let r of data) {
                if (r.id == key) {
                    name = r.name;
                    break;
                }
            }
            return name;
        };

        // used for csrf token in every ajax request
        this.getCookie = function(name){
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }


        /** Constructor Method **/
        this.init = function() {

            if ($.isArray(self.data)) {
                self.master = [];
                $.extend(self.master, self.data);
            }

            self.constructTable();

            self.refreshTableHandler();

        };

        this.init();
        

    };

    ChecklistItem.prototype = {
        plugins: null,
        query: null,
        table: null,
        jsonData: [],
        url: "{% url 'checklist_api:soa_checklist_list' 'all' %}",
        refreshTableHandler: function() {
            var self = this;
            var modal = self.modalElems;
            var crud_urls = self.crud_urls;
            var tbl = self.tblElems;

            // Create Record Button Click
            modal.$btnAddItem.click(function (e) {           
                modal.$form.attr('method', 'POST');     
                modal.$form.attr('action', crud_urls.create);
                console.log("Showing the modal form on create mode.");
                self.modalFormModeChange('createRecordMode-ChecklistItem');
            });
            
            // Edit Record Button Click            
            tbl.$DataTable.on('click', '.tbl-btn-edit', function (e) {
                e.preventDefault();
                // get ID
                var target = $(this).attr("id");
                target=target.split("-");
                var updateRecordID = target[1];
                modal.$id.val(updateRecordID);
                self.retrieveRecord(updateRecordID);

                modal.$form.attr('method', 'POST');     
                modal.$form.attr('action', crud_urls.update(updateRecordID));

                console.log("Showing the modal form on update mode.");
                self.modalFormModeChange('updateRecordMode-ChecklistItem');
                modal.$form.modal('show'); 
            });

            // Delete Record Button Click
            tbl.$DataTable.on('click', '.tbl-btn-delete', function (e) {
                e.preventDefault();
                // get ID
                var target = $(this).attr("id");
                target=target.split("-");
                var deleteRecordID = target[1];
                modal.$id.val(deleteRecordID);
                self.retrieveRecord(deleteRecordID);

                modal.$form.attr('method', 'POST');     
                modal.$form.attr('action', crud_urls.delete(deleteRecordID));
                
                console.log("Showing the modal form on delete mode.");
                self.modalFormModeChange('deleteRecordMode-ChecklistItem');
                modal.$form.modal('show'); 
                
            });

            // Submit Button Event Handler
            modal.$btnSubmit.click(function (e) {
                e.preventDefault();
                console.log("Submit button event triggered.");
                if ($('#is_material').is(":checked")) {
                    $('#is_material').val("True");
                }
                var id = modal.$id.val();
                var data = modal.$form.serialize();

                if (modal.$btnSubmit.hasClass('createRecordMode-ChecklistItem')) {
                    console.log("Modal form is currently on createRecordMode-ChecklistItem mode.");
                    self.createRecord(data);
                    console.log("createRecord(data) method has been called.");
                    window.location.replace("/checklist/settings/");
                } else if (modal.$btnSubmit.hasClass('updateRecordMode-ChecklistItem')) {
                    console.log("Modal form is currently on updateRecordMode-ChecklistItem mode.");
                    self.updateRecord(data);
                    console.log("updateRecord(data) method has been called.");
                } else if (modal.$btnSubmit.hasClass('deleteRecordMode-ChecklistItem')) {
                    console.log("Modal form is currently on deleteRecordMode-ChecklistItem mode.");
                    self.deleteRecord(id);
                    console.log("deleteRecord(data) method has been called.");
                }
            });            

        },
        destroy: function() {
            console.log('prototype.destroy:');
            this.$el.empty();
            return true;
        },
        getObject: function() {
            console.log('prototype.getObject:');
            return this;
        },
        getVersion: function() {
            return this.VERSION;
        },
        getJsonData: function() {
            var jsonData = {};
            var tableData = [];
            this.master.forEach(function(data, i) {
                tableData.push(data.data);
            });
            jsonData.data = tableData;
            return jsonData;
        },
        addTableRow:function(data) {
            console.log('prototype.addTableRow:');
            this.createRecord(data);
        },
        setMaster: function (d) {
            if ($.isArray(d)) {
                this.master = d;
                return true;
            }
            return false;
        },
        saveData: function() {
            console.log('prototype.saveData:');
            return 0;
        }
    };

    var checklistItem = new ChecklistItem('#ChecklistItemDataTable');
    
})( jQuery, window, document);
// end LumpSumExpensesBox




