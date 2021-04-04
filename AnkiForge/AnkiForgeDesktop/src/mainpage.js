const settings = require('electron-settings');
const electron = require('electron'); 
const electronRemote = require('electron').remote
const electronRemoteApp = require('electron').remote.app

// importing module is done through remote of main.js
const net = electron.remote.net; 
const globalShortcut = electron.remote.globalShortcut

// variables
var userKey= settings.getSync('UserAuth.userKey')
var headerKey = "Token " + userKey
// var userDecks = [{"id":56,"user":2,"deck_id":5696702418,"ankiforge_deck_name":"Spanish Cram","anki_deck_name":"Spanish Cram","native_lang":"en","learnt_lang":"es","images_enabled":true,"audio_enabled":true,"model_code":2}];
var selectedDeck = [{empty:"empty"}];
var shortcutSetting = settings.getSync('General.shortcut')
var userMembership = []
console.log("Inital Setting")
console.log(shortcutSetting)
getUserDecks();

console.log(shortcutSetting)
// Document objects
var deckList = document.getElementById("decklist");
var incomingInput = document.getElementById("incomingquote");
var sendQuote = document.getElementById("sendcard")
var quoteFeedback = document.getElementById("quotefeedback")
var signOut = document.getElementById("signout")
var toggleShortcut = document.getElementById('shortcut-toggle')
var forgeCount = document.getElementById("forgecount")
var userPoints = document.getElementById("userpoints")
checkShortcutSetting();

async function checkShortcutSetting(){
    if (settings.hasSync('General.shortcut')){
        // nothing
        if (shortcutSetting){
            toggleShortcut.innerHTML = "Disable";
        }
    }else{
        // make toggle shortcut false, set setting
        shortcutSetting= 0;
        await settings.set('General',  {
            shortcut : 0,
        });
        toggleShortcut.innerHTML = "Enable";
    }
}

// Probably have some safegaurd that this needs to be enabled
// Register shortkey
// Add some string checks before sending
electronRemoteApp.whenReady().then(() => {
    // Register a 'Alt+X' shortcut listener.
    const ret = globalShortcut.register('Alt+X', () => {
        if (shortcutSetting){
            const { clipboard } = require('electron')
            console.log('Alt+X is pressed')
            var copiedText = clipboard.readText('selection')
            console.log(copiedText)
            if (0 < copiedText.len < 255){
                console.log(copiedText.len)
                sendFromKeyboard(copiedText)
                getReadyForForge()
                getUserPoints()
            }else{
                console.log("Length of string too long")
            }
        }else{
            quoteFeedback.innerHTML = "You need to enable the shortcut below!";
        }
    })
  
    if (!ret) {
      console.log('registration of shortkey failed')
    }
  
    // Check whether a shortcut is registered.
    console.log(globalShortcut.isRegistered('Alt+X'))
  })

// Unregister on logout 
electronRemoteApp.on('will-quit', () => {
    // Unregister a shortcut.
    globalShortcut.unregister('Alt+X')

    // Unregister all shortcuts.
    globalShortcut.unregisterAll()
})

function getUserDecks(){
    const request = net.request({ 
        method: 'GET', 
        url: 'http://127.0.0.1:8000/forge/api/userdecks', 
        path: '/get', 
        redirect: 'follow'
    });
    request.on('response', (response) => { 
        console.log(`STATUS: ${response.statusCode}`); 
        console.log(`HEADERS: ${JSON.stringify(response.headers)}`); 
        
        response.on('data', (chunk) => { 
            console.log(`BODY: ${chunk}`)
            // There seems to be an error with parsing if json is too long
            // Maybe could append on each response and then on finish carry out the rest
            userDecks = JSON.parse(chunk)
            if (userDecks.length === 0){
                document.getElementById("optionData").innerHTML = "It looks as if you don't currently have any decks. Go to the website to make some and begin using the desktop applications"
            } else{
                // This all needs to be done after receiving
                // Creating list of decks
                Object.keys(userDecks).map((key) => deckList.add(new Option(userDecks[key].ankiforge_deck_name, JSON.stringify(userDecks[key]))));
                // Listen to input on list
                // deckList.addEventListener("input", () => document.getElementById("optionData").innerHTML = deckList.value);
                // Set defaults for inital values
                // document.getElementById("optionData").innerHTML = JSON.stringify(userDecks[0]);
                selectedDeck = JSON.parse(deckList.value);
                deckList.addEventListener("input", () => {
                    selectedDeck=JSON.parse(deckList.value);
                    getReadyForForge()   
                })
            }
            getReadyForForge()
        });
    });
    request.on('finish', ()=>{
        
    });
    request.setHeader('Content-Type', 'application/json'); 
    request.setHeader('Authorization', headerKey); 
    request.end(); 
}


sendQuote.addEventListener('click', ()=>{
    var selectedDeckId = selectedDeck.id
    console.log(selectedDeckId)
    var body = JSON.stringify({"deck": selectedDeckId, "incoming_quote" : incomingInput.value})
    console.log(body)
    const request = net.request({
        method: 'POST',
        url : 'http://127.0.0.1:8000/forge/api/usercards/'
    });
    request.on('response', (response) => { 
        console.log(`STATUS: ${response.statusCode}`); 
        console.log(`HEADERS: ${JSON.stringify(response.headers)}`); 
        var status= `${response.statusCode}`
        if (status == "201"){
            var formattedQuote = "'".concat(incomingInput.value, "'")
            var successReponse = "Your quote : ".concat(formattedQuote, " has been sent to the deck: ", selectedDeck.ankiforge_deck_name)
            quoteFeedback.innerHTML = successReponse;
            incomingInput.value = "";
        }else{
            quoteFeedback.innerHTML = "It appears there was an error sending this quote. Do you have an active subscription and usage remaining for this month? You can check this on the account section of the website. Please get in touch at ankiforge@gmail.com if you can't resolve the issue."
            incomingInput.value = "";
        }
    }); 
    request.on('finish', () => { 
        console.log('Request is Finished') 
        getUserDecks()
        getUserPoints()
    }); 
    request.on('abort', () => { 
        console.log('Request is Aborted') 
    }); 
    request.on('error', (error) => { 
        console.log(`ERROR: ${JSON.stringify(error)}`) 
    }); 
    request.on('close', (error) => { 
        console.log('Last Transaction has occured') ;
    }); 
    userKey= settings.getSync('UserAuth.userKey')
    headerKey = "Token " + userKey
    request.setHeader('Content-Type', 'application/json'); 
    request.setHeader('Authorization', headerKey); 
    request.write(body, 'utf-8'); 
    request.end(); 
}); 

// Fucntion for keyboard shortcut
function sendFromKeyboard(incomingtext){
    var selectedDeckId = selectedDeck.id
        console.log(selectedDeckId)
        var body = JSON.stringify({"deck": selectedDeckId, "incoming_quote" : incomingtext})
        console.log(body)
        const request = net.request({
            method: 'POST',
            url : 'http://127.0.0.1:8000/forge/api/usercards/'
        });
        request.on('response', (response) => { 
            console.log(`STATUS: ${response.statusCode}`); 
            console.log(`HEADERS: ${JSON.stringify(response.headers)}`); 
            var status= `${response.statusCode}`
            if (status == "201") {                
                var formattedQuote = "'".concat(incomingtext, "'")
                var successReponse = "Your quote : ".concat(formattedQuote, " has been sent to the deck: ", selectedDeck.ankiforge_deck_name)
                quoteFeedback.innerHTML = successReponse;
            }else{
                quoteFeedback.innerHTML = "It appears there was an error sending this quote. Do you have an active subscription and usage remaining for this month? You can check this on the account section of the website. Please get in touch at ankiforge@gmail.com if you can't resolve the issue."
            }
        }); 
        request.on('finish', () => { 
            console.log('Request is Finished') 
        }); 
        request.on('abort', () => { 
            console.log('Request is Aborted') 
        }); 
        request.on('error', (error) => { 
            console.log(`ERROR: ${JSON.stringify(error)}`) 
        }); 
        request.on('close', (error) => { 
            console.log('Last Transaction has occured') ;
        }); 
        request.setHeader('Content-Type', 'application/json'); 
        request.setHeader('Authorization', headerKey); 
        request.write(body, 'utf-8'); 
        request.end(); 
}; 

toggleShortcut.addEventListener('click', async () =>{
    console.log("LCICICICKCKC")
    if (shortcutSetting){
        // nothing
        console.log("Here")
        shortcutSetting = 0;
        await settings.set('General',  {
            shortcut : 0,
        });
        toggleShortcut.innerHTML = "Enable";
    }else{
        console.log("Here2")
        // make toggle shortcut false, set setting
        shortcutSetting= 1;
        await settings.set('General',  {
            shortcut : 1,
        });
        toggleShortcut.innerHTML = "Disable"
    }
});


// Get Cards Ready for forge
function getReadyForForge(){
    console.log(selectedDeck.id)
    var body = JSON.stringify({"deck": selectedDeck.id})
    console.log(body)
    const request = net.request({ 
        method: 'GET', 
        url: 'http://127.0.0.1:8000/forge/api/userreadyforforge', 
        path: '/get', 
        redirect: 'follow'
    });
    request.on('response', (response) => { 
        console.log(`STATUS: ${response.statusCode}`); 
        console.log(`HEADERS: ${JSON.stringify(response.headers)}`); 
        
        response.on('data', (chunk) => { 
            console.log(`BODY: ${chunk}`)
            var cardsForForge = JSON.parse(chunk)
            var numberOfCards = cardsForForge.length
            forgeCount.innerHTML = "Click to forge " + numberOfCards + " waiting cards"
            })
        });;
    request.on('finish', ()=>{
        console.log("Select incoming Request Finished")   
    });
    request.setHeader('Content-Type', 'application/json'); 
    request.setHeader('Authorization', headerKey);
    request.write(body, 'utf-8')
    request.end(); 
}

forgeCount.addEventListener('click' , () => {
    var ankiforgeUrl = "http://127.0.0.1:8000/"
    var deckUrl = ankiforgeUrl + "forge/forgedecks/" + selectedDeck.id + "/"
    require("electron").shell.openExternal(deckUrl);
})

function getUserPoints(){
    const request = net.request({ 
        method: 'GET', 
        url: 'http://127.0.0.1:8000/forge/api/userpoints', 
        path: '/get', 
        redirect: 'follow'
    });
    request.on('response', (response) => { 
        console.log(`STATUS: ${response.statusCode}`); 
        console.log(`HEADERS: ${JSON.stringify(response.headers)}`); 
        
        response.on('data', (chunk) => { 
            console.log(`BODY: ${chunk}`)
            userMembership = JSON.parse(chunk)
            var numberOfPoints = userMembership[0].user_points
            userPoints.innerHTML = ((numberOfPoints/300000)*100).toFixed(1) + "% Credit remaining this month"
            })
        });;
    request.on('finish', ()=>{
        console.log("Select incoming Request Finished")   
    });
    request.setHeader('Content-Type', 'application/json'); 
    request.setHeader('Authorization', headerKey);
    request.end(); 
}

getUserPoints()