$(document).ready(function(){
    // Functions for Edit mode
    $('button[name= "editbtn"]').on('click', function(e) {
        var val = $(this).attr('value');
        console.log(val);
        if (val === "Edit"){
            $("a.details-link").on("click", false);

            // Reveal the checkboxes and other edit mode buttons
            $('button[name="deletebtn"]').prop('hidden', false);
            $('.btn_chk').prop('hidden', false);
            $('button[name= "collbtn"]').hide();

            // Change the button name and value
            $('button[name= "editbtn"]').html("Cancel");
            $('button[name= "editbtn"]').val("Cancel");
        }else{
            $("a.details-link").off("click");

            // Hide the checkboxes and other edit mode buttons
            $('button[name="deletebtn"]').prop('hidden', true);
            $('button[name= "collbtn"]').show();
            $('.btn_chk').prop('hidden', true);

            // Reset the button name and value. Uncheck any boxes that were selected
            $('button[name= "editbtn"]').html("Edit");
            $('button[name= "editbtn"]').val("Edit");
            $(".selected").addClass("collection");
            $(".selected").removeClass("selected");

            $.each($("input.btn_chk:checked"), function(){
                $(this).prop("checked", false);
            });
        }
    });
//    Delete the selected items from the collection
    $('button[name= "deletebtn"]').on('click', function(e) {
        var selected_boxes = [];
        $.each($("input.btn_chk:checked"), function(){
            selected_boxes.push($(this).val());
        });

        confirmation = confirm("Are you sure you want to delete the selected series?");

        if (confirmation){
            $.ajax({
                type: 'POST',
                url: '/remove_from_collection',
                data:{
                    csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
                    to_delete: JSON.stringify(selected_boxes)
                },
                success: function(){
                    alert("Removed from collection");
                    location.reload(true);
                }
            });
        }
    });

    // Change the color of the border in edit mode
    $('.btn_chk').on('click', function(e){
        $(this).parent().toggleClass("selected");
        $(this).parent().toggleClass("collection");
    });
    $("#checkAll").click(function(){
        console.log("Check all");
        $("input[type=checkbox]").trigger("click");
        $("input[type=checkbox]").prop('checked', true);
    });
    //Ajax functions
    //Modify the read status of the chapter on clicking checkbox.
    $('input.read_class').on('click', function(e) {
        console.log("Mark read");
        e.stopPropagation();
        $.ajax({
            type: 'POST',
            url: '/update_read',
            data:{
                csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
                pk: $(this).attr('data-id')
            },
            success: function(){
            }
        });
    });
    //Update read status on clicking link and reload the page once done
    $('a.read_class').on('click', function(e) {
        var pk = $(this).attr('data-id');
        $.ajax({
            type: 'POST',
            url: '/update_read',
            data:{
                csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
                pk: pk
            },
            success: function(){
                location.reload(true);
            }
        });
    });
//    Add entries from search to the collection and change the button on success
    $('button[name= "addcoll"]').on('click', function(e) {
        var pk = $(this).attr('data-id');
        $.ajax({
            type: 'POST',
            url: '/add_to_coll',
            data:{
                csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
                pk: pk
            },
            dataType: "json",
            success: function(data){
                alert("Added to collection");
                $("#"+pk).replaceWith(function(){
                    return "<button type='button' class='btn btn-secondary' disabled>Already In Collection</button>";
                });
            }
        });
    });
});

