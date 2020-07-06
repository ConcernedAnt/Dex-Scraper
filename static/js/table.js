$(document).ready(function() {
    $.fn.dataTable.moment( 'MMMM D, YYYY');
    $.fn.dataTableExt.oSort["test-pre"] = function (x)
    {
        var a = $(x).text();
        return parseFloat(a.trim().substring(4));
    };
    $.fn.dataTableExt.oSort["test-desc"] = function (x, y)
    {
        if ( x > y)
        {
            return -1;
        }
        return 1;

    };

    $.fn.dataTableExt.oSort["test-asc"] = function (x, y)
    {
        if ( x > y)
        {
            return 1;
        }
        return -1;
    }
    var table = $('#mydatatable').DataTable( {
        language: {
            "emptyTable": "No Updates Available For This Manga"
        },
        sDom: 'lrtip',
        bInfo : false,
        rowReorder: true,
        scrollY: 540,
        paging: false,
        columnDefs: [
            {targets: 0, type: "test"},
            {targets: 1, type: 'datetime-moment'},
            {targets: 2, orderDataType: "dom-checkbox"}
        ]
    } );
} );

