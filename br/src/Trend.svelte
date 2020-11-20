<script>
	import Chart from 'svelte-frappe-charts';
	export let trend;
	export let name = "";
	let data;

	$: data = {
		"labels": trend.map((entry) => entry['year']),
		"datasets": [
			{
				"name": "U1 Performance",
				"values": trend.map((item) => Math.round(item['u1_perf']))
			},
			{
				"name": "U5 Performance",
				"values": trend.map((item) => Math.round(item['u5_perf']))
			}
		],
	};
	let tooltipOptions = {
			formatTooltipX: d => d,
			formatTooltipY: d => d + '%',
		},
		valuesOverPoints = 1;
</script>

<style>
	div.trend-overlay {
		position: absolute;
		z-index: 999;
		top: 5em;
		right: 10px;
		backdrop-filter: saturate(100%) blur(5px);
		background-color: rgba(255, 255, 255, .90);
	}
</style>

<div class="card trend-overlay shadow w-25">
	<h5 class="card-header">{name.toUpperCase()} Trend Chart</h5>
	<div class="card-body">
		<div class="text-center">
			{#if trend.length}
			<Chart {data} type='line' {tooltipOptions} {valuesOverPoints} />
			{:else}
			<small>No Data Available</small>
			{/if}
		</div>
	</div>
</div>