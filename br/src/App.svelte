<script>
	import L from 'leaflet';
	import { onMount } from 'svelte';
	import Performance from './Performance.svelte';
	import Trend from './Trend.svelte';
	import Centers from './Centers.svelte';
	import { ScaleOut } from 'svelte-loading-spinners';

	let map;
	let name = 'Nigeria',
		performance = 0,
		boys = 0,
		girls = 0,
		total = 0,
		contributing = 0,
		fresh = 0,
		trend = [],
		lgasLayer, statesLayer, bordersLayer, promise;

	let switchLayers = (enableLGAS) => {
		if (enableLGAS) {
			map.addLayer(lgasLayer);
			map.addLayer(bordersLayer);
		} else {
			map.removeLayer(lgasLayer);
			map.removeLayer(bordersLayer);
		}
	}

	let eachState = (feat, layer) => {
		layer.on('mouseover', (e) => {
			name = e.target.feature.geometry.properties.name;
			performance = e.target.feature.geometry.properties.u1_perf;
			boys = e.target.feature.geometry.properties.boys;
			girls = e.target.feature.geometry.properties.girls;
			total = e.target.feature.geometry.properties.total_centres;
			contributing = e.target.feature.geometry.properties.reporting_centres;
			fresh = e.target.feature.geometry.properties.new_centres;
			trend = e.target.feature.geometry.properties.previous;
			layer.setStyle({fillOpacity: .8});
		});
		layer.on('mouseout', (e) => {
			layer.setStyle({fillOpacity: .5});
		});
		layer.on('click', (e) => {
			map.flyToBounds(e.target.getBounds(), {duration: 0.5, easeLinearity: 1});
			setTimeout(() => switchLayers(true), 600);
		});
	};

	let eachLGA = (feat, layer) => {
		layer.on('mouseover', (e) => {
			name = e.target.feature.geometry.properties.name;
			performance = e.target.feature.geometry.properties.u1_perf;
			boys = e.target.feature.geometry.properties.boys;
			girls = e.target.feature.geometry.properties.girls;
			total = e.target.feature.geometry.properties.total_centres;
			contributing = e.target.feature.geometry.properties.reporting_centres;
			fresh = e.target.feature.geometry.properties.new_centres;
			trend = e.target.feature.geometry.properties.previous;
			layer.setStyle({fillOpacity: .8});
		});
		layer.on('mouseout', (e) => {
			layer.setStyle({fillOpacity: .5});
		});
		layer.on('click', (e) => {
			map.setView([11, 9], 7);
			switchLayers(false);
		});
	};

	let statesStyle = (feat) => {
		let u1_perf = feat.geometry.properties.u1_perf;
		let fillColor;

		if (u1_perf >= 70) fillColor = '#73d216';
		else if (u1_perf >= 60) fillColor = '#a5db2d';
		else if (u1_perf >= 50) fillColor = '#d2e23f';
		else if (u1_perf >= 30) fillColor = '#fdc344';
		else fillColor = '#ef2929';

		return {weight: 4, color: '#fff', fillColor: fillColor, fillOpacity: .5};
	};

	let lgasStyle = (feat) => {
		let u1_perf = feat.geometry.properties.u1_perf;
		let fillColor;

		if (u1_perf >= 70) fillColor = '#73d216';
		else if (u1_perf >= 60) fillColor = '#a5db2d';
		else if (u1_perf >= 50) fillColor = '#d2e23f';
		else if (u1_perf >= 30) fillColor = '#fdc344';
		else fillColor = '#ef2929';

		return {weight: 1, color: '#fff', opacity: .4, fillColor: fillColor, fillOpacity: .5};
	};

	let borderStyle = (feat) => {
		return {weight: 5, color: '#fff', opacity: 1};
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
				switchLayers(true);
			} else {
				switchLayers(false);
			}
		});

		async function loadLayers() {
			let states = await fetch('/br/api/v1/');
			let lgas = await fetch('/br/api/v1/?level=state');
			let borders = await fetch('/static/js/br-state-boundaries.json');

			if (lgas.ok) {
				let json = await lgas.json();
				lgasLayer = L.geoJSON(json, {
					onEachFeature: eachLGA,
					style: lgasStyle
				});
			}

			if (borders.ok) {
				let json = await borders.json();
				bordersLayer = L.geoJSON(json, {
					style: borderStyle,
				});
			}

			if (states.ok) {
				let json = await states.json();
				statesLayer = L.geoJSON(json, {
					onEachFeature: eachState,
					style: statesStyle
				});
				map.addLayer(statesLayer);
			}
		};

		promise = loadLayers();
	})
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
<Performance {name} {performance} {boys} {girls} />
<Trend {name} {trend} />
<Centers {total} {contributing} {fresh} />
