// <script> Must be placed just BEFORE the table so it is ready while the table is loading

(function (undefined){


	var socket = io() //.connect('http://' + document.domain + ':' + location.port + '/');
	socket.on('my response', function(msg) {
		console.log("response got", msg);
	});

	const SPINNER_SELECTOR = '[data-spinner="translationRequest"]';
	var disableCancel = null;

	socket.on('translation update', function(msg) {
		console.log("translation update", msg);

		var translationResultsContainer = document.querySelector('[data-translation-results]');

		var tableLine = translationResultsContainer.querySelector('[data-line-id="' + msg.uid + '"]')

		if(!tableLine){
			document.querySelector(SPINNER_SELECTOR).hidden = true;
			var templateLine = document.querySelector('[data-translation-line]')
			var newLine = document.importNode(templateLine.content.firstElementChild, true);
			tableLine = newLine; // easier to debug
		}

		tableLine.setAttribute('data-line-id', msg.uid)
		tableLine.querySelector('[data-uid]').textContent = msg.uid
		tableLine.querySelector('[data-source_language]').textContent = msg.sourceLanguage
		tableLine.querySelector('[data-target_language]').textContent = msg.targetLanguage
		tableLine.querySelector('[data-status]').textContent = msg.status
		tableLine.querySelector('[data-text]').textContent = msg.text
		tableLine.querySelector('[data-translation]').textContent = msg.translation

		translationResultsContainer.appendChild(tableLine);
	});

	// Can be vastly improved but this is good enough for this page
	var disableOnSubmits = Array.from(document.querySelectorAll('form[data-translation-request] [type=submit]'));

	document.querySelector('form[data-translation-request]').addEventListener('submit', function(event) {
		document.querySelector(SPINNER_SELECTOR).hidden = false;

		disableOnSubmits.forEach(function (elem){
			elem.disabled = true;
		})
		clearInterval(disableCancel);
		disableCancel = setTimeout(function (){
			disableOnSubmits.forEach(function (elem){
				elem.disabled = false;
			})
		})

		socket.emit('translate this', {
			text: document.getElementById('source_text').value,
			sourceLanguage: 'en',
			targetLanguage: 'es',
		});
		event.preventDefault()
		return false;
	});

})();