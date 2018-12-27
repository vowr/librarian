// The scripts that follow are an EXPERIMENT in using jQuery/Javascript to automatically convert
// GET calls to POST calls
// Any anchor with the attribute "usepost" usses these functions.

// Any time an anchor is clicked and the "usepost" attibute is present, convert the href attribute
// to POST format, make a POST form and submit it

$(document).ready(function() {
	$('a.usepost').click(function(e) {
			// Automatically apply a confirmation dialog to "Delete" icons
			if (!($(this).hasClass('no-confirm')) && !($(this).hasClass('icon-embed-btn')) &&
			   ($(this).hasClass('fa-trash'))) {
				var msg = $.trim(this.textContent).toLowerCase();

				if (!msg)
					var msg = $.trim(this.value).toLowerCase();

				var q = 'Are you sure you wish to '+ msg +'?';

				if ($(this).attr('title') != undefined)
					q = 'Are you sure you wish to '+ $(this).attr('title').toLowerCase() + '?';

				if (!confirm(q)) {
					return false;
				}
			}

			var target = $(this).attr("href").split("?");

			postSubmit(get2post(target[1]),target[0]);
			return false;
	});
});

// Convert a GET argument list such as ?name=fred&action=delete into an object of POST
// parameters such as {name : fred, action : delete}
function get2post(getargs) {
	var argdict = {};
	var argarray = getargs.split('&');

	argarray.forEach(function(arg) {
		arg = arg.split('=');
		argdict[arg[0]] = arg[1];
	});

	return argdict;
}

// Create a form, add, the POST data and submit it
function postSubmit(data, target) {
	var $form = $('<form>');

	for (var name in data) {
		$form.append(
			$("<input>")
				.attr("type", "hidden")
				.attr("name", name)
				.val(data[name])
		);
    }

	$form
		.attr("method", "POST")
		.attr("action", target)
		.appendTo('body')
		.submit();
}

// Function for /append to send the data without refreshing the page
$(function () {

	$('form.ajax-sub').on('submit', function (e) {

	  e.preventDefault();

	  var posting = $.ajax({
		type: 'post',
		data: $('form').serialize(),
		// success: function () {
		//   alert('form was submitted');
		// }
	  });

	  posting.done(function( data ) {
		var status = document.getElementById('status').innerHTML;
		if ($.trim(status) == "<p>No changes made.</p>")
			status = data;
		else
			status = data + status;
		document.getElementById('status').innerHTML = status;
	  });

	});

  });

/*
* This script is invoked by the /playlists page. If the playlist dropdown is set to create_new, we display the field for the new playlist name.
*/
function checkNewPlaylist() {
	var e = document.getElementById("playlist");
	var newPlaylist = e.options[e.selectedIndex].value;
	if (newPlaylist === "create_new") {
		document.getElementById("new_playlist_field").innerHTML = '<input type="text" class="auto input-block-level thin" id="playlist_name" placeholder="Playlist Name">';
		document.getElementById("playlist_button").innerHTML = 'Add';
	} else  {
		document.getElementById("new_playlist_field").innerHTML = "";
		document.getElementById("playlist_button").innerHTML = 'Edit';
	}
}

/*
* This script is invoked by the sign in page to give the proper form for master or basic login
*/
function toggleLoginForm(type) {
	if (type === 'master') {
		document.getElementById('login-type-btn').innerHTML = '<a href="#" onclick="toggleLoginForm(\'basic\');" class="btn btn-default">Basic Login</a><a href="#" onclick="toggleLoginForm(\'master\');" class="btn btn-primary active">Master Login</a>';
		document.getElementById('passwd-field').innerHTML = '<input type="password" class="input-block-level" name="password" placeholder="Password">';
	} else if (type === 'basic') {
		document.getElementById('login-type-btn').innerHTML = '<a href="#" onclick="toggleLoginForm(\'basic\');" class="btn btn-primary active">Basic Login</a><a href="#" onclick="toggleLoginForm(\'master\');" class="btn btn-default">Master Login</a>';
		document.getElementById('passwd-field').innerHTML = '';
	}
}

function resizeBody(){
	topNavBar = $(".topnav")
	content = $(".outer-content")
	content.css({"marginTop": "calc("+$(".topnav").css("height") + " + 1.5pc)"})
}


/*
* This script handles auto-completion for any text inputs with the "auto" class.
*/
$(function() {
	$(".auto").autocomplete({
		minLength: 3,
		source: function (request, response) {
			$.ajax({
				url: "/search/auto",
				data: { var: this.element.attr("name"), val: request.term },
				dataType: "json",
				success: response,
				error: function () {
					response([]);
				}
			});
	}})

	window.onresize = resizeBody
	resizeBody()

});

function toggleNavMenu(){
	$('.z-nav__toggle').toggleClass('open-nav');
	var $mobileNav = $('.z-nav__list');
	var $cart = $('.cart__list');
	var $cartToggle = $('.cart__toggle');

	if($mobileNav.hasClass('open-nav')){
		$mobileNav.removeClass('open-nav close-nav');
		$mobileNav.addClass('close-nav');
	}
	else{
		$mobileNav.removeClass('open-nav close-nav');
		$mobileNav.addClass('open-nav');

		$cart.removeClass('open-nav close-nav');
		$cart.addClass('close-nav');
		$cartToggle.removeClass('open-nav close-nav');
		$cartToggle.addClass('close-nav');
	}
}