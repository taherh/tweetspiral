// Generated by CoffeeScript 1.3.3
(function() {

  $(function() {
    $('#id_twitter_handles').triggeredAutocomplete({
      source: "/autocomplete.json",
      trigger: "@"
    });
    return $(".hovercard").hovercard({
      showTwitterCard: true,
      openOnTop: true,
      width: 350
    });
  });

}).call(this);