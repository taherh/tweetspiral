$ -> 
    $('#id_twitter_handles').triggeredAutocomplete(
        source: "/autocomplete.json"
        trigger: "@"
    )
    
    $(".hovercard").hovercard(
        showTwitterCard: true
        openOnTop: true
        width: 350
    );   
