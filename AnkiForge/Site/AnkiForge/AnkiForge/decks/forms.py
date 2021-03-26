from django.forms import ModelForm, TextInput
from decks.models import UserDecks
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML, Div


# class CreateUserDeck(ModelForm):
    
#     class Meta:
#         model = UserDecks
#         fields = ['ankiforge_deck_name', 'anki_deck_name', 'native_lang', 'learnt_lang', 'images_enabled', 'audio_enabled', 'model_code']
#         # Write custom help text etc in helptexts dictionary
#         help_texts = {
#             'ankiforge_deck_name': _('The name of the deck that will appear on this website.'),
#             'anki_deck_name': _('This MUST match the name of your deck as it appears in Anki.')
#         }
 

class CreateUserDeckForm(ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(CreateUserDeckForm, self).__init__(*args, **kwargs)

        # If you pass FormHelper constructor a form instance
        # It builds a default layout with all its fields
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        # You can dynamically adjust your layout
        self.helper.layout = Layout(
            Row(
                Column('ankiforge_deck_name', css_class = 'form-group col-md-6 mb-0'),
                Column('anki_deck_name', css_class = 'form-group col-md-6 mb-0'),
                css_class='form-row',
                ),
            HTML("<br>"),
            Row(
                css_class='form-row',
            ),
            Row(
                Column('native_lang', css_class='form-group col-md-3 mb-0'),
                Column('learnt_lang', css_class='form-group col-md-3 mb-0'),
                Column('model_code', css_class = 'form-group col-md-6 mb-0'),
                css_class='form-row',
            ),
            HTML("<br>"),
            # Row(
            #     Column('audio_enabled', css_class='form-group col-md-6 mb-0'),
            #     Column('images_enabled', css_class='form-group col-md-6 mb-0'),
            #     css_class = 'form-row',
            # ),
            Div(
                Submit('submit', 'Save this deck'),
                css_class='text-center'
            )
            )

    
    class Meta:
        model = UserDecks
        fields = [
            'ankiforge_deck_name', 'anki_deck_name', 'native_lang',
             'learnt_lang', 
            #  'images_enabled', 'audio_enabled', 
             'model_code'
        ]
        # Write custom help text etc in helptexts dictionary
        help_texts = {
            'ankiforge_deck_name': _('The name of the deck that will appear on this website.'),
            'anki_deck_name': _('If you want to add to a deck you already have, this MUST match the name of your deck as it appears in Anki.'),
            'native_lang' :_('We are working on making this available for native languages other than english.'),
            'model_code' : _("This will decide how the cards made will appear. See  default models page to see previews of the layouts listed here. "),
            # 'audio_enabled' :_('Add high quality audio files, in the learnt language, to cards made using this deck, formed using Google or Azure Text-To-Speech (the service used is chosen depending on which service offers the highest quality audio for that language). Disabling this option will save X points per card.'),
            # 'images_enabled' : _('Add relevant images to your cards, shown to help improve retention of words. Disabling this option will save X points per card'),
        }
        labels = {
            'ankiforge_deck_name' : _('Deck tag for AnkiForge'),
            'anki_deck_name' : _('Name of Deck in Anki'),
            'model_code' : _('Card Layout'),
            'native_lang' : _('Native Language'),
            'learnt_lang' : _('Language Learnt'),
            # 'images_enabled' : _('Enable Images'),
            # 'audio_enabled' : _('Enable Audio'),
        }
        widgets = {
            'ankiforge_deck_name' : TextInput(attrs = {
                'placeholder' : 'This is a tag for you to recognise this deck on AnkiForge',
                'max_length' : 50
            }),
            'anki_deck_name' : TextInput(attrs = {
                'placeholder' : 'This should match exactly the name of your deck on Anki',
                'max_length' : 50
            }),
        }

    