const settings = require('electron-settings');
const electron = require('electron'); 
// Importing the net Module from electron remote 
const net = electron.remote.net; 

// Making links open in new window
const shell = require('electron').shell;

$(document).on('click', 'a[href^="http"]', function(event) {
    event.preventDefault();
    shell.openExternal(this.href);
});


// Variables


// dccument values 
var login = document.getElementById('login');
var loginInput = document.getElementById('username'); 
var loginPassword = document.getElementById('password');
var testing = document.getElementById('testing');
var testAuth = document.getElementById('testauth')
var loginFeedback = document.getElementById('loginfeedback')



login.addEventListener('click', ()=>{
    var body = JSON.stringify({"username": loginInput.value, "password":loginPassword.value})
    const request = net.request({
        method: 'POST',
        url : 'https://ankiforge.com/api/auth/login'
    });
    request.on('response', (response) => { 
        console.log(`STATUS: ${response.statusCode}`); 
        console.log(`HEADERS: ${JSON.stringify(response.headers)}`); 
        if (`${response.statusCode}` == "200"){
            response.on('data', async (chunk) => { 
                console.log(`BODY: ${chunk}`);
                console.log(typeof chunk)
                console.log(typeof '${chunk}') 
                var dataArray = JSON.parse(chunk)
                console.log(dataArray)
                console.log(dataArray.key)
                if (dataArray.key) {
                    console.log("WE HAVE A LOGIN")
                    var key = dataArray.key
                    await settings.set('UserAuth',  {
                        userKey : key
                    });
                    window.location.href = "./mainpage.html"
                } else {
                    console.log("FAILED TO LOGIN")
                }
            });
        } else {
            loginFeedback.innerHTML = "You're login details were incorrect, try again. "
        };
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
        console.log('Last Transaction has occured') 
    }); 
    request.setHeader('Content-Type', 'application/json'); 
    request.write(body, 'utf-8'); 
    request.end(); 
}); 

// testing.addEventListener('click', ()=>{
//     var userKey= settings.getSync('UserAuth.userKey')
//     console.log(userKey)
// })

// Skip straight to next page




function testAuthFunc(){
    const request = net.request({ 
        method: 'GET', 
        url: 'https://ankiforge.com/forge/api/userdecks', 
        path: '/get', 
        redirect: 'follow'
    });
    request.on('response', (response) => { 
        console.log(`STATUS: ${response.statusCode}`); 
        console.log(`HEADERS: ${JSON.stringify(response.headers)}`); 
        // Just base it off of status code 200
        var status= `${response.statusCode}`
        if (status == "200"){
            window.location.href = "./mainpage.html"
        } else{
            console.log("USER NOT AUTHENTICATED")
        }
    });
    request.on('finish', ()=>{
        
    });
    var userKey= settings.getSync('UserAuth.userKey')
    var headerKey = "Token " + userKey
    request.setHeader('Content-Type', 'application/json'); 
    request.setHeader('Authorization', headerKey); 
    request.end(); 
}

testAuthFunc()

