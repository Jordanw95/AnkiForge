class StandardModel():
    model_name = 'Basic (and reversed card)'
    css = """.card {
font-family: arial;
font-size: 20px;
text-align: center;
color: black;
background-color: white;
}
.media {
margin: 2px;
}"""
    fields = [
                {'name': 'Question'},
                {'name': 'Answer'},
                {'name': 'MyMedia'},
                {'name': 'MyAudio'}, 
            ]
    templates = [
                {
                    'name': 'Card 1',
                    'qfmt': '{{Question}}<br>{{MyMedia}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br>{{MyAudio}}',
                }, 
                {
                    'name': 'Card 3',
                    'qfmt': '{{MyAudio}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br>{{Question}}<br>{{MyMedia}}',
                },           
            ]

class PrettyStandardModel():
    model_name = 'Pretty Standard Model (with reverse)'
    css =""".card {
font-family:Avantgarde, TeX Gyre Adventor, URW Gothic L, sans-serif;
font-size: 24px;
text-align: center;
color: black;
background-color #20bf55;
background-image: linear-gradient(315deg, #20bf55 0%, #01baef 74%);
}
* {box-sizing: border-box;}

.container-front{
max-height:400px;
padding: 10px;
display: flex;
justify-content:center;
flex-wrap: nowrap;
align-items: center;
border-radius:0.2em;
border-radius:10px 10px 10px 10px;
background-color: rgba(255, 255, 255, 0.5);
}
.push{
margin-left:auto;
padding:10px;
}
.native-front{
width:50%;
display:flex;
font-size:0.9em;
font-style:italic;
padding-left: 20px;
padding-bottom:5px;
border-bottom:solid;
border-color: rgba(182, 186, 186, 0.9);
border-width: 1px;
}

img{
border-radius:10%;
width:auto;
height:auto;
max-width300px;
max-height:300px;
}
.container-back{
max-height:300px;
padding: 10px;
justify-content:center;
flex-wrap: nowrap;
align-items: center
font-size:24px;
font-style:italic;
padding: 10px;
display: flex;
align-items:center;
border-radius:10px 10px 0px 0px;
background-color: rgba(255, 255, 255, 0.5);
}
.learnt{
font-size:24px;
font-style:italic;
justify-content:center;
padding:10px;
display: flex;
align-items:center;
border-radius:0px 0px 10px 10px;
background-color: #f9ea8f;
background-image: linear-gradient(315deg, #f9ea8f 0%, #aff1da 74%);
}
.audiobutton{
display:none;
}
body {
    background-attachment: fixed
}"""
    fields = [
                {'name': 'Native'},
                {'name': 'Learnt'},
                {'name': 'MyMedia'},
                {'name': 'MyAudio'}, 
            ]
    templates = [
                {
                    'name': 'Card 1',
                    'qfmt': """<div class=container-front id=container-front>
	<div class=native-front>
		{{Native}} 
	</div>
	<div class =push>
		{{MyMedia}}
	</div>
</div>""",
                    'afmt': """<div class = answer-background>
	<div class=container-back id=container-back>
		<div class= native-front id=native-front>
			{{Native}}
		</div>
		<div class =push>
			{{MyMedia}}
		</div>
	</div>
	<div class=learnt>
		{{Learnt}}
	</div>
	<div class = audiobutton>
		{{MyAudio}}
	</div>
</div>""",
                }, 
                {
                    'name': 'Card 3',
                    'qfmt': '{{MyAudio}}',
                    'afmt': """<div class = answer-background>
	<div class=container-back id=container-back>
		<div class= native-front id=native-front>
			{{Native}}
		</div>
		<div class =push>
			{{MyMedia}}
		</div>
	</div>
	<div class=learnt>
		{{Learnt}}
	</div>
	<div class = audiobutton>
		{{MyAudio}}
	</div>
</div>""",
                },           
            ]


class PrettyStandardModelNoImage():
    model_name = 'Pretty Standard Model (with reverse)'
    css =""".card {
font-family:Avantgarde, TeX Gyre Adventor, URW Gothic L, sans-serif;
font-size: 24px;
text-align: center;
color: black;
background-color #20bf55;
background-image: linear-gradient(315deg, #20bf55 0%, #01baef 74%);
}
* {box-sizing: border-box;}

.container-front{
max-height:400px;
padding: 10px;
display: flex;
justify-content:center;
flex-wrap: nowrap;
align-items: center;
border-radius:0.2em;
border-radius:10px 10px 10px 10px;
background-color: rgba(255, 255, 255, 0.5);
}
.push{
margin-left:auto;
padding:10px;
}
.native-front{
width:50%;
align-items: center;
font-size:0.9em;
font-style:italic;
padding-left: 20px;
padding-bottom:5px;
border-bottom:solid;
border-color: rgba(182, 186, 186, 0.9);
border-width: 1px;
}

img{
border-radius:10%;
width:auto;
height:auto;
max-width300px;
max-height:300px;
}
.container-back{
max-height:300px;
padding: 10px;
justify-content:center;
flex-wrap: nowrap;
align-items: center
font-size:24px;
font-style:italic;
padding: 10px;
display: flex;
align-items:center;
border-radius:10px 10px 0px 0px;
background-color: rgba(255, 255, 255, 0.5);
}
.learnt{
font-size:24px;
font-style:italic;
justify-content:center;
padding:10px;
display: flex;
align-items:center;
border-radius:0px 0px 10px 10px;
background-color: #f9ea8f;
background-image: linear-gradient(315deg, #f9ea8f 0%, #aff1da 74%);
}
.audiobutton{
display:none;
}
body {
    background-attachment: fixed
}"""
    fields = [
                {'name': 'Native'},
                {'name': 'Learnt'},
                {'name': 'MyAudio'}, 
            ]
    templates = [
                {
                    'name': 'Card 1',
                    'qfmt': """<div class=container-front id=container-front>
	<div class=native-front>
		{{Native}} 
	</div>
</div>""",
                    'afmt': """<div class = answer-background>
	<div class=container-back id=container-back>
		<div class= native-front id=native-front>
			{{Native}}
		</div>
	</div>
	<div class=learnt>
		{{Learnt}}
	</div>
	<div class = audiobutton>
		{{MyAudio}}
	</div>
</div>""",
                }, 
                {
                    'name': 'Card 3',
                    'qfmt': '{{MyAudio}}',
                    'afmt': """<div class = answer-background>
	<div class=container-back id=container-back>
		<div class= native-front id=native-front>
			{{Native}}
		</div>
	</div>
	<div class=learnt>
		{{Learnt}}
	</div>
	<div class = audiobutton>
		{{MyAudio}}
	</div>
</div>""",
                },           
            ]

class PrettyStandardModelNoAudio():
    model_name = 'Pretty Standard Model (with reverse)'
    css =""".card {
font-family:Avantgarde, TeX Gyre Adventor, URW Gothic L, sans-serif;
font-size: 24px;
text-align: center;
color: black;
background-color #20bf55;
background-image: linear-gradient(315deg, #20bf55 0%, #01baef 74%);
}
* {box-sizing: border-box;}

.container-front{
max-height:400px;
padding: 10px;
display: flex;
justify-content:center;
flex-wrap: nowrap;
align-items: center;
border-radius:0.2em;
border-radius:10px 10px 10px 10px;
background-color: rgba(255, 255, 255, 0.5);
}
.push{
margin-left:auto;
padding:10px;
}
.native-front{
width:50%;
display:flex;
font-size:0.9em;
font-style:italic;
padding-left: 20px;
padding-bottom:5px;
border-bottom:solid;
border-color: rgba(182, 186, 186, 0.9);
border-width: 1px;
}

img{
border-radius:10%;
width:auto;
height:auto;
max-width300px;
max-height:300px;
}
.container-back{
max-height:300px;
padding: 10px;
justify-content:center;
flex-wrap: nowrap;
align-items: center
font-size:24px;
font-style:italic;
padding: 10px;
display: flex;
align-items:center;
border-radius:10px 10px 0px 0px;
background-color: rgba(255, 255, 255, 0.5);
}
.learnt{
font-size:24px;
font-style:italic;
justify-content:center;
padding:10px;
display: flex;
align-items:center;
border-radius:0px 0px 10px 10px;
background-color: #f9ea8f;
background-image: linear-gradient(315deg, #f9ea8f 0%, #aff1da 74%);
}
.audiobutton{
display:none;
}
body {
    background-attachment: fixed
}"""
    fields = [
                {'name': 'Native'},
                {'name': 'Learnt'},
                {'name': 'MyMedia'},
            ]
    templates = [
                {
                    'name': 'Card 1',
                    'qfmt': """<div class=container-front id=container-front>
	<div class=native-front>
		{{Native}} 
	</div>
	<div class =push>
		{{MyMedia}}
	</div>
</div>""",
                    'afmt': """<div class = answer-background>
	<div class=container-back id=container-back>
		<div class= native-front id=native-front>
			{{Native}}
		</div>
		<div class =push>
			{{MyMedia}}
		</div>
	</div>
	<div class=learnt>
		{{Learnt}}
	</div>
</div>""",
                }, 
                {
                    'name': 'Card 3',
                    'qfmt':  """<div class=container-front id=container-front>
	<div class=native-front>
		{{Learnt}} 
	</div>
	<div class =push>
		{{MyMedia}}
	</div>
</div>""",
                    'afmt': """<div class = answer-background>
	<div class=container-back id=container-back>
		<div class= native-front id=native-front>
			{{Native}}
		</div>
		<div class =push>
			{{MyMedia}}
		</div>
	</div>
	<div class=learnt>
		{{Learnt}}
	</div>
</div>""",
                },           
            ]