function debounce(func, wait, immediate) {
	var timeout;
	return function() {
		var context = this, args = arguments
		clearTimeout(timeout);
		timeout = setTimeout(function() {
			timeout = null;
			if (!immediate) func.apply(context, args);
		}, wait);
		if (immediate && !timeout) func.apply(context, args);
	};
}

$(function() {
	var country_selector = document.getElementById('country-selector');
	var country = undefined;
	if (country_selector) {
		country = country_selector.options[country_selector.selectedIndex].text;
		if (country == "None") {
			print_country("country-selector");
		} else {
			print_country("country-selector");
			$('#country-selector').val(country);
			
		}
	}
	$('#country-selector').change(function() {
		print_state('state-province-selector', this.selectedIndex);
	});

	var url = window.location.href.split('/');
	var current_page = url[url.length - 1];
	// get next page path if we're simply pulling an ID
	if (isNaN(current_page) == false) {
		current_page = url[url.length -2];
	}

	function testLocalUrl() {
		$.ajax({
			url: '/test_local_url.json',
			data: JSON.stringify({local_url: $('.local_url').val()}),
			success: function(data) {
				if (data == "Taken") {
					$('.test-local-url').html([
						"<i>startupdex.com/startup/"+$('.local_url').val()+"</i>",
					" is taken by another startup"]);
					$('.test-local-url').css( "color", "darkred" );
				} else {
					$('.test-local-url').html([
						"<i>startupdex.com/startup/"+$('.local_url').val()+"</i>",
						" is available!"]);
					$('.test-local-url').css( "color", "green" );
				}
			}
		});
	}
	$('.local_url').keyup(debounce(function() {
			testLocalUrl()
		}, 400)
	);

	function readURL(input) {
		if (input.files && input.files[0]) {
			var reader = new FileReader();
			reader.onload = function (e) {
				$(".photo-preview").attr('src', e.target.result);
			}

			reader.readAsDataURL(input.files[0]);
		}
	}
	$("#logo").change(function () {
		readURL(this);
	});
	$("#photo").change(function () {
		readURL(this);
	});


	$('#startupdex_search').click(
		startupdex_search()
	);
	function startupdex_search() {
		$.ajax({
			//url: '/search'
		})
	}

	$('#cancel-changes').click(function() {
		location.reload();
	});

	$('#enable-changes').click(function() {
		$('input').each(function() {
			$(this).prop('disabled', false);
		});
		$('select').each(function() {
			$(this).prop('disabled', false);
		});
		$('#save-changes').prop('disabled', false);
		$('#cancel-changes').prop('disabled', false);
	});

	$('#cancel-changes').click(function () {
		$('input').each(function() {
			$(this).prop('disabled', true);
		});
		$('select').each(function() {
			$(this).prop('disabled', false);
		});
		$('#save-changes').prop('disabled', true);
		$('#cancel-changes').prop('disabled', true);
	});

	$('#save-changes').click(function() { 
		//var r = confirm("Are you sure you want to save changes?");
		var r = true;
		if (r == true) {
			if (current_page == "modify_startup") {
				modify_startup_save_changes(this);
			} else if (current_page == "modify_social") {
				modify_social_save_changes(this);
			} else if (current_page == "modify_profile") {
				modify_profile_save_changes(this);
			} else if (current_page == "modify_article") {
				modify_article_save_changes(this);
			}
		} else {
			alert("Action canceled");
		}
	});
	function modify_profile_save_changes(el) {
		var tr = $(el).parent().parent().parent();
		$.ajax({
			url: '/modify_profile_save_changes.json',
			data: JSON.stringify({id: $('#id').val(),
													 email: tr.find('.email').val(),
													 fullname: tr.find('.fullname').val(),
													 phone: tr.find('.phone').val(),
													 location: tr.find('.location').val(),
													 country: tr.find('.country').val(),
													 postal_code: tr.find('.postal_code').val(),
													 state_province: tr.find('.state_province').val(),
													 city: tr.find('.city').val(),
													 street_address: tr.find('.street_address').val(),
													 home_url: tr.find('.home_url').val(),
													 twitter_url: tr.find('.twitter_url').val(),
													 blog_url: tr.find('.blog_url').val(),
													 facebook_url: tr.find('.facebook_url').val(),
						})
		});
	}
	function modify_startup_save_changes(el) {
		var tr = $(el).parent().parent().parent();
		$.ajax({
			url: '/modify_startup_save_changes.json',
			data: JSON.stringify({userid: $('#userid').val(),
														startupid: $('#startupid').val(),
													  name: tr.find('.name').val(),
													  local_url: tr.find('.local_url').val(),
														tags: tr.find('.tags').val(),
														company_size: tr.find('.company_size').val(),
														short_info: tr.find('.short_info').val(),
														about: tr.find('.about').val(),
			})
		});
	}
	function modify_social_save_changes(el) {
		var tr = $(el).parent().parent().parent();
		$.ajax({
			url: '/modify_social_save_changes.json',
			data: JSON.stringify({userid: $('#userid').val(),
														startupid: $('#startupid').val(),
													  contact_email: tr.find('.contact_email').val(),
														contact_phone: tr.find('.contact_phone').val(),
														home_url: tr.find('.home_url').val(),
														blog_url: tr.find('.blog_url').val(),
														facebook_url: tr.find('.facebook_url').val(),
														twitter_url: tr.find('.twitter_url').val(),
														country: tr.find('.country').val(),
														postal_code: tr.find('.postal_code').val(),
														state_province: tr.find('.state_province').val(),
														city: tr.find('.city').val(),
														street_address: tr.find('.street_address').val(),
			})
		});
	}
	function modify_locations_save_changes(el) {
		var tr = $(el).parent().parent().parent();
		$.ajax({
			url: '/modify_locations_save_changes.json',
			data: JSON.stringify({userid: $('#userid').val(),
														startupid: $('#startupid').val(),
													  contact_email: tr.find('.contact_email').val(),
														contact_phone: tr.find('.contact_phone').val(),
														country: tr.find('.country').val(),
														state_province: tr.find('.state_province').val(),
														city: tr.find('.city').val(),
														street_address: tr.find('.street_address').val(),
														facebook_url: tr.find('.facebook_url').val(),
														home_url: tr.find('.home_url').val(),
														blog_url: tr.find('.blog_url').val(),
														twitter_url: tr.find('.twitter_url').val(),
			})
		});
	}
	function modify_article_save_changes(el) {
		var tr = $(el).parent().parent().parent();
		$.ajax({
			url: '/modify_article_save_changes.json',
			data: JSON.stringify({userid: $('#userid').val(),
														about: $('#startupid').val(),
													  title	: tr.find('.title').val(),
													  tags	: tr.find('.tags').val(),
													  lead_text	: tr.find('.lead_text').val(),
													  story	: tr.find('.story').val(),
			})
		});
	}

	function postalCodeAutorefresh(el) {
		if ($(el).val().length >= 4) {
			var postal_code = $(el).val();
			var country = $(el).parent().parent().parent().find(".country").val();
			var apiUrl = "https://maps.googleapis.com/maps/api/geocode/json?sensor=false&address=" + postal_code + ", " + country
			$.ajax({
				url: apiUrl,
				xhrFields: { withCredentials: false },
				success: function(data) {
					var geocode = data;
					var country = undefined;
					var state_province = undefined;
					var city = undefined;
					$.each(geocode.results[0].address_components, function(i, component) {
						if (component.types[0] == "country") { country = component.long_name }
						if (component.types[0] == "administrative_area_level_3") { city = component.long_name }
						if (component.types[0] == "locality") { city = component.long_name }
						if (component.types[0] == "administrative_area_level_1") { state_province = component.long_name }
					});
					if (country) {
						$('#country-selector').val(country);
						print_state('state-province-selector', document.getElementById('country-selector').selectedIndex);
					}
					$('#state-province-selector').val(state_province);
					$('.city').val(city);
				}
			});
		}
	}
	$('#postal-code-autorefresh').change(debounce(function() {
			postalCodeAutorefresh(this)
		}, 800)
	);
	$('#postal-code-autorefresh').keyup(debounce(function() {
			postalCodeAutorefresh(this)
		}, 800)
	);


	$(window).bind("load", function() {
		$.ajaxSetup({
			type: 'POST',
			dataType: 'json',
			xhrFields: { withCredentials: true },
			async: true,
			contentType: 'application/json; charset=utf-8',
			success: function(data) {
				if (data == "Fail, reload") {
					location.reload();
				} else {
					location.reload();
				}
			},
			error: function() {
				alert("An error occurred.");
			}
		});
		

		var page_group = current_page.split("_")[0];
		if (page_group == "modify") {
			$(':input[type=text]').on("input", function(event){
				$(event.target).css( "background-color", "#FFFFD5" );
				$('#save-changes').prop('disabled', false);
				$('#cancel-changes').prop('disabled', false);
			});
			$('textarea').on("input", function(event){
				$(event.target).css( "background-color", "#FFFFD5" );
				$('#save-changes').prop('disabled', false);
				$('#cancel-changes').prop('disabled', false);
			});
			$('select').on("change", function(event){
				$(event.target).css( "background-color", "#FFFFD5" );
				$('#save-changes').prop('disabled', false);
				$('#cancel-changes').prop('disabled', false);
			});
		}
	});
	


});
