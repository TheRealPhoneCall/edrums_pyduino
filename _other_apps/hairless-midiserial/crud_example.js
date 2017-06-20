 /************** Addopted from: http://codereview.stackexchange.com/questions/35316/javascript-module-pattern-with-ajax */
 
 $(document).ready(function () {
    //open the modal
    //the update, delete and insert functions come from boxes present in a modal not shown
    $('#openModal').click(function () {
        $('#contact').modal();
    });
    //insert
    $('#btnSavePerson').click(function () {
        //is it a good idea to have the data objects inside all of these functions?    
        var data = {
            personId: $('#tbPersonId').val(),
            firstName: $('#tbFirstName').val(),
            lastName: $('#tbLastName').val()
        };
        person.insert(data);
    });

    //delete
    $('#btnDeletePerson').click(function () {
        var personId = $('#tbDelete').val();
        person.remove(personId);
    });

    //update
    $('#btnUpdatePerson').click(function () {
        var data = {
            personId: $('#tbPersonId').val(),
            firstName: $('#tbFirstName').val(),
            lastName: $('#tbLastName').val()
        };
        console.log(JSON.stringify(data));
        person.update(data);
    });
    //get
    $('#getPeople').click(function () {
        person.get();
    });
    //*********************person module

    var person = (function () {
        //the ajax object will be passed and shared between
        //the functions here (type and dataType dont change in this example)
        var ajax = {
            type: "POST",
            url: "",
            data: {},
            dataType: "json",
            contentType: "application/json",
            success: {},
            error: {}
        }

        //************ insert
        function insert(data) {
            ajax.url = '../Service.asmx/InsertPerson';
            ajax.success = function () {
                console.log('success before setTimeout');
                var successMessage = $('<div>').text('Successfully added to the database...')
                                                .css('color', 'green')
                                                .attr('id', 'success');
                $('.modal-body').append(successMessage);
                window.setTimeout(function () {
                    $('.modal-body').each(function () {
                        $(this).val('');
                    });
                    $('#contact').modal('hide');
                }, 1000);
            }
            ajax.data = JSON.stringify(data);
            ajax.error = function (xhr, ajaxOptions) {
                console.log(xhr.status);
                console.log(ajaxOptions);
            };
            $.ajax(ajax);
        }
        //************* delete
        function remove(data) {
            ajax.url = '../Service.asmx/DeletePerson';
            console.log('working string: ');
            var obj = { personId: data };
            console.log(JSON.stringify(obj));
            ajax.data = JSON.stringify(obj);
            console.log(ajax.data);
            ajax.success = function () {
                console.log('person successfully deleted');
                var successMessage = $('<div>').text('Person successfully deleted from the database')
                                                .css('color', 'red');
                $('.modal-body').append(successMessage);
                window.setTimeout(function () {
                    $('.modal-body input').each(function () {
                        $(this).val('');
                    });
                    $('#contact').modal('hide');
                }, 1000);
            };
            ajax.error = function (xhr, ajaxOptions) {
                console.log(xhr.status);
                console.log(ajaxOptions);
            }
            $.ajax(ajax);
        }
        //*************** update
        function update(data) {
            ajax.url = '../Service.asmx/UpdatePerson',
            ajax.data = JSON.stringify(data),
            ajax.success = function () {
                console.log('update was successful');
                var successMessage = $('<div>').text('Record successfully updated...')
                                                .css('color', 'green');
                $('modal-body').append(successMessage);
                window.setTimeout(function () {
                    $('.modal-body input').each(function () {
                        $(this).val('');
                    });
                    $('#contact').modal('hide');
                }, 1000);
            };
            ajax.error = function (xhr, ajaOptions) {
                console.log(xhr.status);
            };
            $.ajax(ajax);
        };
        //************** get
        function get() {
            //****** appropriate to have this function here?
            function style(json) {
                json = $.parseJSON(json);
                var $personArray = [];
                for (var obj in json) {
                    var $person = $('<div>').addClass('person');
                    for (var prop in json[obj]) {
                        var label = $('<span>').text(prop).addClass('badge pull-left').appendTo($person);
                        var propertyData = $('<span>').text(json[obj][prop]).addClass('pull-right').appendTo($person);
                    }
                    $personArray.push($person);
                }
                return $personArray;
            }
            ajax.url = '../Service.asmx/GetPersons';
            ajax.success = function (data) {
                data = data.d;
                console.log('ajax successful');
                $('body').append(style(data));
            };
            ajax.error = function (xhr, ajaxOptions) {
                console.log(xhr.status);
                console.log(ajaxOptions);
            }
            $.ajax(ajax);
        }
        //*********** public methods
        return {
            insert: insert,
            remove: remove,
            update: update,
            get: get
        };

    })();

});