var ChecklistForm = {
    checklist_data: [],
    review_metadata: [],
    operation_type: [],
    create: function(values){
        var instance = Object.create(this);
        Object.keys(values).forEach(function(key){
            instance[key] = values[key];
        });
        this.init();
        return instance;
    },
    init: function(){
        this.cache_doms();
        this.make_checklist_form();
        this.bind_events();
    },
    cache_doms: function(){
        this.doms = {
            $checklist_body: $('#checklist_body')
        };
    },
    bind_events: function(){
        $('.checklist').change(function(){
            //idCorrect = "chk-correct-" + item_section + "-" + item_subsection + "-" + id;
            //idResolved = "chk-resolved-" + item_section + "-" + item_subsection + "-" + id;
            var target = $(this).attr("id");
            target = target.split("-");
            console.log(target);
            item_section = target[2];
            item_subsection = target[3];
            id = target[4]; 

            if ($(this).is(':checked')) {
                idResolved = "#chk-resolved-" + item_section + "-" + item_subsection + "-" + id;
                $(idResolved).prop('checked', true);
                console.log($(idResolved));
            }
        });

        /* Table Collapse Functions */

        $(document).on("click", ".collapsedpanel" ,function (e) {
            var target = $(this).attr("id");
            target = target.split("-");
            var control = "collapse" + target[1];
            $('#' + control).toggleClass('fa-minus fa-plus');
            $('#' + target[1] ).toggleClass('hidden visible');
        });

        

        $(document).on("click", ".collapse-basic-box" ,function (e) {
            $('#collapseBasicBox').toggleClass('fa-minus fa-plus');
            $('#BasicBox').toggleClass('hidden visible');
        });

        $(document).on("click", ".chevron_toggleable", function(e) {
            $(this).toggleClass('glyphicon-chevron-down glyphicon-chevron-up');
            var target = $(this).attr('id');
            target = target.split("-");
            $('#pref-' + target[1]).slideToggle("slow");
            e.preventDefault();
        });
        
        function showRelatedPreference(preference_row_id){
            $(preference_row_id).removeClass('hidden');
            $(preference_row_id).addClass('show');
        }
        
        function hideRelatedPreference(preference_row_id){
            $(preference_row_id).removeClass('show');
            $(preference_row_id).addClass('hidden');
        }
    },
    make_checklist_form: function(){
        console.log("Creating checklist form");
        var $checklist_body = this.doms.$checklist_body;
        console.log("$checklist_body", $checklist_body);
        var review_metadata = this.review_metadata;
        var current_section = 0;
        var current_subsection = 0;
        
        console.log('review_metadata', review_metadata);

        for (var key in review_metadata) {
            id = review_metadata[key]['id'];
            item_section = review_metadata[key]['item_section'];
            item_section_txt = review_metadata[key]['item_section_txt'];
            item_subsection = review_metadata[key]['item_subsection'];
            item_subsection_txt = review_metadata[key]['item_subsection_txt'];
            description = review_metadata[key]['description'];
            check_where = review_metadata[key]['check_where'];
            check_type = review_metadata[key]['check_type'];
            check_sot = review_metadata[key]['check_sot'];
            check_how = review_metadata[key]['check_how'];
            is_material = review_metadata[key]['is_material'];
            related_preference = review_metadata[key]['related_preference'];
            related_preference_txt = review_metadata[key]['related_preference_txt'];
            sort = review_metadata[key]['sort'];
            
            console.log(id, item_section, item_subsection, description);

            current_checklist_data = this.get_current_item_checklist_data(id);
            correct = current_checklist_data.correct;
            note = current_checklist_data.note;
            resolved = current_checklist_data.resolved;
            

            console.log(correct, note, resolved);
            
            valCorrect =  correct ? "checked" : "";
            valNote =  note;  
            valResolved =  resolved ? "checked" : "";    

            valRelatedPrefField = "Related Preference Here.";
            valRelatedPrefChoice = "Related preference option here.";
            
            idCorrect = "chk-correct-" + item_section + "-" + item_subsection + "-" + id;
            idNote = "area-note-" + item_section + "-" + item_subsection + "-" + id;
            idResolved = "chk-resolved-" + item_section + "-" + item_subsection + "-" + id;
                                   
            lblDescription = description;
            strDisabled = "{% if not update_mode or user == 'Qpp Admin' or form_type == 'view' %}disabled{% endif %}";
            chkCorrect = "<input id='"+ idCorrect + "' class='checklist' type='checkbox' " + valCorrect + " data-group-cls='btn-group-sm' " + strDisabled + ">";
            areaNote = "<textarea id='"+ idNote + "' class='notes-field' placeholder='Enter notes' " + strDisabled + ">" + valNote + "</textarea>";
            chkResolved = "<input id='" + idResolved + "' class='resolved' type='checkbox' " + valResolved + " data-group-cls='btn-group-sm'" + strDisabled + ">";
            
            btnRelatedPref = "<span id='show-"+ id +"' class='chevron_toggleable glyphicon glyphicon-chevron-down hidden' href='#'></span>";
            divRelatedPref = "<tr><td colspan='5'><div id='pref-" + id + "' style='display: none;'><strong>" + valRelatedPrefField + "</strong><p>" + valRelatedPrefChoice + "</p></div></td></tr>";
            
            if (this.operation_type == "non-tech") {
                is_current_check_type = (check_type == "1") ? true : false;
                console.log("is_current_check_type: ", is_current_check_type);
            } else if (this.operation_type == "tech") {
                is_current_check_type = (check_type == "2") ? true : false;
                console.log("is_current_check_type: ", is_current_check_type);
            } else if (this.operation_type == "admin") {
                is_current_check_type = true;
                console.log("is_current_check_type: ", is_current_check_type);
            }
            if (is_current_check_type){
                rowData = "<tr><td></td><td>" + lblDescription + "</td><td>"+ chkCorrect +"</td><td>"+ areaNote + "</td><td>" + chkResolved + "</td><td>" + btnRelatedPref + "</td></tr>";
            } else {
                rowData = "<tr class='hidden'><td></td><td>" + lblDescription + "</td><td>"+ chkCorrect +"</td><td>"+ areaNote + "</td><td>" + chkResolved + "</td><td>" + btnRelatedPref + "</td></tr>";
            }           
                        
            rowRelatedPref = divRelatedPref;

            console.log(rowData);
            console.log(rowRelatedPref);
            console.log(item_section);

            if (current_section != item_section) {
                this.append_new_section($checklist_body, item_section_txt);
            }

            if (current_subsection != item_subsection) {
                this.append_new_subsection($checklist_body, item_section_txt, item_subsection_txt);
            }

            current_section = item_section;
            current_subsection = item_subsection;

            $checklist_body.append(rowData);
            if (related_preference != null){
                $checklist_body.append(rowRelatedPref);
            }                        
            console.log("Appended to checklist_body");
            
            $("#" + idCorrect).checkboxpicker();
            $("#" + idResolved).checkboxpicker();

        }
    },
    append_new_section: function(table, item_section_txt){
        section_has_checklist = false;
        for(var key in review_metadata){
            check_type = review_metadata[key]['check_type']
            if (review_metadata[key]['item_section_txt'] == item_section_txt){
                if (this.operation_type == "non-tech") {
                    if (check_type == '1') {
                        section_has_checklist = true;
                        break;
                    }
                } else if (this.operation_type == "tech") {
                    if (check_type == '2') {
                        section_has_checklist = true;
                        break;
                    }
                } else if (this.operation_type == "admin") {
                    section_has_checklist = true;
                    break;
                }
            }
        }
        if (section_has_checklist) {
            rowNewSection = "<tr><td colspan='6'><div><h4>" + item_section_txt + "</h4></div></td></tr>";
            table.append(rowNewSection);
        }
    },
    append_new_subsection: function(table, item_section_txt, item_subsection_txt){
        subsection_has_checklist = false;
        for(var key in review_metadata){
            check_type = review_metadata[key]['check_type']
            if (review_metadata[key]['item_subsection_txt'] == item_subsection_txt){
                if (this.operation_type == "non-tech") {
                    if (check_type == '1') {
                        subsection_has_checklist = true;
                        break;
                    }

                } else if (this.operation_type == "tech") {
                    if (check_type == '2') {

                        subsection_has_checklist = true;
                        break;
                    }
                } else if (this.operation_type == "admin") {
                    subsection_has_checklist = true;
                    break;
                }
            }
        }
        if (subsection_has_checklist) {
            subsection_header = (item_subsection_txt == '') ? item_section_txt : item_subsection_txt;
            rowNewSubsection = "<tr><td colspan='6' style='padding-left: 30px;'><strong>" + subsection_header + "</strong></td></tr>"
            table.append(rowNewSubsection);
        }
    },
    get_current_item_checklist_data: function(id){
        var correct = false;
        var note = "";
        var resolved = false;
        var is_current_check_type = false;
        var checklist_data = this.checklist_data;
        
        for (var key in checklist_data) {
            check_id = checklist_data[key]['id'];
            console.log("check_id: ", check_id, id);
            if (id == check_id){
                console.log(checklist_data[key]['correct']);
                console.log(checklist_data[key]['note']);
                console.log(checklist_data[key]['resolved']);
                correct = checklist_data[key]['correct'];
                note = checklist_data[key]['note'];
                resolved = checklist_data[key]['resolved'];
                console.log("returned", check_id, correct, note, resolved);
                break;
            }            
        }
        return {
            'correct': correct,
            'note': note,
            'resolved': resolved
        };     
    },
    get_checklist_data: function(){
        var json_checklist_data = [];
        var review_metadata = this.review_metadata;
        for (var key_meta in review_metadata) {
            id = review_metadata[key_meta]['id'];
            item_section = review_metadata[key_meta]['item_section'];
            item_subsection = review_metadata[key_meta]['item_subsection'];
            
            idCorrect = "#chk-correct-" + item_section + "-" + item_subsection + "-" + id;
            idNote = "#area-note-" + item_section + "-" + item_subsection + "-" + id;
            idResolved = "#chk-resolved-" + item_section + "-" + item_subsection + "-" + id;

            var checklist_row = {  
                'id': id,
                'correct': $(idCorrect).is(":checked"),
                'note': $(idNote).val(),
                'resolved': $(idResolved).is(":checked")
            };
            json_checklist_data.push(checklist_row);                              
        }  
        return json_checklist_data;             
    }
};