from django import forms

class SpiralForm(forms.Form):
    twitter_handles = forms.CharField()
    command = forms.ChoiceField(
        (('friend_overlap', "Top Follows in Common"),
         ('follower_overlap', "Top Followers in Common"),
         ('group_profile', "Group Profile")))
    trigger_rate_limit = forms.BooleanField(widget=forms.HiddenInput(),
                                            required=False)

class AutocompleteForm(forms.Form):
    term = forms.CharField()
    