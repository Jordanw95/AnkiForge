from decks.models import IncomingCards, UserDecks
from django.forms import ModelForm, TextInput
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML, Div


class AddIncomingCardForm(ModelForm) : 

    def __init__(self, *args, **kwargs):
        super(AddIncomingCardForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            Row(
                Column('incoming_quote', css_class = 'form-group col-md-8 mb-0'),
                Column('deck', css_class = 'form-group col-md-4 mb-0'),
                css_class='form-row',
            ),
            HTML("<br>"),
            Div(
                Submit('submit', 'Make this card', css_class = 'text_center'),
                css_class='text-center',
            ),
        )
    
    class Meta: 
        model = IncomingCards
        fields = [
            'incoming_quote', 'deck'
        ]