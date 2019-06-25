
(function (undefined){

	// https://stackoverflow.com/a/49041392/551625

	const getCellValue = (tr, idx) => tr.children[idx].textContent;

	const comparer = (idx, asc) => (a, b) => ((v1, v2) =>
		v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.length - v2.length
		)(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));




	window.table = {
		'sortTable': function sortTable(tbody, colIndex){
			// https://stackoverflow.com/a/49041392/551625
			Array.from(tbody.querySelectorAll(':scope > tr'))
				.sort(comparer(colIndex, false))
				.forEach(tr => tbody.appendChild(tr) );
		},
	};

	(function keepTableSorted(){

		var sortingObservers = new WeakMap()

		var registerKeepTableSorted = function (tbody, sortCol){

			var currentObserver = sortingObservers[tbody];
			(currentObserver || false) && currentObserver.disconnect();

			var insertViewport = function (mutations){
				// Doesn't matter what changed. Just resort the table
				window.table.sortTable(tbody, sortCol);
				lineInsertObserver.takeRecords(); // Do not take into account the element that had just been appended
			};

			window.table.sortTable(tbody, sortCol);

			var lineInsertObserver = new MutationObserver(insertViewport);
			lineInsertObserver.observe(tbody,{
				childList: true,
				subtree: true,
			});

			sortingObservers[tbody] = lineInsertObserver;

		};

		window.table.keepTableSorted = registerKeepTableSorted;

		var newToSortObserver = function (mutations){
			mutations.forEach(function(mutation){
				switch(mutation.type) {
					case 'childList':
						Array.from(mutation.addedNodes || []).forEach(function (elem){
						if(!elem.hasAttribute){
							return;
						}
						var attrElem = elem.hasAttribute('data-keep-table-sorted') ? elem : elem.querySelector('[data-keep-table-sorted]')
							if(attrElem){
								registerKeepTableSorted(attrElem, attrElem.getAttribute('data-keep-table-sorted'))
							}
						})

						break;
					case 'attributes':
						console.warn("WIP to handle this")
				}
			});
		};

		var newToSortObserver = new MutationObserver(newToSortObserver);
			newToSortObserver.observe(document.body,{
				childList: true,
				subtree: true,
				attributes: true,
				attributeFilter: ['data-keep-table-sorted'],
			})

		Array.from(document.querySelectorAll('tbody[data-keep-table-sorted]')).forEach((tbody) => {
			registerKeepTableSorted(tbody, tbody.getAttribute('data-keep-table-sorted'))
		})

		document.addEventListener('DOMContentLoaded', function(e){
			Array.from(document.querySelectorAll('tbody[data-keep-table-sorted]')).forEach((tbody) => {
				registerKeepTableSorted(tbody, tbody.getAttribute('data-keep-table-sorted'))
			})
		})

	})();
})();

