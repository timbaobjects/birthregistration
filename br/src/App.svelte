<script>
	import L from 'leaflet';
	import { onMount } from 'svelte';
	import Performance from './Performance.svelte';
	import AgeSelector from './AgeSelector.svelte';
	import Trend from './Trend.svelte';
	import Centers from './Centers.svelte';
	import Toolbar from './Toolbar.svelte';
	import DateSelector from './DateSelector.svelte';
	import { ScaleOut } from 'svelte-loading-spinners';

	let map;
	let name = 'Nigeria',
		age = 0,
		performance = 0,
		boys = 0,
		girls = 0,
		total = 0,
		contributing = 0,
		fresh = 0,
		trend = [],
		national_data = {
			name: 'Nigeria',
			u1_perf: 0,
			u5_perf: 0,
			u1_boys: 0,
			u5_boys: 0,
			u1_girls: 0,
			u5_girls: 0,
			total_centres: 0,
			reporting_centres: 0,
			new_centres: 0,
			previous: []
		},
		lgasLayers = [],
		statesLayers = [],
		bordersLayer, promise;
    const UNDER_1 = 0,
	      UNDER_5 = 1;

	let displayNational = (selector = 0) => {
		let performance_arr = [
			national_data.u1_perf, national_data.u5_perf];
		let boys_arr = [
			national_data.u1_boys, national_data.u5_boys];
		let girls_arr = [
			national_data.u1_girls, national_data.u5_girls];
        selector = Math.min(selector, performance_arr.length - 1);

		name = national_data.name;
		performance = performance_arr[selector];
		boys = boys_arr[selector];
		girls = girls_arr[selector];
		total = national_data.total_centres;
		contributing = national_data.reporting_centres;
		fresh = national_data.new_centres;
		trend = national_data.previous;
	};

	let switchLayers = (selector = 0, showLGAs = false) => {
		if (map !== undefined) {
            selector = Math.max(Math.min(selector, statesLayers.length - 1), 0);

			if (showLGAs || map.getZoom() >= 8) {
				statesLayers.concat([bordersLayer]).concat(lgasLayers).forEach((layer) => {
					map.removeLayer(layer);
				});
				[lgasLayers[selector], bordersLayer].forEach((layer) => {
					map.addLayer(layer);
				});
			} else {
				statesLayers.concat(lgasLayers).concat([bordersLayer]).forEach((layer) => {
					map.removeLayer(layer);
				});
				map.addLayer(statesLayers[selector]);
			}
		}
	}

	let eachState = (selector = 0) => {
		return function (feat, layer) {
			layer.on('mouseover', (e) => {
				var performance_arr = [e.target.feature.geometry.properties.u1_perf,
					e.target.feature.geometry.properties.u5_perf];
				var boys_arr = [e.target.feature.geometry.properties.u1_boys,
					e.target.feature.geometry.properties.u5_boys];
				var girls_arr = [e.target.feature.geometry.properties.u1_girls,
					e.target.feature.geometry.properties.u5_girls];
                selector = Math.min(selector, performance_arr.length - 1);

				name = e.target.feature.geometry.properties.name;
				performance = performance_arr[selector];
				boys = boys_arr[selector];
				girls = girls_arr[selector];
				total = e.target.feature.geometry.properties.total_centres;
				contributing = e.target.feature.geometry.properties.reporting_centres;
				fresh = e.target.feature.geometry.properties.new_centres;
				trend = e.target.feature.geometry.properties.previous;

				layer.setStyle({fillOpacity: .8});
			});
			layer.on('mouseout', (e) => {
				displayNational(age);
				layer.setStyle({fillOpacity: .5});
			});
			layer.on('click', (e) => {
				map.flyToBounds(e.target.getBounds(), {duration: 0.5, easeLinearity: 1});
				setTimeout(() => switchLayers(age, true), 600);
			});
		};
	};

	let eachLGA = (selector = 0) => {
		return function (feat, layer) {
			layer.on('mouseover', (e) => {
				var performance_arr = [e.target.feature.geometry.properties.u1_perf,
					e.target.feature.geometry.properties.u5_perf];
				var boys_arr = [e.target.feature.geometry.properties.u1_boys,
					e.target.feature.geometry.properties.u5_boys];
				var girls_arr = [e.target.feature.geometry.properties.u1_girls,
					e.target.feature.geometry.properties.u5_girls];
                selector = Math.min(selector, performance_arr.length - 1);

				name = e.target.feature.geometry.properties.name;
				performance = performance_arr[selector];
				boys = boys_arr[selector];
				girls = girls_arr[selector];
				total = e.target.feature.geometry.properties.total_centres;
				contributing = e.target.feature.geometry.properties.reporting_centres;
				fresh = e.target.feature.geometry.properties.new_centres;
				trend = e.target.feature.geometry.properties.previous;

				layer.setStyle({fillOpacity: .8});
			});
			layer.on('mouseout', (e) => {
				displayNational(age);
				layer.setStyle({fillOpacity: .5});
			});
			layer.on('click', (e) => {
				map.setView([11, 9], 7);
				switchLayers(age, false);
			});
		};
	};

	let statesStyle = (selector = 0) => {
		return function (feature) {
			var performance_arr = [
				feature.geometry.properties.u1_perf,
				feature.geometry.properties.u5_perf];
            selector = Math.min(selector, performance_arr.length - 1);

			let perf = performance_arr[selector];
			let fillColor;

			if (perf >= 70) fillColor = '#73d216';
			else if (perf >= 60) fillColor = '#a5db2d';
			else if (perf >= 50) fillColor = '#d2e23f';
			else if (perf >= 30) fillColor = '#fdc344';
			else fillColor = '#ef2929';

			return {weight: 4, color: '#fff', fillColor: fillColor, fillOpacity: .5};
		};
	};

	let lgasStyle = (selector = 0) => {
		return function (feature) {
			var performance_arr = [
				feature.geometry.properties.u1_perf,
				feature.geometry.properties.u5_perf];
            selector = Math.min(selector, performance_arr.length - 1);

			let perf = performance_arr[selector];
			let fillColor;

			if (perf >= 70) fillColor = '#73d216';
			else if (perf >= 60) fillColor = '#a5db2d';
			else if (perf >= 50) fillColor = '#d2e23f';
			else if (perf >= 30) fillColor = '#fdc344';
			else fillColor = '#ef2929';

			return {weight: 1, color: '#fff', opacity: .4, fillColor: fillColor, fillOpacity: .5};
		};
	};

	let borderStyle = (feat) => {
		return {weight: 5, color: '#fff', opacity: 1};
	};

	async function loadLayers(year = '', month = '') {
		function buildUrl(base_url) {
			let url = new URLSearchParams(base_url);
			if (year) {
				url.set('year', year);
			}
			if (month) {
				url.set('month', month);
			}

			return decodeURIComponent(url.toString());
		}

		let nation = await fetch(buildUrl('/br/api/v1/?level=country'));
		let states = await fetch(buildUrl('/br/api/v1/?level=state'));
		let lgas = await fetch(buildUrl('/br/api/v1/?level=lga'));

		if (nation.ok) {
			let json = await nation.json();
			national_data.name = json.features[0].properties.name;
			national_data.u1_perf = json.features[0].properties.u1_perf;
			national_data.u5_perf = json.features[0].properties.u5_perf;
			national_data.u1_boys = json.features[0].properties.u1_boys;
			national_data.u1_girls = json.features[0].properties.u1_girls;
			national_data.u5_boys = json.features[0].properties.u5_boys;
			national_data.u5_girls = json.features[0].properties.u5_girls;
			national_data.total_centres = json.features[0].properties.total_centres;
			national_data.reporting_centres = json.features[0].properties.reporting_centres;
			national_data.new_centres = json.features[0].properties.new_centres;
			national_data.previous = json.features[0].properties.previous;
		}

		if (lgas.ok) {
			let json = await lgas.json();
			lgasLayers = [];
			lgasLayers.push(L.geoJSON(json, {
				onEachFeature: eachLGA(UNDER_1),
				style: lgasStyle(UNDER_1)
			}));
			lgasLayers.push(L.geoJSON(json, {
				onEachFeature: eachLGA(UNDER_5),
				style: lgasStyle(UNDER_5)
			}));
		}

		if (bordersLayer === undefined) {
			let borders = await fetch('/static/js/br-state-boundaries.json');

			if (borders.ok) {
				let json = await borders.json();
				bordersLayer = L.geoJSON(json, {
					style: borderStyle,
				});
			}
		}

		if (states.ok) {
			let json = await states.json();
			statesLayers = [];
			statesLayers.push(L.geoJSON(json, {
				onEachFeature: eachState(UNDER_1),
				style: statesStyle(UNDER_1)
			}));
			statesLayers.push(L.geoJSON(json, {
				onEachFeature: eachState(UNDER_5),
				style: statesStyle(UNDER_5)
			}));
		}

		switchLayers(age, false);
		displayNational(age);
	};

	onMount(async () => {
		map = L.map('mapid');
		L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            maxZoom: 12,
            id: 'mapbox/light-v10',
            tileSize: 512,
            zoomOffset: -1,
            accessToken: 'pk.eyJ1IjoidGltYmFvIiwiYSI6IkdYa3BVSHMifQ.BOh_F9hD3Moby5nWoa-rVA'
		}).addTo(map);
		
		map.setView([11, 9], 7);
		map.on('zoomend', (e) => {
			let z = map.getZoom();
			if (z >= 8) {
				switchLayers(age, true);
			} else {
				switchLayers(age, false);
			}
		});

		promise = loadLayers();
	});

	async function handleDate(event) {
		statesLayers.concat([bordersLayer]).concat(lgasLayers).forEach((layer) => {
			map.removeLayer(layer);
		});
		promise = loadLayers(event.detail.year, event.detail.month)
	}

	$: switchLayers(age, false);
	$: displayNational(age);
</script>

<style>
	#mapid {
		height: 100vh;
	}
	.spinner-item {
	  height: 100vh;
	  width: 100%;
	  display: flex;
	  justify-content: center;
	  align-items: center;
	  position: absolute;
	  z-index: 1001;
	  background-color: rgba(255, 255, 255, 1);
	}
	.spinner-title {
	  position: absolute;
	  bottom: 20%;
	  color: #FF3E00;
	}
</style>

{#await promise}
<div class="spinner-item">
	<ScaleOut size="100" color="#FF3E00" unit="px"></ScaleOut>
	<div class="spinner-title">Loading...</div>
</div>
{/await}
<div id="mapid"></div>
<AgeSelector bind:age={age} />
<Performance {name} {performance} {boys} {girls} />
<Trend {name} {trend} />
<Centers {total} {contributing} {fresh} />
<Toolbar />
<DateSelector on:message={handleDate} />