//Amazon service interaction JS

function getUrlVars() {
	var vars = {};
	var parts = window.location.href.replace(/[?#&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
			vars[key] = value;
	});
	return vars;
}

var id_token = getUrlVars()["id_token"];

AWS.config.region = 'us-east-1';
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
	IdentityPoolId: 'us-east-1:65ef58e5-2f60-417b-a7b2-1675ad762faf',
	Logins: {
		'cognito-idp.us-east-1.amazonaws.com/us-east-1_ZsFDICqc6': id_token
	}
});

var apigClient;
AWS.config.credentials.refresh(function(){
	var accessKeyId = AWS.config.credentials.accessKeyId;
	var secretAccessKey = AWS.config.credentials.secretAccessKey;
	var sessionToken = AWS.config.credentials.sessionToken;
	AWS.config.region = 'us-east-1';
	apigClient = apigClientFactory.newClient({
		accessKey: AWS.config.credentials.accessKeyId,
		secretKey: AWS.config.credentials.secretAccessKey,
		sessionToken: AWS.config.credentials.sessionToken, // this field was missing
		region: 'us-east-1'
	});
});

var identityId = AWS.config.credentials.identityId;

var messages = [], //array that hold the record of each string in chat
  lastUserMessage = "", //keeps track of the most recent input string from the user
  botMessage = "", //var keeps track of what the chatbot is going to say
  botName = 'Chatboy', //name of the chatbot
  talking = true; //when false the speach function doesn't work

	function chatbotResponse() {
		
		// User's own message for display
		lastUserMessage = userMessage();
		return new Promise(function (resolve, reject) {
			talking = true;
			let params = {};
			let additionalParams = {
				headers: {
				"x-api-key" : 'L9Re0I5GsN7Y5JO3Ix1Tr6jMF9AY1OMg2hQZxbQP'
				}
			};
			var body = {
			"message" : lastUserMessage,
			"identityID": identityId
			}
			apigClient.chatbotPost(params, body, additionalParams)
			.then(function(result){
				
				reply = result.data.body;
			
				$("<li class='replies'><p>" + reply + "</p></li>").appendTo($('.messages ul'));
				$('.message-input input').val(null);
				$('.contact.active .preview').html('<span>You: </span>' + reply);
				$(".messages").animate({ scrollTop: $(document).height() }, "fast");
				
				resolve(result.data.body);
				botMessage = result.data.body;
			}).catch( function(result){
				// Add error callback code here.
				console.log(result);
				botMessage = "Couldn't connect"
				reject(result);
			});
		})
	}


//Js for the chat application


$(".messages").animate({ scrollTop: $(document).height() }, "fast");

$("#profile-img").click(function() {
	$("#status-options").toggleClass("active");
});

$(".expand-button").click(function() {
  $("#profile").toggleClass("expanded");
	$("#contacts").toggleClass("expanded");
});

$("#status-options ul li").click(function() {
	$("#profile-img").removeClass();
	$("#status-online").removeClass("active");
	$("#status-away").removeClass("active");
	$("#status-busy").removeClass("active");
	$("#status-offline").removeClass("active");
	$(this).addClass("active");
	
	if($("#status-online").hasClass("active")) {
		$("#profile-img").addClass("online");
	} else if ($("#status-away").hasClass("active")) {
		$("#profile-img").addClass("away");
	} else if ($("#status-busy").hasClass("active")) {
		$("#profile-img").addClass("busy");
	} else if ($("#status-offline").hasClass("active")) {
		$("#profile-img").addClass("offline");
	} else {
		$("#profile-img").removeClass();
	};
	
	$("#status-options").removeClass("active");
});

function userMessage() {
	message = $(".message-input input").val();
	if($.trim(message) == '') {
		return false;
	}

	$('<li class="sent"><p>' + message + '</p></li>').appendTo($('.messages ul'));
	$('.message-input input').val(null);
	$('.contact.active .preview').html('<span>You: </span>' + message);
	$(".messages").animate({ scrollTop: $(document).height() }, "fast");

	return message;
};

$('.submit').click(function() {
	// newMessage();
	chatbotResponse();
});

$(window).on('keydown', function(e) {
  if (e.which == 13) {
		// newMessage();
		chatbotResponse();
    return false;
  }
});