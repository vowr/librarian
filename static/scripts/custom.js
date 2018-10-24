"use strict";

//Modernizr touch detect
Modernizr.load({
	test: Modernizr.touch,
	yep :['/static/style/touch.css?v=1'],
	nope: ['/static/scripts/waypoints.min.js'],
	complete : function () {
		if (Modernizr.touch){
			//initMobile
		}							 
		else{
			//initDesc
			
			//Animated header positioning
			var $head = $( '.header-fixed' );
			$( '.waypoint' ).each( function(i) {
				var $el = $( this ),
				animClassDown = $el.data( 'animateDown' ),
				animClassUp = $el.data( 'animateUp' );
							 
				$el.waypoint( function( direction ) {
					if( direction === 'down' && animClassDown ) {
						$head.attr('class', 'header-fixed ' + animClassDown);
					}
					else if( direction === 'up' && animClassUp ){
						$head.attr('class', 'header-fixed ' + animClassUp);
					}
				}, { offset: -250 });
			});	
		}
	}  
});

//Test if classList exist
var test = false;
if ("document" in self && !("classList" in document.createElement("_"))){
	test = true;
}

Modernizr.load({
  test: test,
  yep : ['external/classList/classList.js'],
  nope: []
});

//Plaeholder handler
if(!Modernizr.input.placeholder){             //placeholder for old brousers and IE
 
  $('[placeholder]').focus(function() {
   	var input = $(this);
   	if (input.val() == input.attr('placeholder')) {
    	input.val('');
    	input.removeClass('placeholder');
   	}
  }).blur(function() {
   	var input = $(this);
   	if (input.val() == '' || input.val() == input.attr('placeholder')) {
    	input.addClass('placeholder');
    	input.val(input.attr('placeholder'));
   	}
  }).blur();
 
  $('[placeholder]').parents('form').submit(function() {
   	$(this).find('[placeholder]').each(function() {
    	var input = $(this);
    	if (input.val() == input.attr('placeholder')) {
     		input.val('');
    	}
   	})
  });
 }

//Top link function
jQuery.fn.topLink = function(settings) {
	settings = jQuery.extend({
		min: 1,
		fadeSpeed: 200
	}, settings);
	
	return this.each(function() {
		//listen for scroll
		var el = $(this);
		el.hide(); //in case the user forgot
		$(window).scroll(function() {
			if($(window).scrollTop() >= settings.min)
			{
				el.fadeIn(settings.fadeSpeed);
			}
			else
			{
				el.fadeOut(settings.fadeSpeed);
			}
		});
	});
};
		    	
// Init for all template pages
$(document).ready(function() {
	// Call mobile menu 

	$('.z-nav__list').mobileMenu({
	    triggerMenu:'.z-nav__toggle',
		subMenuTrigger: ".z-nav__toggle-sub",
		animationSpeed:500	
	});

	$('.z-nav__toggle').on('mousedown touchstart', function (){
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
	});

	//usage smoothscroll
	//set the link
	$('.top-scroll').topLink({
		min: 200,
		fadeSpeed: 500
	});
	
	//smoothscroll
	$('.top-scroll').click(function(e) {
		e.preventDefault();
		$.scrollTo(0,700);
	});

});

//Function section

//Start function
function sequence(parrent) {
			var sequence =  $(parrent +' .sequence__item');
				
			sequence.click(function (e) {
				e.preventDefault();

				sequence.removeClass('sequence__item--active');
				$(this).addClass('sequence__item--active');

				var sepatators = $('.sequence--clickable .sequence__separator');
				var defaultSeparator = '<span class="sequence__devider"></span><span class="sequence__devider"></span><span class="sequence__devider"></span><span class="sequence__devider"></span><span class="sequence__devider"></span><span class="sequence__devider"></span><span class="sequence__devider"></span><span class="sequence__devider"></span>';
				var prevSeparator= '<span class="sequence__devider sequence__color--one"></span><span class="sequence__devider sequence__color--one1"></span><span class="sequence__devider sequence__color--one2"></span><span class="sequence__devider sequence__color--one3"></span><span class="sequence__devider sequence__color--two3"></span><span class="sequence__devider sequence__color--two2"></span><span class="sequence__devider sequence__color--two1"></span><span class="sequence__devider sequence__color--two"></span>';
				var nextSeparator = '<span class="sequence__devider sequence__color--two"></span><span class="sequence__devider sequence__color--two1"></span><span class="sequence__devider sequence__color--two2"></span><span class="sequence__devider sequence__color--two3"></span><span class="sequence__devider sequence__color--one3"></span><span class="sequence__devider sequence__color--one2"></span><span class="sequence__devider sequence__color--one1"></span><span class="sequence__devider sequence__color--one"></span>';

				sepatators.html(defaultSeparator);
				$(this).prev('.sequence__separator').html(prevSeparator);
				$(this).next('.sequence__separator').html(nextSeparator);
			});
}
//end function	

//Start function
function sequenceExp() {
				var sequence =  $('.sequence__item');
				
				sequence.click(function (e) {
					e.preventDefault();

					sequence.removeClass('sequence__item--active');
					$(this).addClass('sequence__item--active');

					var sepatators = $('.sequence--clickable .sequence__separator');
					var connector = $(this).attr('data-connect');
					var textArea = $('.sequence__text');

					textArea.hide(0);
					$('.'+ connector).show();

					var defaultSeparator = '<span class="sequence__devider"></span><span class="sequence__devider"></span><span class="sequence__devider"></span><span class="sequence__devider"></span><span class="sequence__devider"></span><span class="sequence__devider"></span><span class="sequence__devider"></span><span class="sequence__devider"></span>';
					var prevSeparator= '<span class="sequence__devider sequence__color--one"></span><span class="sequence__devider sequence__color--one1"></span><span class="sequence__devider sequence__color--one2"></span><span class="sequence__devider sequence__color--one3"></span><span class="sequence__devider sequence__color--two3"></span><span class="sequence__devider sequence__color--two2"></span><span class="sequence__devider sequence__color--two1"></span><span class="sequence__devider sequence__color--two"></span>';
					var nextSeparator = '<span class="sequence__devider sequence__color--two"></span><span class="sequence__devider sequence__color--two1"></span><span class="sequence__devider sequence__color--two2"></span><span class="sequence__devider sequence__color--two3"></span><span class="sequence__devider sequence__color--one3"></span><span class="sequence__devider sequence__color--one2"></span><span class="sequence__devider sequence__color--one1"></span><span class="sequence__devider sequence__color--one"></span>';

					sepatators.html(defaultSeparator);
					$(this).prev('.sequence__separator').html(prevSeparator);
					$(this).next('.sequence__separator').html(nextSeparator);
				});
}
//end function

//Start function
function qNumber() {

	// This button will increment the value
	$('.qtyplus').click(function(e){
		// Stop acting like a button
		e.preventDefault();
		// Get the field name
		var fieldName = $(this).attr('data-field');
		// Get its current value
		var currentVal = parseInt($('input[name='+fieldName+']').val());
		// If is not undefined
		if (!isNaN(currentVal)) {
			// Increment
			$('input[name='+fieldName+']').val(currentVal + 1);
		} else {
			// Otherwise put a 0 there
			$('input[name='+fieldName+']').val(0);
		}
	});
	// This button will decrement the value till 0
	$(".qtyminus").click(function(e) {
		// Stop acting like a button
		e.preventDefault();
		// Get the field name
		var fieldName = $(this).attr('data-field');
		// Get its current value
		var currentVal = parseInt($('input[name='+fieldName+']').val());
		// If it isn't undefined or its greater than 0
		if (!isNaN(currentVal) && currentVal > 0) {
			// Decrement one
			$('input[name='+fieldName+']').val(currentVal - 1);
		} else {
			// Otherwise put a 0 there
			$('input[name='+fieldName+']').val(0);
		}
	});
}
//end function

//Start function
function scrollControls() {
	//Scroll down navigation function
	//scroll down
	$('.tags__item--comment').click(function (ev) {
		ev.preventDefault();
		$('html, body').stop().animate({'scrollTop': $('#comment-start').offset().top-100}, 900, 'swing');
	});

	$('.tags__item--user').click(function (ev) {
		ev.preventDefault();
		$('html, body').stop().animate({'scrollTop': $('#user-post-start').offset().top-100}, 900, 'swing');
	});
}
//end function

//Start function
function smoothLink() {

					// Smooth scroll
		            $('.scroll-link').bind('click.smoothscroll',function (e) {
		                e.preventDefault();

		                var target = this.hash,
		                $target = $(target);

		                if($target.offset() == undefined) return;

		                $('html, body').stop().animate({
		                    'scrollTop': $target.offset().top-110
		                }, 900, 'swing', function () {
		                    if($('body').hasClass('auto-close-menu') && $('.menu-open').length > 0){
		                        $('#menuToggle, #menuToggleLeft').click();
		                    }
		                    
		                });
		            });

		            $('.scroll-link').click(function (e) {
		            	$('#review').trigger('click');
		            });
}
//end function

//Start function
function smoothScrollInit() {

	 				// Smooth scroll
		            $('a[href^="#"]').bind('click.smoothscroll',function (e) {
		                e.preventDefault();

		                var target = this.hash,
		                $target = $(target);

		                if($target.offset() == undefined) return;

		                $('html, body').stop().animate({
		                    'scrollTop': $target.offset().top-110
		                }, 900, 'swing', function () {
		                    if($('body').hasClass('auto-close-menu') && $('.menu-open').length > 0){
		                        $('#menuToggle, #menuToggleLeft').click();
		                    }
		                    
		                });
		            });
}
//end function

//Start function
function preloader() {

}
//end function