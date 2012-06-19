
// Set up our namespace
if (typeof TweetSpiral === "undefined" || !TweetSpiral) { TweetSpiral = {}; }

$(document).ready(function() {
    $('#id_twitter_handles').triggeredAutocomplete({
        source: "/autocomplete.json",
        trigger: "@"
    });
});
